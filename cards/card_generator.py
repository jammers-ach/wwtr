#!/usr/bin/env python3
import argparse
import sys
import re
from pathlib import Path


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



def apply_template(template: str, texts:str, cadence:int, image_names = []) -> [str]:
    '''takes the template, and makes N new files, with <cadence> cards in each
    will apply the texts to each card, and if image_names is specified, it will load in all the iamge names'''
    loop = lambda lst,n: [lst[i:i+n] for i in range (0, len(lst), n)]

    documents = []
    for a in loop(texts, cadence):
        d = template
        for i, text in enumerate(a):
            d = d.replace(f"Text {i+1}", text.replace("\n",""))
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

    template = "".join(template_file.open().readlines())
    cadence = determine_num_cards(template)
    word_list = list_file.open().readlines()

    cards = apply_template(template, word_list, cadence)

    genfname = lambda orig, number: orig.replace("template", f"sheet{number:02d}")

    for i, card in enumerate(cards):
        new_fname = genfname(args.template_file, i+1)
        with open(new_fname, "w") as f:
            f.write(card)
        print(f"written {new_fname}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
