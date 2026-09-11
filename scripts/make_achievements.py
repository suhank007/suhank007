#!/usr/bin/env python3
"""Achievements strip: a grid of stat badges (icon + headline number +
label) surfacing the standout facts otherwise buried in the career log,
impact metrics and education panels. Same terminal-panel look, staggered
scale/fade-in on load."""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from icon_lib import _load  # noqa: E402

WIDTH = 860
BG = "#0d1117"
BORDER = "#30363d"
TITLEBAR = "#161b22"
CARD_BG = "#11161d"
STAT_COLOR = "#e6edf3"
LABEL_COLOR = "#8b949e"
ACCENT = "#39d353"
CYAN = "#7dd3fc"

# (lucide icon key, icon color, stat, [label lines])
BADGES = [
    ("award", CYAN, "7+ yrs", ["BI & data product", "leadership"]),
    ("trending-up", ACCENT, "+60%", ["Dashboard", "utilisation"]),
    ("trending-down", ACCENT, "−40%", ["Critical production", "issues"]),
    ("graduation-cap", CYAN, "Distinction", ["M.Sc., Toulouse", "Business School"]),
    ("badge-check", CYAN, "3x Certified", ["PL-300 · Databricks GenAI", "SAFe POPM"]),
    ("building-2", CYAN, "8 enterprise", ["clients across 6", "industries"]),
]

COLS = 3
GAP = 14
TOP_PAD = 26
CARD_W = (WIDTH - 56 - GAP * (COLS - 1)) / COLS
CARD_H = 92
ICON_BOX = 34
STAGGER_MS = 90
DUR_MS = 360


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_svg(static: bool) -> str:
    rows = (len(BADGES) + COLS - 1) // COLS
    height = TOP_PAD + rows * CARD_H + (rows - 1) * GAP + 24

    cards = []
    for i, (icon_key, icon_color, stat, label_lines) in enumerate(BADGES):
        col = i % COLS
        row = i // COLS
        x = 28 + col * (CARD_W + GAP)
        y = TOP_PAD + row * (CARD_H + GAP)
        delay = i * STAGGER_MS

        if static:
            opacity_attr = 'opacity="1"'
            transform_attr = ""
            style = ""
        else:
            opacity_attr = 'opacity="0"'
            transform_attr = 'transform="translate(0,10) scale(0.97)"'
            style = f'style="animation: card-in {DUR_MS}ms cubic-bezier(.2,.7,.3,1) {delay}ms forwards"'

        icon_cx = x + 18 + ICON_BOX / 2
        icon_cy = y + 18 + ICON_BOX / 2
        inner = _load(icon_key, "stroke")
        icon_svg = (
            f'<g transform="translate({icon_cx - 8:.1f},{icon_cy - 8:.1f}) scale({16/24:.4f})" '
            f'fill="none" stroke="{icon_color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{inner}</g>'
        )

        label_svg = "".join(
            f'<text x="{x + 18}" y="{y + 56 + li * 15}" font-family="SFMono-Regular,Consolas,Menlo,monospace" font-size="11" fill="{LABEL_COLOR}">{esc(line)}</text>'
            for li, line in enumerate(label_lines)
        )

        cards.append(
            f'''<g {opacity_attr} {transform_attr} {style}>
  <rect x="{x:.1f}" y="{y:.1f}" width="{CARD_W:.1f}" height="{CARD_H}" rx="10" fill="{CARD_BG}" stroke="{BORDER}"/>
  <circle cx="{icon_cx:.1f}" cy="{icon_cy:.1f}" r="{ICON_BOX/2}" fill="{TITLEBAR}" stroke="{BORDER}"/>
  {icon_svg}
  <text x="{x + 18 + ICON_BOX + 10:.1f}" y="{y + 30}" font-family="SFMono-Regular,Consolas,Menlo,monospace" font-size="17" font-weight="700" fill="{STAT_COLOR}">{esc(stat)}</text>
  {label_svg}
</g>'''
        )

    keyframes = "" if static else """
    @keyframes card-in {
      from { opacity: 0; transform: translate(0,10px) scale(0.97); }
      to   { opacity: 1; transform: translate(0,0) scale(1); }
    }
    """

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height:.0f}" viewBox="0 0 {WIDTH} {height:.1f}">
  <style>{keyframes}</style>
  <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{height - 1:.1f}" rx="10" fill="{BG}" stroke="{BORDER}"/>
  <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="34" rx="10" fill="{TITLEBAR}"/>
  <rect x="0.5" y="24.5" width="{WIDTH - 1}" height="10" fill="{TITLEBAR}"/>
  <line x1="0.5" y1="34.5" x2="{WIDTH - 0.5}" y2="34.5" stroke="{BORDER}"/>
  <circle cx="24" cy="17" r="6" fill="#ff5f56"/>
  <circle cx="44" cy="17" r="6" fill="#ffbd2e"/>
  <circle cx="64" cy="17" r="6" fill="#27c93f"/>
  <text x="{WIDTH/2:.1f}" y="22" text-anchor="middle" font-family="SFMono-Regular,Consolas,Menlo,monospace" font-size="12" fill="#7d8590">~/achievements</text>
{chr(10).join(cards)}
</svg>'''


if __name__ == "__main__":
    static = os.environ.get("STATIC") == "1"
    out = ROOT / "achievements.svg"
    out.write_text(build_svg(static))
    print(f"Wrote {out}")
