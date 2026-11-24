# profile_svg

`profile_svg` is a small Python project that generates the animated SVG used
in the GitHub profile README. It uses the `code2svg` implementation included in
this directory to draw a syntax-highlighted code example from TrueType font
glyphs.

The project is intentionally small and specific: it generates one concrete
profile graphic and does not parse arbitrary source files. The code, colors,
animation, and layout for that graphic are defined in `__main__.py`.

## Requirements

- Python 3.12 or newer
- A TrueType font (`.ttf`) containing the glyphs used by the example

Install the Python dependency from this directory with:

```bash
python -m pip install -r requirements.txt
```

The dependency is [fontTools](https://github.com/fonttools/fonttools), which is
used to read the font and generate the SVG glyph paths.

## Usage

Run the module from the repository root with an output path and a font:

```bash
python -m profile_svg output.svg --font-file path/to/font.ttf
```

For formatted SVG output, add `--pretty` (or `-p`):

```bash
python -m profile_svg output.svg --font-file path/to/font.ttf --pretty
```

To add invisible, machine-readable text elements for screen readers, use
`--accessibility` (or `-a`):

```bash
python -m profile_svg output.svg --font-file path/to/font.ttf --accessibility
```

The command overwrites an existing regular output file. The font file must
exist and be a regular file.

## Command-line options

| Option | Description |
| --- | --- |
| `output` | Path of the SVG file to create. |
| `-f`, `--font-file` | TrueType font file used to create the glyph paths. Required. |
| `-p`, `--pretty` | Format the SVG with line breaks and indentation. |
| `-a`, `--accessibility` | Include invisible text for tools such as screen readers. |

## `code2svg`

The `code2svg` directory contains the reusable SVG-generation components:
token colors, font conversion, SVG nodes, and animation support. It is an
implementation detail of this project rather than a standalone command-line
tool.

Because the entry point uses package-relative imports, invoke it with
`python -m profile_svg` from the repository root instead of running
`profile_svg/__main__.py` directly.
