#!/usr/bin/env python3
"""Проверка целостности базы знаний: битые ссылки [[...]] и файлы-сироты."""
import pathlib, re, collections, sys

ROOT = pathlib.Path("/Users/hermmoment/coding/websites/sales-system/knowledge-base")
files = {p.stem: p for p in ROOT.rglob("*.md")}
bad = collections.defaultdict(list)
linked = set()

for p in ROOT.rglob("*.md"):
    for m in re.findall(r"\[\[([^\]]+)\]\]", p.read_text(encoding="utf-8")):
        linked.add(m)
        if m not in files:
            bad[m].append(str(p.relative_to(ROOT)))

print(f"файлов в базе: {len(files)}")

if bad:
    print("\n⚠️  битые ссылки:")
    for k, v in sorted(bad.items()):
        print(f"   [[{k}]]  ← {', '.join(sorted(set(v)))}")
else:
    print("✅ все ссылки валидны")

orphans = sorted(set(files) - linked - {"README"})
if orphans:
    print("\nℹ️  ни на кого не ссылаются (проверь, нужны ли ссылки из README):")
    for o in orphans:
        print("   ", files[o].relative_to(ROOT))

sys.exit(1 if bad else 0)
