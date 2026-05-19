#!/bin/bash

set -euo pipefail

for f in images/[0-9]*.png; do
  [ -e "$f" ] || continue
  echo "Trimming $f"
  convert "$f" -trim +repage "$f"
done


