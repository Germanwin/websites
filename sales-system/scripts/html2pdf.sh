#!/bin/bash
# ============================================================
#  html2pdf.sh — превратить КП (или любой артефакт) в PDF
# ============================================================
#
#   ./scripts/html2pdf.sh путь/к/файлу.html [выход.pdf]
#
# Работает с файлами в формате артефакта (без <html>/<head>/<body>):
# скрипт сам оборачивает их в полноценный документ, форсирует светлую
# тему, задаёт формат A4 и запрещает разрывы страниц внутри карточек,
# таблиц и блоков.
#
# Требуется Google Chrome (уже установлен на этой машине).
# ============================================================
set -eu
SRC="${1:?Укажите путь к .html}"
OUT="${2:-${SRC%.html}.pdf}"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
TMP="$(mktemp -d)"
PRINT="$TMP/print.html"

python3 - "$SRC" "$PRINT" <<'PY'
import sys, pathlib
src, dest = sys.argv[1], sys.argv[2]
body = pathlib.Path(src).read_text(encoding="utf-8")

PRINT_CSS = """
<style>
  @page { size: A4; margin: 14mm 13mm; }
  html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  body {
    padding: 0 !important;
    font-size: 10.4pt !important;
    line-height: 1.5 !important;
    background: var(--ground) !important;
  }
  .wrap { max-width: none !important; }

  h1 { font-size: 23pt !important; }
  h2 { font-size: 15pt !important; }
  h3 { font-size: 11.5pt !important; }
  .lede { font-size: 11.5pt !important; }
  table { font-size: 9.3pt !important; min-width: 0 !important; }
  th, td { padding: 6px 9px !important; }
  .fact .v { font-size: 16pt !important; }
  .eyebrow { font-size: 8pt !important; }

  header.doc { padding-top: 0 !important; }
  section { padding: 15px 0 !important; }
  .stack { gap: 12px !important; }
  footer.doc { padding-top: 22px !important; }

  /* на A4 все группы показателей идут ровно в один ряд — без пустых ячеек */
  .facts { grid-template-columns: repeat(4, 1fr) !important; }
  .grid-2, .vs { gap: 10px !important; }
  .card { padding: 14px 16px !important; }

  /* не рвать смысловые блоки между страницами */
  .card, .facts, .fact, .tablewrap, .problem, .note, .todo,
  .vs, .vs .col, ol.steps, ol.steps li, tr, thead,
  footer.doc { break-inside: avoid; page-break-inside: avoid; }
  h1, h2, h3 { break-after: avoid; page-break-after: avoid; }
  .picket { break-inside: avoid; }
  table { break-inside: auto; }
  thead { display: table-header-group; }

  /* ссылки в печати — без подчёркивания цветом экрана */
  a { text-decoration: none; }
</style>
"""

html = f"""<!doctype html>
<html lang="ru" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{body.split('</style>')[0]}</style>
{PRINT_CSS}
</head>
<body>
{'</style>'.join(body.split('</style>')[1:])}
</body>
</html>"""
pathlib.Path(dest).write_text(html, encoding="utf-8")
print("подготовлено")
PY

"$CHROME" --headless=new --disable-gpu --no-pdf-header-footer \
  --virtual-time-budget=4000 \
  --print-to-pdf="$OUT" "file://$PRINT" 2>/dev/null

rm -rf "$TMP"
echo "PDF: $OUT"
ls -lh "$OUT" | awk '{print "размер:", $5}'
