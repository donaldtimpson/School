#!/bin/bash
# Renders src/*.html -> pdf/*.pdf, injecting the shared stylesheet.
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
CSS="$DIR/src/style.css"
mkdir -p "$DIR/build" "$DIR/pdf"

targets=("$@")
if [ ${#targets[@]} -eq 0 ]; then targets=("$DIR"/src/*.html); fi

for f in "${targets[@]}"; do
  [ -f "$f" ] || f="$DIR/src/$(basename "$f")"
  name="$(basename "$f" .html)"
  out="$DIR/build/$name.html"
  python3 - "$f" "$CSS" "$out" <<'PY'
import sys
src, css, out = sys.argv[1], sys.argv[2], sys.argv[3]
html = open(src, encoding='utf-8').read()
style = "<style>\n" + open(css, encoding='utf-8').read() + "\n</style>"
open(out, 'w', encoding='utf-8').write(html.replace("<!--STYLE-->", style))
PY
  "$CHROME" --headless --disable-gpu --no-pdf-header-footer \
    --print-to-pdf="$DIR/pdf/$name.pdf" "$out" 2>/dev/null
  echo "  -> pdf/$name.pdf"
done
