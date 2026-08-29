#!/usr/bin/env python3
"""JSON от whisper.cpp → читаемые markdown-транскрипты с таймкодами."""
import json, pathlib, re

ROOT = pathlib.Path("/Users/hermmoment/coding/websites/sales-system")
RAW = ROOT / "03-transcripts" / "raw"
OUT = ROOT / "03-transcripts"


def build(p: pathlib.Path) -> tuple[str, int]:
    d = json.loads(p.read_text(encoding="utf-8"))
    segs = d.get("transcription", [])
    title = p.stem.replace("__", "  ›  ")
    lines = [f"# {title}", ""]

    buf, start = [], None
    for s in segs:
        txt = s["text"].strip()
        if not txt:
            continue
        if start is None:
            start = s["offsets"]["from"] / 1000
        buf.append(txt)
        # абзац закрываем на конце предложения при достаточной длине
        if sum(len(x) for x in buf) > 600 and re.search(r"[.!?]$", txt):
            m, sec = divmod(int(start), 60)
            lines += [f"**[{m:02d}:{sec:02d}]** " + " ".join(buf), ""]
            buf, start = [], None
    if buf:
        m, sec = divmod(int(start or 0), 60)
        lines += [f"**[{m:02d}:{sec:02d}]** " + " ".join(buf), ""]

    body = "\n".join(lines)
    return body, len(body)


def main():
    n = 0
    total_chars = 0
    for p in sorted(RAW.glob("*.json")):
        dest = OUT / (p.stem + ".md")
        if dest.exists() and dest.stat().st_mtime > p.stat().st_mtime:
            continue
        body, size = build(p)
        dest.write_text(body, encoding="utf-8")
        total_chars += size
        n += 1
    print(f"транскриптов собрано: {n}, символов: {total_chars:,}")


if __name__ == "__main__":
    main()
