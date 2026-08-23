#!/usr/bin/env python3
"""Education + publication panel: self-typing rows, same terminal
aesthetic as the info card and career log."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

WIDTH = 860
BG = "#0d1117"
BORDER = "#30363d"
TITLEBAR = "#161b22"
LABEL_COLOR = "#7dd3fc"
VALUE_COLOR = "#c9d1d9"
DIM_COLOR = "#8b949e"
ACCENT = "#39d353"

ROWS = [
    (
        "M.Sc.",
        "Big Data, Marketing & Management",
        "Toulouse Business School, France - 2018-2020 - Distinction (summa cum laude, 3.8)",
    ),
    (
        "B.Tech.",
        "Electronics & Telecommunication Engineering",
        "Lovely Professional University, India - 2010-2014",
    ),
    (
        "Paper",
        '"Hourly Investigations of the 2019 Heatwave in France" (2020)',
        "Research study analyzing meteorological data patterns and their socioeconomic impacts",
    ),
]

TOP_PAD = 34
ROW_H = 58
ROW_STAGGER_MS = 180
FADE_MS = 360


def esc(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def build_svg(static: bool) -> str:
    height = TOP_PAD + ROW_H * len(ROWS) + 20

    rows_svg = []
    for i, (tag, title, detail) in enumerate(ROWS):
        y = TOP_PAD + i * ROW_H
        delay = i * ROW_STAGGER_MS
        if static:
            opacity_attr = 'opacity="1"'
            style = ""
        else:
            opacity_attr = 'opacity="0"'
            style = f'style="animation: row-in {FADE_MS}ms ease-out {delay}ms forwards"'
        rows_svg.append(
            f'''<g {opacity_attr} {style}>
  <circle cx="32" cy="{y - 4}" r="3.5" fill="{ACCENT}"/>
  <text x="48" y="{y}" font-family="SFMono-Regular,Consolas,Menlo,monospace" font-size="12.5" fill="{LABEL_COLOR}" font-weight="600">{esc(tag)}</text>
  <text x="130" y="{y}" font-family="SFMono-Regular,Consolas,Menlo,monospace" font-size="13" fill="{VALUE_COLOR}" font-weight="600">{esc(title)}</text>
  <text x="130" y="{y + 20}" font-family="SFMono-Regular,Consolas,Menlo,monospace" font-size="11.5" fill="{DIM_COLOR}">{esc(detail)}</text>
</g>'''
        )
        if i < len(ROWS) - 1:
            rows_svg.append(
                f'<line x1="32" y1="{y + 10}" x2="32" y2="{y + ROW_H - 6}" stroke="{BORDER}" stroke-width="1.5"/>'
            )

    keyframes = "" if static else """
    @keyframes row-in {
      from { opacity: 0; transform: translate(-10px, 0); }
      to   { opacity: 1; transform: translate(0, 0); }
    }
    """

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}">
  <style>{keyframes}</style>
  <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{height - 1}" rx="10" fill="{BG}" stroke="{BORDER}"/>
  <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="34" rx="10" fill="{TITLEBAR}"/>
  <rect x="0.5" y="24.5" width="{WIDTH - 1}" height="10" fill="{TITLEBAR}"/>
  <line x1="0.5" y1="34.5" x2="{WIDTH - 0.5}" y2="34.5" stroke="{BORDER}"/>
  <circle cx="24" cy="17" r="6" fill="#ff5f56"/>
  <circle cx="44" cy="17" r="6" fill="#ffbd2e"/>
  <circle cx="64" cy="17" r="6" fill="#27c93f"/>
{chr(10).join(rows_svg)}
</svg>'''


if __name__ == "__main__":
    static = os.environ.get("STATIC") == "1"
    out = ROOT / "education.svg"
    out.write_text(build_svg(static))
    print(f"Wrote {out}")
