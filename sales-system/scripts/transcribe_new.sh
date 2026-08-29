#!/bin/bash
set -u
ROOT="/Users/hermmoment/coding/websites/sales-system"
MODEL="$ROOT/models/ggml-large-v3-turbo.bin"
TRAW="$ROOT/03-transcripts/raw"
mkdir -p "$TRAW"
n=0; done_=0
for f in "$ROOT"/01-audio/*.wav; do
  [ -e "$f" ] || continue
  base="$(basename "$f" .wav)"
  [ -f "$TRAW/$base.json" ] && continue
  n=$((n+1))
  echo "=== [$n] $base ===" >> "$ROOT/03-transcripts/whisper.log"
  whisper-cli -m "$MODEL" -f "$f" -l ru -t 8 -np -oj -of "$TRAW/$base" \
    >> "$ROOT/03-transcripts/whisper.log" 2>&1
  echo "DONE $base"
done
"$ROOT/.venv/bin/python" "$ROOT/scripts/build_transcripts.py"
echo "ALL TRANSCRIPTION COMPLETE"
