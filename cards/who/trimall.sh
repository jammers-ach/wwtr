#!/bin/bash

set -euo pipefail

for f in [0-9]*.png; do
  [ -e "$f" ] || continue
  echo "Trimming $f"
  convert "$f" -trim +repage "$f"
done


