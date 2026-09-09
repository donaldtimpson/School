#!/bin/bash
# pp.sh START END  -> prints book text for PRINTED page range (offset +2 to PDF pages)
DIR="$(cd "$(dirname "$0")" && pwd)"
awk -v s="$(( $1 + 2 ))" -v e="$(( $2 + 2 ))" 'BEGIN{RS="\f"} NR>=s && NR<=e' "$DIR/text/book.txt"
