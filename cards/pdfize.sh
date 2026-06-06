#!/usr/bin/env bash
set -euo pipefail

usage() {
    cat <<EOF
Usage:
  $(basename "$0") [options] file1.svg [file2.svg ...]

Options:
  -o, --output FILE   Output PDF (default: output.pdf)
  -h, --help          Show this help

Examples:
  $(basename "$0") a.svg b.svg c.svg
  $(basename "$0") -o print.pdf *.svg
EOF
}

OUTPUT="output.pdf"
declare -a SVGS=()

while [[ $# -gt 0 ]]; do
    case "$1" in
        -o|--output)
            if [[ $# -lt 2 ]]; then
                echo "Error: $1 requires a filename" >&2
                exit 1
            fi
            OUTPUT="$2"
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        --)
            shift
            SVGS+=("$@")
            break
            ;;
        -*)
            echo "Unknown option: $1" >&2
            usage >&2
            exit 1
            ;;
        *)
            SVGS+=("$1")
            shift
            ;;
    esac
done

if [[ ${#SVGS[@]} -eq 0 ]]; then
    echo "Error: no SVG files specified" >&2
    usage >&2
    exit 1
fi

if ! command -v inkscape >/dev/null 2>&1; then
    echo "Error: inkscape not found in PATH" >&2
    exit 1
fi

MERGER=""
if command -v pdfunite >/dev/null 2>&1; then
    MERGER="pdfunite"
elif command -v qpdf >/dev/null 2>&1; then
    MERGER="qpdf"
else
    echo "Error: need either pdfunite or qpdf installed" >&2
    exit 1
fi

TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

declare -a PDFS=()

for svg in "${SVGS[@]}"; do
    if [[ ! -f "$svg" ]]; then
        echo "Error: file not found: $svg" >&2
        exit 1
    fi

    base=$(basename "$svg")
    pdf="$TMPDIR/${base%.*}.pdf"

    echo "Converting: $svg"

    inkscape \
        --export-type=pdf \
        --export-filename="$pdf" \
        "$svg"

    PDFS+=("$pdf")
done

echo "Merging into: $OUTPUT"

case "$MERGER" in
    pdfunite)
        pdfunite "${PDFS[@]}" "$OUTPUT"
        ;;
    qpdf)
        qpdf --empty --pages "${PDFS[@]}" -- "$OUTPUT"
        ;;
esac

echo "Done: $OUTPUT"

