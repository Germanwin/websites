#!/usr/bin/env python3
"""OCR отдельных картинок из 00-source/ (скриншоты лендингов, слайды-картинки).

Высокие скриншоты режутся на куски по 2400 px — иначе tesseract захлёбывается.
Узкие апскейлятся до 1600 px по ширине для читаемости. Идемпотентно.
"""
import os, subprocess, tempfile, pathlib
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "00-source"
OUT = ROOT / "04-slides-ocr"
EXT = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}
CHUNK = 2400
MIN_W = 1600

OUT.mkdir(exist_ok=True)

for path in sorted(SRC.rglob("*")):
    if not path.is_file() or path.suffix.lower() not in EXT:
        continue
    flat = str(path.relative_to(SRC).with_suffix("")).replace("/", "__")
    dst = OUT / f"{flat}.md"
    if dst.exists():
        continue
    try:
        im = Image.open(path).convert("RGB")
    except Exception as e:
        print("  пропуск:", flat, e)
        continue
    w, h = im.size
    if w < 400 or h < 400:          # иконки и логотипы не распознаём
        continue
    parts, y = [], 0
    while y < h:
        tile = im.crop((0, y, w, min(h, y + CHUNK)))
        if w < MIN_W:
            tile = tile.resize((MIN_W, int(MIN_W * tile.size[1] / w)), Image.LANCZOS)
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as t:
            tile.save(t.name)
            r = subprocess.run(["tesseract", t.name, "stdout", "-l", "rus+eng", "--psm", "3"],
                               capture_output=True, text=True)
        os.unlink(t.name)
        parts.append(r.stdout)
        y += CHUNK
    text = "\n".join(parts).strip()
    if len(text) < 40:
        continue
    header = f"# {path.relative_to(SRC)}\n\n*(OCR картинки, tesseract rus+eng, {w}×{h} px)*\n\n"
    dst.write_text(header + text + "\n", encoding="utf-8")
    print("  OCR:", flat, f"({len(text)} симв.)")
