#!/usr/bin/env python3
"""
Проверка «есть ли у компании собственный сайт» по поисковой выдаче.

Никогда не пишет «нет сайта», если поисковик заблокировал запрос — такие строки
помечаются «НЕ ПРОВЕРЕНО».

Сначала проверь, какие поисковики доступны с твоей машины:
    python3 verify-site.py --probe

Потом запускай проверку (бэкенд выберется сам, живой):
    PAUSE=4 python3 verify-site.py ../leads/leads-стоматология.csv "стоматология Санкт-Петербург" > out.csv

Принудительно один бэкенд:  BACKEND=bing python3 verify-site.py ...
Яндекс XML (не режет):      export YANDEX_FOLDER=... YANDEX_APIKEY=...
"""
import base64, csv, json, os, re, sys, time, urllib.parse, urllib.request

CACHE_PATH = os.path.expanduser("~/.cache/verify-site.json")
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
PAUSE = float(os.environ.get("PAUSE", "3"))
Y_FOLDER, Y_APIKEY = os.environ.get("YANDEX_FOLDER", ""), os.environ.get("YANDEX_APIKEY", "")

AGGREGATORS = {
    "2gis.ru", "yandex.ru", "ya.ru", "zoon.ru", "prodoctorov.ru", "napopravku.ru",
    "doctu.ru", "startsmile.ru", "stom-firms.ru", "topdent.ru", "topdantist.ru",
    "krasotaimedicina.ru", "docdoc.ru", "sberhealth.ru", "yell.ru", "orgpage.ru",
    "rusprofile.ru", "list-org.com", "zachestnyibiznes.ru", "avito.ru", "youla.ru",
    "profi.ru", "blizko.ru", "vk.com", "ok.ru", "instagram.com", "facebook.com",
    "t.me", "youtube.com", "flamp.ru", "otzovik.com", "irecommend.ru", "google.com",
    "wikipedia.org", "hh.ru", "spr.ru", "rubri.co", "duckduckgo.com", "bing.com",
    "ecosia.org", "mail.ru", "dzen.ru", "sravni.ru", "otzyvru.com", "medbooking.com",
    "gorodzovet.ru", "tiu.ru", "pulscen.ru", "microsoft.com", "msn.com",
}
BLOCK_MARKERS = ("captcha", "anomaly", "unusual traffic", "are you a robot",
                 "доступ ограничен", "подтвердите, что запросы")


class Blocked(Exception):
    pass


def fetch(url, data=None, headers=None, timeout=30):
    h = {"User-Agent": UA, "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.5"}
    h.update(headers or {})
    req = urllib.request.Request(url, data=data, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.getcode(), r.read().decode(errors="replace")
    except urllib.error.HTTPError as e:
        raise Blocked(f"HTTP {e.code}")
    except Exception as e:
        raise Blocked(type(e).__name__)


def hosts_from_html(html, pattern=r'href="(https?://[^"]+)'):
    out = []
    for m in re.finditer(pattern, html):
        link = urllib.parse.unquote(m.group(1))
        h = urllib.parse.urlparse(link).netloc.lower().replace("www.", "")
        if h and h not in out:
            out.append(h)
    return out


def guard(code, html):
    low = html.lower()
    if code == 202 or any(b in low for b in BLOCK_MARKERS):
        raise Blocked(f"antibot (HTTP {code})")


def b_ddg_lite(q):
    code, html = fetch("https://lite.duckduckgo.com/lite/",
                       data=urllib.parse.urlencode({"q": q}).encode())
    guard(code, html)
    hs = [urllib.parse.urlparse(urllib.parse.unquote(m.group(1))).netloc.replace("www.", "")
          for m in re.finditer(r"uddg=([^\"&]+)", html)]
    return list(dict.fromkeys(h for h in hs if h)) or hosts_from_html(html)


def b_bing(q):
    code, html = fetch("https://www.bing.com/search?" +
                       urllib.parse.urlencode({"q": q, "setlang": "ru", "cc": "RU"}))
    guard(code, html)
    return hosts_from_html(html)


def b_ecosia(q):
    code, html = fetch("https://www.ecosia.org/search?" + urllib.parse.urlencode({"q": q}))
    guard(code, html)
    return hosts_from_html(html)


def b_mojeek(q):
    code, html = fetch("https://www.mojeek.com/search?" + urllib.parse.urlencode({"q": q}))
    guard(code, html)
    return hosts_from_html(html)


def _searx(base):
    def fn(q):
        code, body = fetch(f"{base}/search?" + urllib.parse.urlencode(
            {"q": q, "format": "json"}), headers={"Accept": "application/json"})
        guard(code, body)
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            return hosts_from_html(body)
        return list(dict.fromkeys(
            urllib.parse.urlparse(r.get("url", "")).netloc.replace("www.", "")
            for r in data.get("results", []) if r.get("url")))
    return fn


def b_yandex(q):
    body = json.dumps({"query": {"searchType": "SEARCH_TYPE_RU", "queryText": q},
                       "folderId": Y_FOLDER, "responseFormat": "FORMAT_HTML"}).encode()
    code, raw = fetch("https://searchapi.api.cloud.yandex.net/v2/web/search", data=body,
                      headers={"Authorization": f"Api-Key {Y_APIKEY}",
                               "Content-Type": "application/json"}, timeout=45)
    xml = base64.b64decode(json.loads(raw).get("rawData", "")).decode(errors="replace")
    return [urllib.parse.urlparse(u).netloc.replace("www.", "")
            for u in re.findall(r"<url>(.*?)</url>", xml)]


BACKENDS = {
    "yandex": b_yandex, "bing": b_bing, "ddg_lite": b_ddg_lite, "ecosia": b_ecosia,
    "mojeek": b_mojeek,
    "searx_priv": _searx("https://priv.au"),
    "searx_tiekoetter": _searx("https://searx.tiekoetter.com"),
    "searx_bus": _searx("https://search.bus-hit.me"),
}
ORDER = ["yandex", "bing", "ddg_lite", "ecosia", "mojeek",
         "searx_priv", "searx_tiekoetter", "searx_bus"]

TEST_Q = "стоматология Меридент Санкт-Петербург"


def probe(verbose=True):
    """Возвращает имя первого живого бэкенда."""
    alive = None
    for name in ORDER:
        if name == "yandex" and not (Y_FOLDER and Y_APIKEY):
            continue
        try:
            hosts = BACKENDS[name](TEST_Q)
            own = [h for h in hosts if not is_aggregator(h)]
            # живой бэкенд обязан найти хотя бы один НЕ-агрегаторный домен,
            # иначе это страница-заглушка антибота
            ok = len(hosts) >= 3 and len(own) >= 1
            if verbose:
                print(f"  {'OK ' if ok else 'пусто'} {name:18} хостов {len(hosts):3} "
                      f"{('· напр. ' + own[0]) if own else ''}", file=sys.stderr)
            if ok and alive is None:
                alive = name
                if not verbose:
                    return alive
        except Blocked as e:
            if verbose:
                print(f"  БЛОК {name:18} {e}", file=sys.stderr)
        except Exception as e:
            if verbose:
                print(f"  ОШИБ {name:18} {type(e).__name__}", file=sys.stderr)
        time.sleep(0.5)
    return alive


def root(h):
    p = h.split(".")
    return ".".join(p[-2:]) if len(p) >= 2 else h


def is_aggregator(h):
    h = h.lower().replace("www.", "")
    return any(h == a or h.endswith("." + a) for a in AGGREGATORS) or root(h) in AGGREGATORS


def main():
    if "--probe" in sys.argv:
        print("# проба поисковиков:", file=sys.stderr)
        best = probe()
        print(f"\n# рабочий бэкенд: {best or 'НИ ОДНОГО — нужен Яндекс XML с ключом'}",
              file=sys.stderr)
        return

    if len(sys.argv) < 3:
        sys.exit('Использование: python3 verify-site.py <файл.csv> "контекст поиска"')
    path, context = sys.argv[1], sys.argv[2]

    name = os.environ.get("BACKEND") or probe(verbose=False)
    if not name:
        sys.exit("Ни один поисковик не отвечает. Подключи Яндекс XML "
                 "(YANDEX_FOLDER + YANDEX_APIKEY) — он не режет по частоте.")
    backend = BACKENDS[name]
    print(f"# бэкенд: {name} · пауза {PAUSE}с", file=sys.stderr)

    try:
        cache = json.load(open(CACHE_PATH))
    except Exception:
        cache = {}

    rows = list(csv.reader(open(path)))
    header, data = rows[0], rows[1:]
    w = csv.writer(sys.stdout)
    w.writerow(header + ["Вердикт", "Найденный сайт"])
    n = {"site": 0, "clean": 0, "unknown": 0}

    for i, row in enumerate(data, 1):
        key = f"{row[0]}|{context}"
        if key in cache:
            res = cache[key]
        else:
            res, delay = None, PAUSE
            for attempt in range(3):
                try:
                    hosts = backend(f"{row[0]} {context}")
                    own = [h for h in hosts if not is_aggregator(h)]
                    res = ["есть сайт", own[0]] if own else ["нет сайта", ""]
                    cache[key] = res
                    break
                except Blocked as e:
                    if attempt == 2:
                        res = ["НЕ ПРОВЕРЕНО", str(e)[:40]]
                    else:
                        time.sleep(delay)
                        delay *= 3
            time.sleep(PAUSE)

        v = res[0]
        n["site" if v == "есть сайт" else "clean" if v == "нет сайта" else "unknown"] += 1
        w.writerow(row + res)
        sys.stdout.flush()
        if i % 10 == 0:
            print(f"# {i}/{len(data)} · с сайтом {n['site']} · без сайта {n['clean']} "
                  f"· не проверено {n['unknown']}", file=sys.stderr)
            json.dump(cache, open(CACHE_PATH, "w"), ensure_ascii=False)

    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    json.dump(cache, open(CACHE_PATH, "w"), ensure_ascii=False)
    print(f"# ИТОГ · есть сайт {n['site']} · БЕЗ САЙТА {n['clean']} · "
          f"не проверено {n['unknown']}", file=sys.stderr)


if __name__ == "__main__":
    main()
