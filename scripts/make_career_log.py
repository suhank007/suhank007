#!/usr/bin/env python3
"""Animated career timeline SVG: self-typing role rows followed by a
staggered row of client-name chips. Same terminal aesthetic as the info
card and heatmap; all motion via CSS keyframes so GitHub renders it
through <img>."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

WIDTH = 860
BG = "#0d1117"
BORDER = "#30363d"
TITLEBAR = "#161b22"
PERIOD_COLOR = "#7dd3fc"
ORG_COLOR = "#c9d1d9"
ROLE_COLOR = "#8b949e"
ACCENT = "#39d353"
CHIP_BG = "#161b22"
CHIP_TEXT = "#7d8590"

ROLES = [
    ("2026 — Now", "We.PLM x Atlas Copco", "Product Manager, Data Transformation"),
    ("2020 — 2025", "Cognizant", "Product Owner & Senior BI Analytics Consultant"),
    ("2019 — 2020", "Liebherr Aerospace", "Data Analyst Intern"),
    ("2015 — 2018", "Capgemini x Societe Generale", "Business Analyst / Scrum Coordinator"),
]

CLIENTS = [
    "Atlas Copco",
    "Air France",
    "Dior (LVMH)",
    "AXA Insurance",
    "Sanofi",
    "Altares",
    "Advarra",
    "Societe Generale",
]

ROW_H = 40
TOP_PAD = 32
ROW_STAGGER_MS = 130
FADE_MS = 340
CHIP_H = 26
CHIP_GAP = 8
CHIP_PAD_X = 14
CHIP_CHAR_W = 6.6


def esc(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def build_svg(static: bool) -> str:
    rows_top = TOP_PAD + 26
    rows_h = ROW_H * len(ROLES)
    chips_top = rows_top + rows_h + 22

    # Lay out client chips left-to-right, wrapping to a new line.
    max_w = WIDTH - 56
    cx, cy = 0, 0
    chip_rows = []
    for name in CLIENTS:
        w = len(name) * CHIP_CHAR_W + CHIP_PAD_X * 2
        if cx + w > max_w and cx > 0:
            cx = 0
            cy += CHIP_H + CHIP_GAP
        chip_rows.append((name, cx, cy, w))
        cx += w + CHIP_GAP
    chips_h = cy + CHIP_H

    height = chips_top + chips_h + 28

    role_svg = []
    for i, (period, org, role) in enumerate(ROLES):
        y = rows_top + i * ROW_H
        delay = i * ROW_STAGGER_MS
        if static:
            opacity_attr = 'opacity="1"'
            style = ""
        else:
            opacity_attr = 'opacity="0"'
            style = f'style="animation: row-in {FADE_MS}ms ease-out {delay}ms forwards"'
        role_svg.append(
            f'''<g {opacity_attr} {style}>
  <circle cx="32" cy="{y - 5}" r="3.5" fill="{ACCENT}"/>
  <text x="48" y="{y}" font-family="SFMono-Regular,Consolas,Menlo,monospace" font-size="13" fill="{PERIOD_COLOR}" font-weight="600">{esc(period)}</text>
  <text x="190" y="{y}" font-family="SFMono-Regular,Consolas,Menlo,monospace" font-size="13" fill="{ORG_COLOR}" font-weight="600">{esc(org)}</text>
  <text x="470" y="{y}" font-family="SFMono-Regular,Consolas,Menlo,monospace" font-size="12.5" fill="{ROLE_COLOR}">{esc(role)}</text>
</g>'''
        )
        if i < len(ROLES) - 1:
            role_svg.append(
                f'<line x1="32" y1="{y + 8}" x2="32" y2="{y + ROW_H - 8}" stroke="{BORDER}" stroke-width="1.5"/>'
            )

    chip_delay_base = len(ROLES) * ROW_STAGGER_MS + FADE_MS
    chip_svg = []
    for i, (name, cx, cy_, w) in enumerate(chip_rows):
        x = 28 + cx
        y = chips_top + cy_
        delay = chip_delay_base + i * 45
        if static:
            opacity_attr = 'opacity="1"'
            transform_attr = ""
            style = ""
        else:
            opacity_attr = 'opacity="0"'
            transform_attr = 'transform="translate(0,6)"'
            style = f'style="animation: chip-in 260ms ease-out {delay}ms forwards"'
        chip_svg.append(
            f'''<g {opacity_attr} {transform_attr} {style}>
  <rect x="{x}" y="{y}" width="{w:.1f}" height="{CHIP_H}" rx="13" fill="{CHIP_BG}" stroke="{BORDER}"/>
  <text x="{x + w / 2:.1f}" y="{y + 17}" text-anchor="middle" font-family="SFMono-Regular,Consolas,Menlo,monospace" font-size="11" fill="{CHIP_TEXT}">{esc(name)}</text>
</g>'''
        )

    keyframes = "" if static else """
    @keyframes row-in {
      from { opacity: 0; transform: translate(-10px, 0); }
      to   { opacity: 1; transform: translate(0, 0); }
    }
    @keyframes chip-in {
      from { opacity: 0; transform: translate(0, 6px); }
      to   { opacity: 1; transform: translate(0, 0); }
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
{chr(10).join(role_svg)}
  <line x1="28" y1="{chips_top - 14}" x2="{WIDTH - 28}" y2="{chips_top - 14}" stroke="{BORDER}"/>
{chr(10).join(chip_svg)}
</svg>'''


if __name__ == "__main__":
    static = os.environ.get("STATIC") == "1"
    out = ROOT / "career-log.svg"
    out.write_text(build_svg(static))
    print(f"Wrote {out}")
