#!/usr/bin/env python3
"""Render a scripted terminal transcript; never execute its contents."""
import argparse
import base64
import html
import json
from pathlib import Path
import shutil
import subprocess
import tempfile


COLORS = {
    "text": "#f5edf5", "green": "#55ff00", "cyan": "#51def0",
    "yellow": "#eade49", "purple": "#b785ff", "pink": "#ff0080",
    "lime": "#b8df00",
}


def render(data, font_path):
    size = int(data.get("fontSize", 20))
    step = int(data.get("lineHeight", 27))
    padding = int(data.get("padding", 40))
    width = int(data.get("width", 947))
    lines = data["lines"]
    height = 66 + padding * 2 + max(1, len(lines)) * step
    if min(size, step, width) <= 0 or padding < 0:
        raise ValueError("Dimensions must be positive; padding may be zero")
    esc = lambda value: html.escape(str(value), quote=True)
    family = data.get("fontFamily", "DejaVu Sans Mono")
    font = esc(f"'{family}', monospace")
    encoded_font = base64.b64encode(font_path.read_bytes()).decode("ascii")
    css_family = json.dumps(family).replace("<", "\\3c ")
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'<defs><style>@font-face {{ font-family: {esc(css_family)}; src: url("data:font/ttf;base64,{encoded_font}") format("truetype"); }}</style></defs>',
        f'<rect width="{width}" height="{height}" rx="15" fill="#1c071f"/>',
        f'<path d="M0 66H{width}" stroke="#412044"/>',
    ]
    for x, color in [(30, "#ff5f57"), (51, "#febc2e"), (72, "#28c840")]:
        parts.append(f'<circle cx="{x}" cy="34" r="6" fill="{color}"/>')
    parts.append(f'<text x="{width / 2:g}" y="40" text-anchor="middle" font-family="{font}" font-size="15" fill="#cda9d1">{esc(data.get("title", "Terminal"))}</text>')
    for index, line in enumerate(lines):
        spans = [{"text": line}] if isinstance(line, str) else line
        parts.append(f'<text x="{padding}" y="{66 + padding + size + index * step}" font-family="{font}" font-size="{size}" xml:space="preserve">')
        column = 0
        for span in spans:
            color = span.get("color", "text")
            x = padding + column * size * 0.60205
            parts.append(f'<tspan x="{x:g}" fill="{esc(COLORS.get(color, color))}">{esc(span["text"])}</tspan>')
            column += len(span["text"])
        parts.append('</text>')
    parts.append('</svg>')
    return "\n".join(parts) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("transcript", type=Path)
    parser.add_argument("output", type=Path, help="Output .svg or .png")
    parser.add_argument("--font", type=Path, help="Monospace TTF to embed (default: locate fontFamily with fontconfig)")
    args = parser.parse_args()
    try:
        suffix = args.output.suffix.lower()
        if suffix not in (".svg", ".png"):
            raise ValueError("Output must end in .svg or .png")
        data = json.loads(args.transcript.read_text(encoding="utf-8"))
        font_path = args.font
        if font_path is None:
            if not shutil.which("fc-match"):
                raise ValueError("Pass --font /path/to/monospace.ttf or install fontconfig")
            match = subprocess.run(
                ["fc-match", "-f", "%{file}", data.get("fontFamily", "DejaVu Sans Mono")],
                check=True, capture_output=True, text=True,
            )
            font_path = Path(match.stdout)
        svg = render(data, font_path)
        if suffix == ".svg":
            args.output.write_text(svg, encoding="utf-8")
        else:
            converter = shutil.which("magick") or shutil.which("convert")
            if not converter:
                raise ValueError("PNG export requires ImageMagick (magick or convert)")
            with tempfile.TemporaryDirectory(prefix="terminal-shot-") as directory:
                source = Path(directory) / "terminal.svg"
                source.write_text(svg, encoding="utf-8")
                subprocess.run([converter, "-background", "none", str(source),
                                "-strip", "-define", "png:exclude-chunks=date,time",
                                str(args.output.resolve())], check=True)
    except (ValueError, KeyError, TypeError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"terminal-shot: {error}\n")


if __name__ == "__main__":
    main()
