#!/bin/bash


set -euo pipefail

INPUT="${1:-list.txt}"

count=1
while IFS= read -r line; do
    
    count_c=$(printf "%03d\n" "$count")
    shopt -s nullglob
    files=("${count_c}"*)
    if (( ${#files[@]} > 0 )); then
        echo "$count_c -    OK   - $line"
    else
        echo "$count_c - MISSING - $line"
    fi

    ((count++))
done < "$INPUT"
