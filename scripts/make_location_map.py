#!/usr/bin/env python3
"""Location/availability panel: a stylized world map (simplified from the
MIT-licensed svg-maps/world dataset, see scripts/icon_cache/world_map.json)
with a "home" pin and pulsing markers on a few hub regions, connected by
flight-path arcs, signalling openness to relocate / work from anywhere.
Same terminal-panel look as the other generated SVGs."""
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / "scripts" / "icon_cache" / "world_map.json").read_text())

WIDTH = 860
BG = "#0d1117"
BORDER = "#30363d"
TITLEBAR = "#161b22"
LAND_FILL = "#1c232c"
LAND_STROKE = "#30363d"
HOME_COLOR = "#39d353"
PIN_COLOR = "#7dd3fc"
ARC_COLOR = "#7dd3fc"
TEXT_DIM = "#8b949e"
TEXT_MAIN = "#c9d1d9"

VB_W, VB_H = DATA["viewbox"][2], DATA["viewbox"][3]
CONTENT_W = WIDTH - 56
CONTENT_H = CONTENT_W * VB_H / VB_W
TOP_PAD = 46
SCALE = CONTENT_W / VB_W

HOME_KEY = "France"
HUB_KEYS = ["United States", "United Kingdom", "United Arab Emirates", "India", "Singapore", "Australia", "Brazil"]


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_svg(static: bool) -> str:
    home = DATA["markers"][HOME_KEY]
    hubs = [DATA["markers"][k] for k in HUB_KEYS]

    map_top = TOP_PAD
    map_bottom = map_top + CONTENT_H
    caption_y = map_bottom + 34
    height = caption_y + 24

    # arcs: quadratic bezier from home to each hub, control point bowed
    # outward (toward the top) for a "flight path" feel
    arc_parts = []
    for i, hub in enumerate(hubs):
        x1, y1 = home["cx"], home["cy"]
        x2, y2 = hub["cx"], hub["cy"]
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2 - abs(x2 - x1) * 0.12 - 20
        dpath = f"M{x1:.1f},{y1:.1f} Q{mx:.1f},{my:.1f} {x2:.1f},{y2:.1f}"
        # approx length for dash animation
        length = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5 * 1.15
        delay = 500 + i * 160
        if static:
            dash_style = ""
        else:
            dash_style = (
                f'stroke-dasharray="{length:.0f}" stroke-dashoffset="{length:.0f}" '
                f'style="animation: draw-arc 900ms ease-out {delay}ms forwards"'
            )
        arc_parts.append(
            f'<path d="{dpath}" fill="none" stroke="{ARC_COLOR}" stroke-width="1" opacity="0.45" {dash_style}/>'
        )

    def pin(mk, color, radius, label, delay, pulse):
        cx, cy = mk["cx"], mk["cy"]
        inv = 1 / SCALE
        ring = ""
        if pulse and not static:
            ring = (
                f'<circle r="{radius}" fill="none" stroke="{color}" stroke-width="1.5" opacity="0">'
                f'<animate attributeName="r" from="{radius}" to="{radius*3.2}" dur="1800ms" begin="{delay}ms" repeatCount="indefinite"/>'
                f'<animate attributeName="opacity" values="0.55;0" dur="1800ms" begin="{delay}ms" repeatCount="indefinite"/>'
                f'</circle>'
            )
        dot_opacity = 'opacity="1"' if static else 'opacity="0"'
        dot_style = "" if static else f'style="animation: pin-in 300ms ease-out {delay}ms forwards"'
        label_svg = ""
        if label:
            label_svg = (
                f'<text x="{radius + 5}" y="3.5" font-family="SFMono-Regular,Consolas,Menlo,monospace" '
                f'font-size="10.5" fill="{TEXT_MAIN}" font-weight="600">{esc(label)}</text>'
            )
        return f'''<g transform="translate({cx:.1f},{cy:.1f})">
  <g transform="scale({inv:.4f})" {dot_opacity} {dot_style}>
    {ring}
    <circle r="{radius}" fill="{color}"/>
    {label_svg}
  </g>
</g>'''

    home_pin = pin(home, HOME_COLOR, 4.5, "Paris — home", 200, pulse=True)
    hub_pins = "".join(
        pin(hub, PIN_COLOR, 3.5, None, 900 + i * 160, pulse=True)
        for i, hub in enumerate(hubs)
    )

    map_group = f'''<g transform="translate(28,{map_top}) scale({SCALE:.5f})">
  <path d="{DATA['world_d']}" fill="{LAND_FILL}" stroke="{LAND_STROKE}" stroke-width="0.6"/>
  {"".join(arc_parts)}
  {home_pin}
  {hub_pins}
</g>'''

    keyframes = "" if static else """
    @keyframes pin-in {
      from { opacity: 0; }
      to   { opacity: 1; }
    }
    @keyframes draw-arc {
      to { stroke-dashoffset: 0; }
    }
    @keyframes caption-in {
      from { opacity: 0; transform: translate(0,4px); }
      to   { opacity: 1; transform: translate(0,0); }
    }
    """

    caption_delay = 900 + len(hubs) * 160 + 300
    caption_opacity = 'opacity="1"' if static else 'opacity="0"'
    caption_style = "" if static else f'style="animation: caption-in 400ms ease-out {caption_delay}ms forwards"'

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height:.0f}" viewBox="0 0 {WIDTH} {height:.1f}">
  <style>{keyframes}</style>
  <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{height - 1:.1f}" rx="10" fill="{BG}" stroke="{BORDER}"/>
  <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="34" rx="10" fill="{TITLEBAR}"/>
  <rect x="0.5" y="24.5" width="{WIDTH - 1}" height="10" fill="{TITLEBAR}"/>
  <line x1="0.5" y1="34.5" x2="{WIDTH - 0.5}" y2="34.5" stroke="{BORDER}"/>
  <circle cx="24" cy="17" r="6" fill="#ff5f56"/>
  <circle cx="44" cy="17" r="6" fill="#ffbd2e"/>
  <circle cx="64" cy="17" r="6" fill="#27c93f"/>
  <text x="{WIDTH/2:.1f}" y="22" text-anchor="middle" font-family="SFMono-Regular,Consolas,Menlo,monospace" font-size="12" fill="#7d8590">~/location --available</text>
{map_group}
  <g {caption_opacity} {caption_style}>
    <text x="{WIDTH/2:.1f}" y="{caption_y:.1f}" text-anchor="middle" font-family="SFMono-Regular,Consolas,Menlo,monospace" font-size="13" fill="{TEXT_MAIN}" font-weight="600">Based in Paris — open to relocate &amp; remote work, anywhere</text>
  </g>
</svg>'''


if __name__ == "__main__":
    static = os.environ.get("STATIC") == "1"
    out = ROOT / "location-map.svg"
    out.write_text(build_svg(static))
    print(f"Wrote {out}")
