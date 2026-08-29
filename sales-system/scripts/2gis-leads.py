#!/usr/bin/env python3
"""
Полная выгрузка лидов из 2ГИС: компании БЕЗ сайта, с телефоном.

Бесплатный ключ отдаёт максимум 50 карточек на запрос (page 1-5 x page_size 10).
Обход: адаптивная сетка по координатам. Для каждой точки спрашиваем radius-поиск,
смотрим result.total; если больше лимита — делим квадрат на 4 и идём вглубь.
Так выгружаются все 3000+ карточек рубрики, а не первые 50.

Ключ: https://dev.2gis.ru/order/

    export DGIS_KEY="твой_ключ"
    python3 2gis-leads.py "автосервис" "Санкт-Петербург" > ~/leads-avto.csv

Несколько подрубрик за прогон:
    python3 2gis-leads.py "автосервис;кузовной ремонт;шиномонтаж" "Санкт-Петербург" > leads.csv

Все компании, а не только без сайта:   ALL=1 python3 2gis-leads.py ...
Сырой ответ API:                       DEBUG=1 python3 2gis-leads.py ...
"""
import csv, json, math, os, sys, time, urllib.parse, urllib.request

KEY = os.environ.get("DGIS_KEY", "f71fd53b-5faa-4993-8df6-738738f0402d")
DEBUG = os.environ.get("DEBUG") == "1"
ALL = os.environ.get("ALL") == "1"
BASE = "https://catalog.api.2gis.com"
PAGE_SIZE = int(os.environ.get("PAGE_SIZE", "10"))
MAX_PAGES = int(os.environ.get("MAX_PAGES", "5"))
HARD_CAP = PAGE_SIZE * MAX_PAGES          # 50 — потолок одного запроса
START_RADIUS = int(os.environ.get("START_RADIUS", "8000"))
MIN_RADIUS = int(os.environ.get("MIN_RADIUS", "300"))
SLEEP = float(os.environ.get("SLEEP", "1.5"))   # 2ГИС блокирует ключ за частые запросы
MAX_REQUESTS = int(os.environ.get("MAX_REQUESTS", "400"))  # потолок на прогон

# Прямоугольники городов: (lon_min, lat_min, lon_max, lat_max) — с пригородами
CITY_BBOX = {
    "санкт-петербург": (29.55, 59.62, 30.80, 60.15),
    "москва": (37.30, 55.55, 37.90, 55.92),
}

stats = {"requests": 0, "cells": 0, "total": 0, "with_phone": 0, "with_site": 0}


class StopHarvest(Exception):
    """Ключ заблокирован или исчерпан бюджет запросов — прекращаем немедленно."""


def get(path, **params):
    """2ГИС отвечает HTTP 200 всегда — реальный код лежит в meta.code."""
    params["key"] = KEY
    url = f"{BASE}{path}?{urllib.parse.urlencode(params)}"
    for attempt in range(3):
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                raw = r.read().decode()
            break
        except urllib.error.HTTPError as e:
            raw = e.read().decode(errors="replace")
            break
        except Exception as e:
            if attempt == 2:
                raise
            time.sleep(1 + attempt)
    stats["requests"] += 1
    if stats["requests"] > MAX_REQUESTS:
        raise StopHarvest(f"достигнут потолок {MAX_REQUESTS} запросов за прогон")
    if DEBUG:
        print(f"# GET {params.get('q','')} {params.get('point','')} -> {raw[:400]}", file=sys.stderr)
    data = json.loads(raw)
    meta = data.get("meta", {})
    if meta.get("code", 200) != 200:
        msg = (meta.get("error") or {}).get("message", "")
        if meta.get("code") == 403 or "blocked" in msg.lower():
            raise StopHarvest(f"2ГИС заблокировал ключ: {msg}")
        raise RuntimeError(f"{meta.get('code')}: {msg}")
    return data


def region_id(city):
    items = get("/2.0/region/search", q=city).get("result", {}).get("items", [])
    if not items:
        sys.exit(f"Не нашёл регион «{city}»")
    return items[0]["id"], items[0]["name"]


def contacts(item):
    phones, sites, socials = [], [], []
    for group in item.get("contact_groups", []) or []:
        for c in group.get("contacts", []) or []:
            t = c.get("type")
            v = c.get("value") or c.get("text") or c.get("url") or ""
            if not v:
                continue
            if t == "phone":
                phones.append(v)
            elif t == "website":
                sites.append(v)
            elif t in ("vkontakte", "instagram", "telegram", "whatsapp", "facebook"):
                socials.append(v)
    return phones, sites, socials


FIELDS = "items.contact_groups,items.address,items.rubrics,items.reviews,items.point"


def fetch_cell(query, lon, lat, radius, seen):
    """Забирает до HARD_CAP карточек в круге. Возвращает result.total (сколько там всего)."""
    total = None
    for page in range(1, MAX_PAGES + 1):
        try:
            data = get("/3.0/items", q=query, point=f"{lon},{lat}", radius=radius,
                       page=page, page_size=PAGE_SIZE, fields=FIELDS)
        except StopHarvest:
            raise
        except RuntimeError as e:
            if "NothingFound" not in str(e) and "not found" not in str(e).lower():
                print(f"#   {query} @{lon:.3f},{lat:.3f} r{radius}: {e}", file=sys.stderr)
            return total or 0
        except Exception as e:
            print(f"#   сеть: {e}", file=sys.stderr)
            return total or 0

        res = data.get("result", {})
        if total is None:
            total = res.get("total", 0)
        items = res.get("items", [])
        if not items:
            break
        for it in items:
            key = it.get("id") or f"{it.get('name')}|{it.get('address_name')}"
            if key in seen:
                continue
            phones, sites, socials = contacts(it)
            stats["total"] += 1
            if phones:
                stats["with_phone"] += 1
            if sites:
                stats["with_site"] += 1
            seen[key] = (it, phones, sites, socials)
        time.sleep(SLEEP)
    return total or 0


def harvest(query, lon, lat, radius, seen, depth=0):
    """Рекурсивный обход: переполненный круг делится на 4 круга поменьше."""
    stats["cells"] += 1
    total = fetch_cell(query, lon, lat, radius, seen)
    if total > HARD_CAP and radius > MIN_RADIUS:
        # смещение центров дочерних кругов, в градусах
        half = radius / 2
        dlat = (half / 111_000) * 0.9
        dlon = (half / (111_000 * math.cos(math.radians(lat)))) * 0.9
        for dx, dy in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
            harvest(query, lon + dx * dlon, lat + dy * dlat, int(half * 1.3),
                    seen, depth + 1)


def city_grid(bbox, radius):
    """Точки покрытия прямоугольника кругами радиуса radius."""
    lon0, lat0, lon1, lat1 = bbox
    step_lat = (radius * 1.4 / 111_000)
    pts = []
    lat = lat0
    while lat <= lat1:
        step_lon = (radius * 1.4 / (111_000 * math.cos(math.radians(lat))))
        lon = lon0
        while lon <= lon1:
            pts.append((round(lon, 4), round(lat, 4)))
            lon += step_lon
        lat += step_lat
    return pts


def main():
    if not KEY:
        sys.exit("Нет ключа. https://dev.2gis.ru/order/ , затем export DGIS_KEY=...")
    if len(sys.argv) < 3:
        sys.exit('Использование: python3 2gis-leads.py "рубрика[;рубрика2]" "город"')

    queries = [q.strip() for q in sys.argv[1].split(";") if q.strip()]
    city = sys.argv[2]
    rid, rname = region_id(city)
    bbox = CITY_BBOX.get(city.strip().lower())
    if not bbox:
        sys.exit(f"Нет координат города «{city}». Добавь bbox в CITY_BBOX.")

    grid = city_grid(bbox, START_RADIUS)
    print(f"# {rname}: {len(queries)} рубрик x {len(grid)} точек, старт радиус {START_RADIUS} м",
          file=sys.stderr)

    seen = {}
    t0 = time.time()
    stopped = None
    try:
        for qi, q in enumerate(queries, 1):
            for i, (lon, lat) in enumerate(grid, 1):
                harvest(q, lon, lat, START_RADIUS, seen)
                if i % 5 == 0:
                    print(f"#   [{qi}/{len(queries)}] «{q}» точка {i}/{len(grid)} · "
                          f"уникальных {len(seen)} · запросов {stats['requests']}", file=sys.stderr)
            print(f"# «{q}» готово: уникальных {len(seen)}", file=sys.stderr)
    except StopHarvest as e:
        stopped = str(e)
        print(f"# ОСТАНОВ: {e}", file=sys.stderr)
    except KeyboardInterrupt:
        stopped = "прервано вручную"
        print("# прервано — записываю собранное", file=sys.stderr)

    w = csv.writer(sys.stdout)
    w.writerow(["Компания", "Телефон", "Доп. телефоны", "Соцсети", "Адрес", "Рубрика",
                "Отзывов", "Рейтинг", "Есть сайт", "Статус", "Следующий шаг"])
    rows = []
    for it, phones, sites, socials in seen.values():
        if not ALL and (sites or not phones):
            continue
        rev = it.get("reviews") or {}
        rows.append([
            it.get("name", ""), phones[0] if phones else "", "; ".join(phones[1:]),
            "; ".join(socials),
            it.get("address_name") or (it.get("address") or {}).get("name", ""),
            ", ".join(r.get("name", "") for r in (it.get("rubrics") or [])[:2]),
            rev.get("general_review_count", 0) or 0,
            rev.get("general_rating", "") or "",
            "да" if sites else "нет", "не связывались", "",
        ])
    rows.sort(key=lambda r: r[6], reverse=True)      # больше отзывов — выше в обзвоне
    for r in rows:
        w.writerow(r)

    if stopped:
        print(f"# выгрузка неполная, причина: {stopped}", file=sys.stderr)
    print(f"# итог за {int(time.time()-t0)} c · запросов {stats['requests']} · "
          f"ячеек {stats['cells']} · карточек {stats['total']} · "
          f"с телефоном {stats['with_phone']} · с сайтом {stats['with_site']} · "
          f"строк в CSV {len(rows)}", file=sys.stderr)
    if stats["total"] and not stats["with_phone"]:
        print("# ВНИМАНИЕ: ни одного телефона — ключу не отдают contact_groups. "
              "Запусти с DEBUG=1 и покажи вывод.", file=sys.stderr)


if __name__ == "__main__":
    main()
