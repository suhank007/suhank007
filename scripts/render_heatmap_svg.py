#!/usr/bin/env python3
"""Render data/contributions.json as a 53-week x 7-day calendar of rounded,
colored boxes. Reveals once with a diagonal slide-down, then freezes."""
import json
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]

CELL = 11
GAP = 3
LEFT_PAD = 30
TOP_PAD = 20
MONTH_LABEL_H = 16
STAGGER_MS = 4.5


def build_grid(days: list[dict]):
    by_date = {d["date"]: d for d in days}
    if not days:
        return [], None, None

    last = datetime.strptime(days[-1]["date"], "%Y-%m-%d")
    end = last
    start = end - timedelta(weeks=52)
    start -= timedelta(days=start.weekday() + 1 if start.weekday() != 6 else 0)
    start -= timedelta(days=(start.weekday() + 1) % 7)

    weeks = []
    cur = start
    week = []
    while cur <= end:
        rec = by_date.get(cur.strftime("%Y-%m-%d"))
        level = min(rec["level"], 5) if rec else 0
        count = rec["count"] if rec else 0
        week.append({"date": cur, "level": level, "count": count})
        if cur.weekday() == 5:
            weeks.append(week)
            week = []
        cur += timedelta(days=1)
    if week:
        weeks.append(week)

    return weeks, start, end


def month_labels(weeks):
    labels = []
    last_month = None
    for wi, week in enumerate(weeks):
        first_day = week[0]["date"]
        m = first_day.strftime("%b")
        if m != last_month:
            labels.append((wi, m))
            last_month = m
    return labels


def build_svg(data: dict) -> str:
    weeks, start, end = build_grid(data["days"])
    stats = data["stats"]
    width = LEFT_PAD + len(weeks) * (CELL + GAP) + 20
    height = TOP_PAD + MONTH_LABEL_H + 7 * (CELL + GAP) + 46

    cells = []
    idx = 0
    for wi, week in enumerate(weeks):
        for day in week:
            dow = day["date"].weekday()
            row = (dow + 1) % 7
            x = LEFT_PAD + wi * (CELL + GAP)
            y = TOP_PAD + MONTH_LABEL_H + row * (CELL + GAP)
            color = PALETTE[day["level"]]
            delay = idx * STAGGER_MS
            cells.append(
                f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" '
                f'fill="{color}" opacity="0" style="animation: box-in 260ms ease-out {delay:.1f}ms forwards">'
                f'<title>{day["count"]} contributions on {day["date"].strftime("%b %d, %Y")}</title></rect>'
            )
            idx += 1

    labels = month_labels(weeks)
    label_svg = [
        f'<text x="{LEFT_PAD + wi * (CELL + GAP)}" y="{TOP_PAD + 10}" '
        f'font-family="SFMono-Regular,Consolas,Menlo,monospace" font-size="10" fill="#7d8590">{m}</text>'
        for wi, m in labels
    ]

    dow_labels = {1: "Mon", 3: "Wed", 5: "Fri"}
    dow_svg = [
        f'<text x="4" y="{TOP_PAD + MONTH_LABEL_H + row * (CELL + GAP) + 9}" '
        f'font-family="SFMono-Regular,Consolas,Menlo,monospace" font-size="9" fill="#7d8590">{label}</text>'
        for row, label in dow_labels.items()
    ]

    legend_y = height - 22
    legend_x = width - 20 - len(PALETTE) * (CELL + 2) - 60
    legend_boxes = [
        f'<rect x="{legend_x + 40 + i * (CELL + 2)}" y="{legend_y}" width="{CELL}" height="{CELL}" rx="2.5" fill="{c}"/>'
        for i, c in enumerate(PALETTE)
    ]

    footer = f"{stats['total']:,} contributions in the last year"
    if stats.get("current_streak", 0) > 0:
        footer += f"  ·  current streak {stats['current_streak']}d"
    if stats.get("longest_streak", 0) > 0:
        footer += f"  ·  longest streak {stats['longest_streak']}d"

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <style>
    @keyframes box-in {{
      from {{ opacity: 0; transform: translate(-6px, -6px); }}
      to   {{ opacity: 1; transform: translate(0, 0); }}
    }}
    rect {{ transform-box: fill-box; transform-origin: center; }}
  </style>
  <rect x="0" y="0" width="{width}" height="{height}" rx="10" fill="#0d1117"/>
{chr(10).join(label_svg)}
{chr(10).join(dow_svg)}
{chr(10).join(cells)}
  <text x="{LEFT_PAD}" y="{height - 26}" font-family="SFMono-Regular,Consolas,Menlo,monospace" font-size="11" fill="#7d8590">{footer}</text>
  <text x="{legend_x}" y="{legend_y + 9}" font-family="SFMono-Regular,Consolas,Menlo,monospace" font-size="9" fill="#7d8590">Less</text>
{chr(10).join(legend_boxes)}
  <text x="{legend_x + 40 + len(PALETTE) * (CELL + 2) + 6}" y="{legend_y + 9}" font-family="SFMono-Regular,Consolas,Menlo,monospace" font-size="9" fill="#7d8590">More</text>
</svg>'''


if __name__ == "__main__":
    data = json.loads((ROOT / "data" / "contributions.json").read_text())
    out = ROOT / "contrib-heatmap.svg"
    out.write_text(build_svg(data))
    print(f"Wrote {out}")
