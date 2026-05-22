#!/usr/bin/env python3
import argparse
import sys
import re
import os
from pathlib import Path

from xml.etree import ElementTree as ET
from PIL import Image


def determine_num_cards(template: str) -> int:
    '''determines how many cards there are in the templates'''
    # the templates have their placeholders in 'Text X'
    # go through and find out how many, and check theat are in sequential order
    matches = re.findall(r"\bText ([0-9])\b", template)
    nums = sorted([int(x) for x in matches])

    for a,b in  zip(nums, nums[1:]):
        if b != a+1:
            raise ValueError(f"Non sequential Text in template file: Text {a} -> Text {b}")

    if min(nums) != 1:
        raise ValueError("Missing template in text in file: Text 1")

    return len(nums)


def update_svg_image(svg_string: str, search_text: str, image_path: str, output_path: Path) -> str:
    """
    Finds a <tspan> containing exactly `search_text`, then finds the next <image> element
    after it in document order, updates its href, and adjusts width/height to fit while
    preserving aspect ratio.

    Returns the updated SVG as a string.
    """

    if not image_path:
        return svg_string

    # --- Load image dimensions ---
    with Image.open(image_path) as img:
        new_w, new_h = img.size

    # --- Parse SVG ---
    root = ET.fromstring(svg_string)

    # Common namespaces in SVG
    ns = {
        "svg": "http://www.w3.org/2000/svg",
        "xlink": "http://www.w3.org/1999/xlink",
    }

    # Helper: iterate all elements in document order
    all_elements = list(root.iter())

    # --- Find matching tspan ---
    tspan_index = None
    for i, el in enumerate(all_elements):
        if el.tag.endswith("tspan"):
            text = (el.text or "").strip()
            if text == search_text:
                tspan_index = i
                break

    if tspan_index is None:
        raise ValueError(f"No <tspan> found with text: {search_text}")

    # --- Find next <image> element after the tspan ---
    image_el = None
    for el in all_elements[tspan_index + 1:]:
        if el.tag.endswith("image"):
            image_el = el
            break

    if image_el is None:
        raise ValueError(f"No <image> element found after <tspan> text: {search_text}")

    # --- Read existing width/height from the SVG image element ---
    def parse_float(val):
        if val is None:
            return None
        # strips px, pt, etc if present
        m = re.match(r"^\s*([0-9.]+)", val)
        return float(m.group(1)) if m else None

    old_w = parse_float(image_el.get("width"))
    old_h = parse_float(image_el.get("height"))

    if old_w is None or old_h is None:
        raise ValueError("Target <image> element must have width and height attributes.")

    # --- Fit new image into old box while preserving aspect ratio ---
    scale = min(old_w / new_w, old_h / new_h)
    fitted_w = new_w * scale
    fitted_h = new_h * scale

    image_el.set("width", str(fitted_w))
    image_el.set("height", str(fitted_h))

    # Adjust the offset if the new width is different
    if fitted_w < old_w:
        x = float(image_el.get("x"))
        x += (old_w/2) - (fitted_w/2)
        image_el.set("x", str(x))

    if fitted_h < old_h:
        x = float(image_el.get("y"))
        x += (old_h/2) - (fitted_h/2)
        image_el.set("y", str(x))


    # --- Update href ---
    # SVG 2 prefers plain "href", but many SVGs still use xlink:href
    new_path = Path(os.path.relpath(image_path.absolute().parent, output_path.absolute())) / image_path.name
    image_el.set(f"{{{ns['xlink']}}}href", str(new_path))
    image_el.set("href", str(new_path))


    # --- Serialize back to string ---
    return ET.tostring(root, encoding="unicode")

def apply_template(template: str, texts:str, cadence:int, output_path:Path, image_names = {}) -> [str]:
    '''takes the template, and makes N new files, with <cadence> cards in each
    will apply the texts to each card, and if image_names is specified, it will load in all the iamge names'''
    loop = lambda lst,n: [lst[i:i+n] for i in range (0, len(lst), n)]

    documents = []
    for a in loop(list(enumerate(texts)), cadence):
        d = template
        for template_i, indexed_text in enumerate(a):
            list_i, text = indexed_text
            if image_names:
                image = image_names.get(list_i+1, "")
                d = update_svg_image(d, f"Text {template_i+1}", image, output_path)

            d = d.replace(f"Text {template_i+1}", text.replace("\n",""))
        documents.append(d)

    return documents

def die(msg: str, code: int = 1) -> None:
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(code)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generates cards for the game."
    )
    parser.add_argument("list_file", help="Path to the the list file")
    parser.add_argument("template_file", help="Path to the template file")
    parser.add_argument("--image_dir", help="Path to the image dir")
    parser.add_argument("--output_dir", help="Path to the output dir (default same as template dir)")

    args = parser.parse_args()

    list_file = Path(args.list_file)
    template_file = Path(args.template_file)


    if not list_file.exists():
        die(f"list file does not exist: {list_file}")
    if not list_file.is_file():
        die(f"list file is not a file: {list_file}")

    if not template_file.exists():
        die(f"list file does not exist: {template_file}")
    if not template_file.is_file():
        die(f"list file is not a file: {template_file}")

    if args.output_dir:
        output_dir = Path(args.output_dir)
        if not output_dir.exists():
            die(f"output directory does not exist: {output_dir}")
        if not output_dir.is_dir():
            die(f"output directory is not directory: {output_dir}")
    else:
        output_dir = template_file.parent

    image_paths = None
    if args.image_dir:
        image_dir = Path(args.image_dir)
        if not image_dir.exists():
            die(f"image directory does not exist: {image_dir}")
        if not image_dir.is_dir():
            die(f"image directory is not directory: {image_dir}")

        image_paths = {
            int(m.group(1)): p
            for p in image_dir.iterdir()
            if p.is_file() and (m := re.match(r"^(\d{3})", p.name))
        }
        if len(image_paths) == 0:
            die(f"Not found any images in: {image_dir}")
        else:
            print(f"Found {len(image_paths)} images in {image_dir}")


    template = "".join(template_file.open().readlines())
    cadence = determine_num_cards(template)
    word_list = list_file.open().readlines()

    if image_paths and len(image_paths) > 0 and len(image_paths) != len(word_list):
        print(f"WARNING: {len(image_paths)} images found, but {len(word_list)} phrases")

    cards = apply_template(template, word_list, cadence, output_dir, image_paths)

    genfname = lambda orig, number: orig.replace("template", f"sheet{number:02d}")

    for i, card in enumerate(cards):
        new_fname = genfname(template_file.name, i+1)

        with open(output_dir / new_fname, "w") as f:
            f.write(card)
        print(f"written {output_dir / new_fname}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
