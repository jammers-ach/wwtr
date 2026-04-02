#!/bin/bash
set -euo pipefail

INPUT="list.txt"
TEMPLATE="${1:-A5_template.svg}"
sheet_num=1



# Read input.txt in chunks of 8 lines
lines_buffer=()
while IFS= read -r line; do
    lines_buffer+=("$line")
    if [ "${#lines_buffer[@]}" -eq 8 ]; then
        name="sheet_${sheet_num}.svg"

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
    name="sheet_${sheet_num}.svg"
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
