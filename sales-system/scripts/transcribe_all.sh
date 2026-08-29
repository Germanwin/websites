#!/bin/bash
# Локальная транскрипция уроков через whisper.cpp (Metal, Apple Silicon).
#
#   ./scripts/transcribe_all.sh [модель] [папка_вывода]
#
# По умолчанию — large-v3 (точная пунктуация, лучше держит быструю живую речь).
# Альтернатива для черновика: models/ggml-large-v3-turbo.bin (в ~4 раза быстрее).
#
# Идемпотентно: готовые .json пропускаются — можно прерывать и продолжать.
# Порядок обработки: сначала модули, которые приносят деньги.
set -u
ROOT="/Users/hermmoment/coding/websites/sales-system"
MODEL="${1:-$ROOT/models/ggml-large-v3.bin}"
OUT="${2:-$ROOT/03-transcripts/raw}"
AUDIO="$ROOT/01-audio"
LOG="$ROOT/03-transcripts/whisper.log"
mkdir -p "$OUT"

# приоритет: чем раньше в списке — тем раньше транскрибируется
PRIORITY=(
  "Поиск клиентов"
  "Выход на 200-300к"
  "Ультрабазовые"
  "Модуль Главнокомандующего"
  "Юридическая"
  ""                    # всё остальное
)

ordered=()
declare -a seen=()
for pat in "${PRIORITY[@]}"; do
  while IFS= read -r f; do
    [ -z "$f" ] && continue
    case " ${ordered[*]-} " in *" $f "*) continue;; esac
    ordered+=("$f")
  done < <(ls -1 "$AUDIO"/*.wav 2>/dev/null | grep -F "$pat")
done

total=${#ordered[@]}
i=0
start=$(date +%s)
echo "Модель: $(basename "$MODEL")   файлов: $total"
for f in "${ordered[@]}"; do
  i=$((i+1))
  base=$(basename "$f" .wav)
  if [ -f "$OUT/$base.json" ]; then
    echo "[$i/$total] SKIP $base"
    continue
  fi
  t0=$(date +%s)
  echo "[$i/$total] $base"
  whisper-cli -m "$MODEL" -f "$f" -l ru -t 8 -np -oj -of "$OUT/$base" >> "$LOG" 2>&1 \
    || { echo "    !! ОШИБКА, см. $LOG"; continue; }
  echo "    готово за $(( $(date +%s) - t0 ))с"
done
echo "ГОТОВО за $(( ($(date +%s) - start) / 60 )) мин;  файлов: $(ls -1 "$OUT"/*.json | wc -l | tr -d ' ')"
