#!/bin/bash
SRC="/Users/hermmoment/coding/websites/sales-system/00-source/Модули по заработку"
OUT="/Users/hermmoment/coding/websites/sales-system/01-audio"
mkdir -p "$OUT"
n=0
find "$SRC" -name "*.mp4" -print0 | while IFS= read -r -d '' f; do
  rel="${f#$SRC/}"
  flat=$(echo "$rel" | sed 's|/|__|g; s|\.mp4$||')
  dest="$OUT/${flat}.wav"
  if [ -f "$dest" ]; then echo "SKIP $flat"; continue; fi
  ffmpeg -nostdin -v error -i "$f" -vn -ac 1 -ar 16000 -c:a pcm_s16le "$dest" </dev/null && echo "OK $flat"
done
echo "AUDIO EXTRACTION DONE"
ls -1 "$OUT" | wc -l
