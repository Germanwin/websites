#!/usr/bin/env python3
"""OCR презентаций без текстового слоя.

Презентации выгружены по шагам анимации: один слайд = много почти одинаковых
страниц. Поэтому после OCR соседние страницы схлопываются — остаётся только
финальное (самое полное) состояние каждого слайда.
"""
import pathlib, subprocess, tempfile, sys, re

ROOT = pathlib.Path("/Users/hermmoment/coding/websites/sales-system")
SRC = ROOT / "00-source"
OUT = ROOT / "04-slides-ocr"
OUT.mkdir(parents=True, exist_ok=True)
DPI = 150


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip().lower()


def ocr_page(pix_path: str) -> str:
    r = subprocess.run(
        ["tesseract", pix_path, "stdout", "-l", "rus+eng", "--psm", "3"],
        capture_output=True, text=True,
    )
    return re.sub(r"\n{3,}", "\n\n", r.stdout).strip()


def process(pdf: pathlib.Path) -> str | None:
    import fitz

    doc = fitz.open(str(pdf))
    pages = []
    with tempfile.TemporaryDirectory() as td:
        for i, page in enumerate(doc):
            # страница уже с текстом — OCR не нужен
            native = (page.get_text() or "").strip()
            if len(native) > 40:
                pages.append(native)
                continue
            png = f"{td}/p{i}.png"
            page.get_pixmap(dpi=DPI).save(png)
            pages.append(ocr_page(png))
    doc.close()

    # схлопываем шаги анимации: страница поглощается следующей, если её текст
    # целиком содержится в тексте соседа
    slides = []
    for t in pages:
        if not t.strip():
            continue
        n = norm(t)
        if slides and (norm(slides[-1]) in n or n in norm(slides[-1])):
            if len(n) > len(norm(slides[-1])):
                slides[-1] = t          # оставляем более полный вариант
            continue
        slides.append(t)

    if not slides:
        return None
    rel = pdf.relative_to(SRC)
    out = [f"# {rel}", "", f"*(OCR; {len(pages)} стр. → {len(slides)} уникальных слайдов)*", ""]
    for i, s in enumerate(slides, 1):
        out += [f"--- слайд {i} ---", s, ""]
    return "\n".join(out)


def main():
    if subprocess.run(["which", "tesseract"], capture_output=True).returncode != 0:
        print("tesseract не установлен: brew install tesseract tesseract-lang", file=sys.stderr)
        return 1

    pdfs = sorted(SRC.rglob("*.pdf"))
    for i, pdf in enumerate(pdfs, 1):
        dest = OUT / (str(pdf.relative_to(SRC)).replace("/", "__") + ".md")
        if dest.exists():
            print(f"[{i}/{len(pdfs)}] SKIP {pdf.name}")
            continue
        print(f"[{i}/{len(pdfs)}] {pdf.relative_to(SRC)}", flush=True)
        try:
            body = process(pdf)
            if body:
                dest.write_text(body, encoding="utf-8")
                print(f"      → {len(body):,} символов")
        except Exception as e:
            print(f"      !! ошибка: {e}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
