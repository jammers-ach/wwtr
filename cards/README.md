# Card generation

This tool generates printable card sheets from an SVG template.

It takes a `list.txt` file containing a list of phrases (one per line), and optionally a directory of images. The template SVG should contain placeholder text fields such as `Text 1`, `Text 2`, etc.

## How it works

### Text replacement
Each placeholder (`Text 1`, `Text 2`, ...) is replaced with the corresponding line from `list.txt`.

Example:
Text 1 -> line 1 from list.txt
Text 2 -> line 2 from list.txt

### Image replacement (optional)
If an image directory is provided, the tool will also update images in the SVG template.

For each placeholder text field, it finds the `<image>` element immediately following it in the SVG and replaces its `xlink:href` (or `href`) attribute with the appropriate image path.

Images are matched by filename prefix:

- Each image file must start with a number (e.g. `001-foo.png`)
- `001` corresponds to line 1 in `list.txt`
- `002` corresponds to line 2, and so on

## Example usage

```bash
./gen_cards who/list.txt who/A5_template.svg --image_dir who/images
```

This will generate one or more output SVG sheets:
    * `who/A5_sheet01.svg`
    * `who/A5_sheet02.svg`
    * ...

Each output file contains a full sheet of populated cards based on the template.
