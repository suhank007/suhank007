#!/usr/bin/env python3
"""Animated horizontal bar chart of resume achievements: bars fill from 0
to their value on load, then freeze. Same terminal-panel look as the
other SVGs."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

WIDTH = 860
BG = "#0d1117"
BORDER = "#30363d"
TITLEBAR = "#161b22"
LABEL_COLOR = "#c9d1d9"
TRACK_COLOR = "#161b22"
UP_COLOR = "#39d353"
DOWN_COLOR = "#7dd3fc"

# (label, value_pct, direction "up"|"down")
METRICS = [
    ("Reporting adoption", 50, "up"),
    ("Dashboard utilisation", 60, "up"),
    ("Critical production issues", 40, "down"),
    ("Delivery risk", 30, "down"),
]

TOP_PAD = 50
ROW_H = 46
LABEL_W = 260
BAR_MAX_W = WIDTH - LABEL_W - 100
BAR_H = 14
STAGGER_MS = 160
DUR_MS = 700


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_svg(static: bool) -> str:
    height = TOP_PAD + ROW_H * len(METRICS) + 24
    rows = []
    for i, (label, value, direction) in enumerate(METRICS):
        y = TOP_PAD + i * ROW_H
        bar_w = BAR_MAX_W * (value / 100)
        color = UP_COLOR if direction == "up" else DOWN_COLOR
        arrow = "^" if direction == "up" else "v"
        delay = i * STAGGER_MS
        bar_y = y - BAR_H + 2
        clip_id = f"barclip{i}"
        if static:
            clip_rect = f'<rect x="{LABEL_W}" y="{bar_y}" width="{bar_w:.1f}" height="{BAR_H}"/>'
            text_opacity = ""
        else:
            clip_rect = (
                f'<rect x="{LABEL_W}" y="{bar_y}" width="0" height="{BAR_H}">'
                f'<animate attributeName="width" from="0" to="{bar_w:.1f}" dur="{DUR_MS}ms" begin="{delay}ms" fill="freeze" calcMode="linear"/>'
                f'</rect>'
            )
            text_opacity = f'opacity="0" style="animation: fade-in 300ms ease-out {delay + DUR_MS - 150}ms forwards"'

        rows.append(
            f'''<text x="28" y="{y}" font-family="SFMono-Regular,Consolas,Menlo,monospace" font-size="13" fill="{LABEL_COLOR}">{esc(label)}</text>
<rect x="{LABEL_W}" y="{bar_y}" width="{BAR_MAX_W}" height="{BAR_H}" rx="4" fill="{TRACK_COLOR}"/>
<clipPath id="{clip_id}">{clip_rect}</clipPath>
<rect x="{LABEL_W}" y="{bar_y}" width="{BAR_MAX_W}" height="{BAR_H}" rx="4" fill="{color}" clip-path="url(#{clip_id})"/>
<text x="{LABEL_W + BAR_MAX_W + 14}" y="{y}" font-family="SFMono-Regular,Consolas,Menlo,monospace" font-size="13" font-weight="600" fill="{color}" {text_opacity}>{arrow} {value}%</text>'''
        )

    keyframes = "" if static else """
    @keyframes fade-in {
      from { opacity: 0; }
      to   { opacity: 1; }
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
{chr(10).join(rows)}
</svg>'''


if __name__ == "__main__":
    static = os.environ.get("STATIC") == "1"
    out = ROOT / "impact-metrics.svg"
    out.write_text(build_svg(static))
    print(f"Wrote {out}")
