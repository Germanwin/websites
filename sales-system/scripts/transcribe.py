#!/usr/bin/env python3
"""Локальная транскрипция всех уроков через MLX Whisper (Apple Silicon GPU).

Использование:
    .venv/bin/python scripts/transcribe.py            # всё, что ещё не сделано
    .venv/bin/python scripts/transcribe.py --force    # заново
"""
import sys, json, time, pathlib

ROOT = pathlib.Path("/Users/hermmoment/coding/websites/sales-system")
AUDIO = ROOT / "01-audio"
OUT = ROOT / "03-transcripts"
MODEL = "mlx-community/whisper-large-v3-turbo"

OUT.mkdir(parents=True, exist_ok=True)
force = "--force" in sys.argv

import mlx_whisper

files = sorted(AUDIO.glob("*.wav"))
print(f"Файлов: {len(files)}  модель: {MODEL}\n")

t_all = time.time()
for i, f in enumerate(files, 1):
    dest_md = OUT / (f.stem + ".md")
    dest_json = OUT / (f.stem + ".json")
    if dest_md.exists() and not force:
        print(f"[{i}/{len(files)}] SKIP {f.stem}")
        continue
    t0 = time.time()
    print(f"[{i}/{len(files)}] {f.stem} ...", flush=True)
    r = mlx_whisper.transcribe(
        str(f),
        path_or_hf_repo=MODEL,
        language="ru",
        task="transcribe",
        verbose=None,
        condition_on_previous_text=False,
    )
    dest_json.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")

    # markdown с таймкодами по абзацам
    lines = [f"# {f.stem.replace('__', ' / ')}", ""]
    buf, buf_start = [], None
    for seg in r["segments"]:
        if buf_start is None:
            buf_start = seg["start"]
        buf.append(seg["text"].strip())
        if sum(len(x) for x in buf) > 700:
            m, s = divmod(int(buf_start), 60)
            lines.append(f"**[{m:02d}:{s:02d}]** " + " ".join(buf))
            lines.append("")
            buf, buf_start = [], None
    if buf:
        m, s = divmod(int(buf_start or 0), 60)
        lines.append(f"**[{m:02d}:{s:02d}]** " + " ".join(buf))
    dest_md.write_text("\n".join(lines), encoding="utf-8")
    print(f"      готово за {time.time()-t0:.0f}с, {len(r['text'])} символов")

print(f"\nВСЁ ГОТОВО за {(time.time()-t_all)/60:.1f} мин")
