#!/bin/bash
# ============================================================
#  ingest.sh — добавить любые новые материалы в базу знаний
# ============================================================
#
#  Использование:
#     ./scripts/ingest.sh /путь/к/папке-или-файлу [имя-коллекции]
#
#  Примеры:
#     ./scripts/ingest.sh ~/Downloads/Модули по сайтам.zip sites
#     ./scripts/ingest.sh ~/Downloads/новый-урок.mp4 sales
#     ./scripts/ingest.sh ~/Downloads/папка_с_уроками
#
#  Что делает:
#     1. Распаковывает архив (если это .zip), чиня кодировку имён
#     2. Видео (mp4/mov/mkv/avi/webm) → WAV 16 kHz mono → транскрипт
#     3. Аудио (mp3/m4a/wav/aac/ogg)  → WAV 16 kHz mono → транскрипт
#     4. PDF/PPTX/XLSX/DOCX/TXT       → текст в 02-docs-text/
#     5. PDF без текстового слоя      → OCR (rus+eng) в 04-slides-ocr/
#     6. PNG/JPG/WEBP (скриншоты)     → OCR (rus+eng) в 04-slides-ocr/
#
#  Всё идемпотентно: уже обработанные файлы пропускаются.
# ============================================================
set -u
ROOT="/Users/hermmoment/coding/websites/sales-system"
SRC_IN="${1:?Укажите путь к файлу, папке или архиву}"
COLLECTION="${2:-$(basename "$SRC_IN" | sed 's/\.[^.]*$//')}"

MODEL="$ROOT/models/ggml-large-v3-turbo.bin"
PY="$ROOT/.venv/bin/python"
SRC="$ROOT/00-source/$COLLECTION"
AUDIO="$ROOT/01-audio"
TRAW="$ROOT/03-transcripts/raw"
mkdir -p "$SRC" "$AUDIO" "$TRAW" "$ROOT/02-docs-text" "$ROOT/04-slides-ocr"

echo "==> Коллекция: $COLLECTION"

# --- 1. Импорт в 00-source ---
if [[ "$SRC_IN" == *.zip ]]; then
  echo "==> Распаковка архива..."
  "$PY" - "$SRC_IN" "$SRC" <<'PY'
import sys, zipfile, pathlib
src, dest = sys.argv[1], sys.argv[2]
z = zipfile.ZipFile(src)
for i in z.infolist():
    name = i.filename
    if not (i.flag_bits & 0x800):          # имена не в UTF-8 — чиним
        for enc in ("cp866", "cp1251"):
            try:
                name = name.encode("cp437").decode(enc); break
            except Exception: pass
    target = pathlib.Path(dest) / name
    if i.is_dir():
        target.mkdir(parents=True, exist_ok=True); continue
    target.parent.mkdir(parents=True, exist_ok=True)
    with z.open(i) as s, open(target, "wb") as d:
        d.write(s.read())
print("распаковано")
PY
elif [ -d "$SRC_IN" ]; then
  rsync -a "$SRC_IN"/ "$SRC"/
else
  cp "$SRC_IN" "$SRC"/
fi

# --- 2. Медиа → WAV 16 kHz mono ---
echo "==> Извлечение аудио..."
find "$SRC" -type f \( -iname "*.mp4" -o -iname "*.mov" -o -iname "*.mkv" -o -iname "*.avi" \
  -o -iname "*.webm" -o -iname "*.mp3" -o -iname "*.m4a" -o -iname "*.wav" -o -iname "*.aac" \
  -o -iname "*.ogg" \) -print0 | while IFS= read -r -d '' f; do
  rel="${f#$ROOT/00-source/}"
  flat="$(echo "${rel%.*}" | sed 's|/|__|g')"
  [ -f "$AUDIO/$flat.wav" ] && continue
  ffmpeg -nostdin -v error -i "$f" -vn -ac 1 -ar 16000 -c:a pcm_s16le "$AUDIO/$flat.wav" </dev/null \
    && echo "    аудио: $flat"
done

# --- 3. Транскрипция ---
echo "==> Транскрипция (whisper.cpp, Metal)..."
for f in "$AUDIO"/*.wav; do
  [ -e "$f" ] || continue
  base="$(basename "$f" .wav)"
  [ -f "$TRAW/$base.json" ] && continue
  echo "    → $base"
  whisper-cli -m "$MODEL" -f "$f" -l ru -t 8 -np -oj -of "$TRAW/$base" \
    >> "$ROOT/03-transcripts/whisper.log" 2>&1
done

# --- 4. Транскрипты → markdown ---
"$PY" "$ROOT/scripts/build_transcripts.py"

# --- 5. Документы → текст ---
echo "==> Извлечение текста из документов..."
"$PY" "$ROOT/scripts/extract_docs.py" > /dev/null

# --- 6. OCR презентаций ---
echo "==> OCR презентаций..."
"$PY" "$ROOT/scripts/ocr_pdfs.py"

# --- 7. OCR отдельных картинок (скриншоты лендингов, слайды-картинки) ---
echo "==> OCR картинок..."
"$PY" "$ROOT/scripts/ocr_images.py"

echo
echo "==> ГОТОВО. Материалы добавлены в базу."
echo "    Транскрипты:  $ROOT/03-transcripts/"
echo "    Документы:    $ROOT/02-docs-text/"
echo "    Слайды (OCR): $ROOT/04-slides-ocr/"
echo
echo "    Дальше скажите Claude: «обнови базу знаний из новых материалов»"
