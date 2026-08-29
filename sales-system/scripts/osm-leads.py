#!/usr/bin/env python3
"""
Выгрузка лидов из OpenStreetMap (Overpass API): компании с телефоном и БЕЗ сайта.

Без ключей, без лимитов, без блокировок. Пишет CSV построчно — прерывание
не уничтожает уже собранное.

    python3 osm-leads.py автосервис "Санкт-Петербург" > ~/leads-avto.csv
    python3 osm-leads.py мебель "Санкт-Петербург" > ~/leads-mebel.csv
    python3 osm-leads.py --list          # все пресеты

Произвольный OSM-фильтр:
    python3 osm-leads.py 'shop=car_repair;craft=car_repair' "Санкт-Петербург"
"""
import csv, json, sys, time, urllib.parse, urllib.request

ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]

PRESETS = {
    "автосервис":   ["shop=car_repair", "craft=car_repair", "shop=tyres"],
    "автомойка":    ["amenity=car_wash"],
    "мебель":       ["shop=furniture", "craft=carpenter", "shop=kitchen", "shop=interior_decoration"],
    "окна":         ["shop=window_blind", "craft=window_construction"],
    "стоматология": ["amenity=dentist", "healthcare=dentist"],
    "медцентр":     ["amenity=clinic", "healthcare=centre"],
    "ветклиника":   ["amenity=veterinary"],
    "красота":      ["shop=beauty", "shop=hairdresser"],
    "фитнес":       ["leisure=fitness_centre"],
    "стройка":      ["craft=builder", "shop=doityourself", "craft=plumber", "craft=electrician"],
    "металл":       ["craft=metal_construction", "craft=blacksmith"],
    "клининг":      ["shop=laundry", "shop=dry_cleaning"],
    "детский":      ["amenity=kindergarten", "leisure=playground"],
}


def build_query(filters, city):
    parts = []
    for f in filters:
        k, _, v = f.partition("=")
        parts.append(f'  nwr["{k}"="{v}"](area.searchArea);')
    body = "\n".join(parts)
    return f"""[out:json][timeout:180];
area["name"="{city}"]["admin_level"~"^(4|6)$"]->.searchArea;
(
{body}
);
out center tags;"""


def run_query(q):
    data = urllib.parse.urlencode({"data": q}).encode()
    last = None
    for url in ENDPOINTS:
        for attempt in range(2):
            try:
                req = urllib.request.Request(url, data=data,
                                             headers={"User-Agent": "sales-leads/1.0"})
                with urllib.request.urlopen(req, timeout=300) as r:
                    return json.loads(r.read().decode())
            except Exception as e:
                last = e
                print(f"# {url}: {e}, повтор", file=sys.stderr)
                time.sleep(5)
    raise SystemExit(f"Overpass недоступен: {last}")


def phone_of(t):
    for k in ("phone", "contact:phone", "contact:mobile", "phone:RU"):
        if t.get(k):
            return t[k]
    return ""


def site_of(t):
    for k in ("website", "contact:website", "url", "contact:vk", "contact:instagram"):
        if t.get(k) and k in ("website", "contact:website", "url"):
            return t[k]
    return ""


def social_of(t):
    out = []
    for k in ("contact:vk", "contact:instagram", "contact:telegram",
              "contact:whatsapp", "contact:facebook", "vk"):
        if t.get(k):
            out.append(t[k])
    return "; ".join(out)


def main():
    if "--list" in sys.argv:
        for k, v in PRESETS.items():
            print(f"{k:14} {', '.join(v)}")
        return
    if len(sys.argv) < 3:
        sys.exit('Использование: python3 osm-leads.py <ниша|фильтры> "Город"')

    arg, city = sys.argv[1], sys.argv[2]
    filters = PRESETS.get(arg) or [f.strip() for f in arg.split(";") if f.strip()]
    print(f"# {city} · фильтры: {', '.join(filters)}", file=sys.stderr)

    data = run_query(build_query(filters, city))
    elements = data.get("elements", [])
    print(f"# объектов в OSM: {len(elements)}", file=sys.stderr)

    w = csv.writer(sys.stdout)
    w.writerow(["Компания", "Телефон", "Соцсети", "Адрес", "Категория",
                "Часы работы", "Есть сайт", "Статус", "Следующий шаг"])

    rows, with_phone, with_site = [], 0, 0
    for el in elements:
        t = el.get("tags", {}) or {}
        name = t.get("name") or t.get("operator") or ""
        phone, site = phone_of(t), site_of(t)
        if phone:
            with_phone += 1
        if site:
            with_site += 1
        if not name or not phone or site:
            continue
        addr = " ".join(x for x in [
            t.get("addr:street", ""), t.get("addr:housenumber", "")] if x)
        cat = next((f"{k}={t[k]}" for k in ("shop", "craft", "amenity", "healthcare", "leisure")
                    if t.get(k)), "")
        rows.append([name, phone, social_of(t), addr, cat,
                     t.get("opening_hours", ""), "нет", "не связывались", ""])

    seen = set()
    for r in rows:
        key = (r[0], r[1])
        if key in seen:
            continue
        seen.add(key)
        w.writerow(r)
        sys.stdout.flush()

    print(f"# с телефоном: {with_phone} · с сайтом: {with_site} · "
          f"ЛИДОВ (телефон есть, сайта нет): {len(seen)}", file=sys.stderr)


if __name__ == "__main__":
    main()
