#!/usr/bin/env python3
"""Convert source-prepped.png into a monochrome ASCII-art SVG that prints
itself row by row (SMIL wipe + block cursor), then freezes. GitHub strips
<script> but renders SVG SMIL/CSS animation via <img>, so all motion lives
inside the SVG file itself."""
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent

RAMP = " .`:-=+*cs#%@"  # bright (sparse) -> dark (dense); leading space = blank
COLS = 100
CHAR_ASPECT = 0.52  # monospace glyph width / height, used to keep proportions
FONT_SIZE = 8
CHAR_W = FONT_SIZE * 0.6
CHAR_H = FONT_SIZE * 1.15
FILL = "#c9d1d9"
BG = "#0d1117"
CURSOR_COLOR = "#39d353"

ROW_STAGGER_MS = 34
ROW_DUR_MS = 220


def esc(ch: str) -> str:
    return {"&": "&amp;", "<": "&lt;", ">": "&gt;"}.get(ch, ch)


def image_to_rows(img_path: Path) -> list[str]:
    img = Image.open(img_path).convert("L")
    rows_count = max(1, round(COLS * (img.height / img.width) * CHAR_ASPECT))
    small = img.resize((COLS, rows_count), Image.Resampling.BOX)

    ramp_len = len(RAMP)
    rows = []
    for y in range(rows_count):
        line = []
        for x in range(COLS):
            brightness = small.getpixel((x, y))  # 0 dark .. 255 bright
            idx = ramp_len - 1 - int((brightness / 255) * (ramp_len - 1))
            line.append(RAMP[idx])
        rows.append("".join(line))
    return rows


def build_svg(rows: list[str]) -> str:
    width = COLS * CHAR_W
    height = len(rows) * CHAR_H
    row_w_px = COLS * CHAR_W

    parts = []
    for i, row in enumerate(rows):
        y = (i + 1) * CHAR_H - CHAR_H * 0.2
        clip_id = f"clip{i}"
        begin = i * ROW_STAGGER_MS
        parts.append(
            f'''<clipPath id="{clip_id}">
  <rect x="0" y="{i * CHAR_H}" width="0" height="{CHAR_H}">
    <animate id="wipe{i}" attributeName="width" from="0" to="{row_w_px:.1f}" dur="{ROW_DUR_MS}ms" begin="{begin}ms" fill="freeze" calcMode="linear"/>
  </rect>
</clipPath>
<text x="0" y="{y:.1f}" font-family="SFMono-Regular,Consolas,Menlo,monospace" font-size="{FONT_SIZE}" fill="{FILL}" xml:space="preserve" textLength="{row_w_px:.1f}" lengthAdjust="spacingAndGlyphs" clip-path="url(#{clip_id})">{esc(row)}</text>
<rect x="0" y="{i * CHAR_H:.1f}" width="{CHAR_W * 0.8:.1f}" height="{CHAR_H * 0.85:.1f}" fill="{CURSOR_COLOR}">
  <animate attributeName="x" from="0" to="{row_w_px:.1f}" dur="{ROW_DUR_MS}ms" begin="{begin}ms" fill="freeze" calcMode="linear"/>
  <animate attributeName="opacity" values="1;1;0" keyTimes="0;0.85;1" dur="{ROW_DUR_MS}ms" begin="{begin}ms" fill="freeze"/>
</rect>'''
        )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}" viewBox="0 0 {width:.1f} {height:.1f}">
  <rect x="0" y="0" width="{width:.1f}" height="{height:.1f}" fill="{BG}"/>
{chr(10).join(parts)}
</svg>'''


if __name__ == "__main__":
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "source-prepped.png"
    rows = image_to_rows(src)
    out = ROOT / "avi-ascii.svg"
    out.write_text(build_svg(rows))
    print(f"Wrote {out} ({COLS}x{len(rows)} grid)")
