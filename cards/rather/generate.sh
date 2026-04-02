#!/bin/bash

set -euo pipefail

set -x

# File paths
INPUT="list.txt"
TEMPLATE="A5_rather_template.svg"

# Counter for sheet number
sheet_num=1


# Read input.txt in chunks of 8 lines
while IFS= read -r line1 && IFS= read -r line2 && IFS= read -r line3 && \
      IFS= read -r line4 && IFS= read -r line5 && IFS= read -r line6 && \
      IFS= read -r line7 && IFS= read -r line8; do

    # Copy template to new sheet file
    OUTFILE="A5_rather_${sheet_num}.svg"
    cp "$TEMPLATE" "$OUTFILE"

    # Replace placeholders with lines
    sed -i \
        -e "s/Text 1/$line1/" \
        -e "s/Text 2/$line2/" \
        -e "s/Text 3/$line3/" \
        -e "s/Text 4/$line4/" \
        -e "s/Text 5/$line5/" \
        -e "s/Text 6/$line6/" \
        -e "s/Text 7/$line7/" \
        -e "s/Text 8/$line8/" \
        "$OUTFILE"

    ((sheet_num++))
done < "$INPUT"

# Handle remaining lines if input.txt is not a multiple of 8
remaining_lines=()
while IFS= read -r line; do
    remaining_lines+=("$line")
done

if [ ${#remaining_lines[@]} -gt 0 ]; then
    OUTFILE="A5_rather_${sheet_num}.svg"
    cp "$TEMPLATE" "$OUTFILE"
    for i in "${!remaining_lines[@]}"; do
        placeholder=$((i+1))
        sed -i "s/text $placeholder/${remaining_lines[i]}/" "$OUTFILE"
    done
fi

echo "Finished generating sheets."
