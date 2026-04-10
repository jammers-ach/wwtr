#!/bin/bash
set -euo pipefail

INPUT="list.txt"
TEMPLATE="${1:-A5_template.svg}"
sheet_num=1
chunk_size="${2:-8}"

if ! [[ "$chunk_size" =~ ^[0-9]+$ ]] || (( chunk_size < 1 || chunk_size > 20 )); then
  echo "Error: chunk_size must be an integer between 1 and 20" >&2
  exit 1
fi

changename() {
  num=$(printf "%02d\n" "$1")
  echo "${TEMPLATE/_template/_sheet_$num}"
}

# Read input.txt in chunks of 8 lines
lines_buffer=()
while IFS= read -r line; do
    lines_buffer+=("$line")
    if [ "${#lines_buffer[@]}" -eq "$chunk_size" ]; then
        name="$(changename "$sheet_num")"

        if [[ -f "$name" ]]; then
            echo "$name" exists, skipping
        else
            cp "$TEMPLATE" "$name"

            text_num=1
            for line in "${lines_buffer[@]}"; do
                sed -i "s|Text $text_num|$(printf '%s' "$line" | sed 's/[&/\]/\\&/g')|g" "$name"
                echo "$sheet_num.$text_num: $line"
                ((text_num++))
            done
        fi
        ((sheet_num++))
        lines_buffer=()
    fi
done < "$INPUT"

# Handle remaining lines (less than 8)
if [ "${#lines_buffer[@]}" -gt 0 ]; then
    name="$(changename "$sheet_num")"
    if [[ -f "$name" ]]; then
        echo "$name" exists, skipping
    else
        cp "$TEMPLATE" "$name"

        text_num=1
        for line in "${lines_buffer[@]}"; do
            sed -i "s|Text $text_num|$(printf '%s' "$line" | sed 's/[&/\]/\\&/g')|g" "$name"
            echo "$sheet_num.$text_num: $line"
            ((text_num++))
        done
    fi
fi

echo "Finished generating sheets."
