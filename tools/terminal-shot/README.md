# Terminal Shot

A small Python 3 CLI for scripted terminal images styled after `docs/images/terminal.png`. Displayed commands are text only. No terminal, shell execution, clock, random values, or screenshot capture is involved.

From the repository root:

```sh
python3 tools/terminal-shot/terminal_shot.py tools/terminal-shot/example.json /tmp/terminal.svg
python3 tools/terminal-shot/terminal_shot.py tools/terminal-shot/example.json /tmp/terminal.png
```

SVG generation uses the Python standard library and embeds the font so browser viewers do not need it installed. By default, fontconfig (`fc-match`) locates DejaVu Sans Mono. Alternatively, pass `--font /path/to/monospace.ttf`. PNG export also requires ImageMagick and the configured font installed.

Edit the JSON to change `title`, `width`, `fontSize`, `lineHeight`, `padding`, `fontFamily`, and `lines`. Height follows the line count. Each line is a string or an array of spans:

```json
[{"text": "% ", "color": "green"}, {"text": "echo hello"}]
```

Named colors: `text`, `green`, `cyan`, `yellow`, `purple`, `pink`, `lime`. You can also supply CSS hex colors. Spaces and blank lines are preserved. Choose a width large enough for the transcript; lines do not wrap or auto-fit.

Identical input and font files produce identical SVG bytes. PNG bytes are repeatable with the same ImageMagick version and fonts; metadata timestamps are excluded. Keep those dependencies fixed when comparing image hashes across machines. SVG viewers that disable embedded web fonts fall back to their monospace font. Span positions assume DejaVu Sans Mono metrics; use that font for exact alignment.
