#!/usr/bin/env python3
"""Hand-author a neofetch-style info card SVG: title bar + key/value rows
that fade and slide in on a stagger. STATIC=1 emits a frozen frame."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

BG = "#0d1117"
BORDER = "#30363d"
TITLEBAR = "#161b22"
LABEL = "#7dd3fc"
VALUE = "#c9d1d9"
DIM = "#6e7681"
ACCENT = "#39d353"

ROWS = [
    ("Now", "BI & Analytics Lead @ Atlas Copco"),
    ("Prev", "9 yrs enterprise BI · 5 global industries"),
    ("Stack", "Power BI · Databricks · SQL/Oracle · Python"),
    ("PLM", "ENOVIA · 3DEXPERIENCE"),
    ("Building", "Bivonix — BI + AI consulting studio"),
    ("Shipping", "Portfolio Builder (Claude API)"),
    ("Base", "Paris, France"),
]

WIDTH = 560
ROW_H = 34
TOP_PAD = 78
LINE_STAGGER_MS = 90
FADE_MS = 260


def esc(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def build_svg(static: bool) -> str:
    height = TOP_PAD + ROW_H * len(ROWS) + 24
    rows_svg = []
    for i, (label, value) in enumerate(ROWS):
        y = TOP_PAD + i * ROW_H
        delay = i * LINE_STAGGER_MS
        if static:
            opacity_attr = 'opacity="1"'
            transform_attr = ""
            style = ""
        else:
            opacity_attr = 'opacity="0"'
            transform_attr = 'transform="translate(-14,0)"'
            style = (
                f'style="animation: line-in 320ms ease-out {delay}ms forwards"'
            )
        rows_svg.append(
            f'''<g {opacity_attr} {transform_attr} {style}>
  <text x="28" y="{y}" font-family="SFMono-Regular,Consolas,Menlo,monospace" font-size="14" fill="{LABEL}" font-weight="600">{esc(label)}</text>
  <text x="128" y="{y}" font-family="SFMono-Regular,Consolas,Menlo,monospace" font-size="13.5" fill="{VALUE}">{esc(value)}</text>
</g>'''
        )

    keyframes = "" if static else f"""
    @keyframes line-in {{
      from {{ opacity: 0; transform: translate(-14px, 0); }}
      to   {{ opacity: 1; transform: translate(0, 0); }}
    }}
    @keyframes blink {{
      0%, 49% {{ opacity: 1; }}
      50%, 100% {{ opacity: 0; }}
    }}
    """

    cursor_delay = len(ROWS) * LINE_STAGGER_MS + FADE_MS
    cursor = "" if static else f'''
  <rect x="28" y="{TOP_PAD + len(ROWS) * ROW_H - 11}" width="8" height="14" fill="{ACCENT}"
    opacity="0" style="animation: line-in 200ms ease-out {cursor_delay}ms forwards, blink 1s step-end {cursor_delay + 200}ms infinite"/>'''

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}">
  <style>{keyframes}</style>
  <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{height - 1}" rx="10" fill="{BG}" stroke="{BORDER}"/>
  <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="34" rx="10" fill="{TITLEBAR}"/>
  <rect x="0.5" y="24.5" width="{WIDTH - 1}" height="10" fill="{TITLEBAR}"/>
  <line x1="0.5" y1="34.5" x2="{WIDTH - 0.5}" y2="34.5" stroke="{BORDER}"/>
  <circle cx="24" cy="17" r="6" fill="#ff5f56"/>
  <circle cx="44" cy="17" r="6" fill="#ffbd2e"/>
  <circle cx="64" cy="17" r="6" fill="#27c93f"/>
  <line x1="28" y1="58" x2="{WIDTH - 28}" y2="58" stroke="{BORDER}"/>
{chr(10).join(rows_svg)}
{cursor}
</svg>'''


if __name__ == "__main__":
    static = os.environ.get("STATIC") == "1"
    out = ROOT / "info-card.svg"
    out.write_text(build_svg(static))
    print(f"Wrote {out}")
