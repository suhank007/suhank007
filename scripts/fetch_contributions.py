#!/usr/bin/env python3
"""Fetch the public contribution calendar HTML fragment (no token needed)
and write data/contributions.json with raw days plus derived stats."""
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
USERNAME = "suhank007"
URL = f"https://github.com/users/{USERNAME}/contributions"


def fetch(username: str) -> dict:
    resp = requests.get(
        f"https://github.com/users/{username}/contributions",
        headers={"User-Agent": "Mozilla/5.0 (profile-readme-bot)"},
        timeout=20,
    )
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # Count lives in a sibling <tool-tip for="<td-id>">N contributions on
    # <date>.</tool-tip>, not on the <td> itself.
    tooltips_by_for = {
        tt.get("for"): tt.get_text(strip=True)
        for tt in soup.find_all("tool-tip")
        if tt.get("for")
    }

    days = []
    cells = soup.select("td.ContributionCalendar-day")
    for cell in cells:
        date = cell.get("data-date")
        level = cell.get("data-level")
        if date is None:
            continue
        tooltip_text = tooltips_by_for.get(cell.get("id"), "")
        count = _parse_count(tooltip_text)
        days.append(
            {
                "date": date,
                "count": count,
                "level": int(level) if level is not None else _level_from_count(count),
            }
        )

    days.sort(key=lambda d: d["date"])
    return {"username": username, "days": days}


def _parse_count(text: str) -> int:
    text = text.strip()
    if text.lower().startswith("no contributions"):
        return 0
    parts = text.split()
    for p in parts:
        if p.isdigit():
            return int(p)
    return 0


def _level_from_count(count: int) -> int:
    if count is None or count == 0:
        return 0
    if count < 3:
        return 1
    if count < 6:
        return 2
    if count < 10:
        return 3
    return 4


def derive_stats(days: list[dict]) -> dict:
    total = sum(d["count"] for d in days)
    current_streak = 0
    longest_streak = 0
    running = 0
    for d in days:
        if d["count"] > 0:
            running += 1
            longest_streak = max(longest_streak, running)
        else:
            running = 0
    for d in reversed(days):
        if d["count"] > 0:
            current_streak += 1
        else:
            break

    best_day = max(days, key=lambda d: d["count"], default=None)

    monthly = defaultdict(int)
    for d in days:
        month = d["date"][:7]
        monthly[month] += d["count"]

    return {
        "total": total,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best_day,
        "monthly": dict(sorted(monthly.items())),
    }


if __name__ == "__main__":
    username = sys.argv[1] if len(sys.argv) > 1 else USERNAME
    data = fetch(username)
    data["stats"] = derive_stats(data["days"])
    data["generated_at"] = datetime.now(timezone.utc).isoformat()

    out = ROOT / "data" / "contributions.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(data, indent=2))
    print(f"Wrote {out} ({len(data['days'])} days, {data['stats']['total']} total)")
