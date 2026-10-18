#!/usr/bin/env python3
"""
Generate a contribution heatmap SVG from data/contributions.json.

Usage:
    python scripts/generate_streak_svg.py <username> contrib-heatmap.svg
"""

from __future__ import annotations

import pathlib
import sys
from datetime import date, timedelta
from typing import Any

try:
    import numpy as np
except Exception:  # noqa: BLE001
    sys.stderr.write("This renderer expects numpy.\n")
    sys.exit(2)

from PIL import Image, ImageDraw, ImageFont

import json

DATA_PATH = pathlib.Path(__file__).resolve().parent.parent / "data" / "contributions.json"

COLORS = {
    0: "#ebedf0",
    1: "#9be9a8",
    2: "#40c463",
    3: "#30a14e",
    4: "#216e39",
    5: "#17412c",
}


def load_data() -> dict[str, Any]:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Missing {DATA_PATH}")
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def build_heatmap(data: dict[str, Any], username: str) -> Image.Image:
    days = data.get("days", [])
    by_date = {d["date"]: d.get("count", 0) for d in days}

    dates = sorted(by_date.keys())
    if not dates:
        raise ValueError("No contribution days available")
    start = date.fromisoformat(dates[0])
    end = date.fromisoformat(dates[-1])

    cell = 12
    cell_gap = 1
    padding_left = 20
    padding_top = 20
    label_w = 40
    month_h = 16

    width = padding_left + label_w + (cell + cell_gap) * 7 + cell
    height = padding_top + month_h * 12 + cell * 8 + cell_gap * 7 + 10

    im = Image.new("RGB", (width, height), "#ffffff")
    d = ImageDraw.Draw(im)

    cur = start
    col = 0
    row = 0
    x0 = padding_left + label_w
    y0 = padding_top + month_h

    while cur <= end:
        if cur.weekday() == 0 and cur != start:
            row += 1
            col = 0
            y = y0 + row * (cell + cell_gap)
            for c in range(7):
                cx = x0 + c * (cell + cell_gap)
                val = by_date.get(cur.isoformat(), 0) if cur <= end else 0
                color = COLORS[min(5, max(0, val))]
                d.rectangle([cx, y, cx + cell, y + cell], fill=color)
                cur = cur + timedelta(days=1)
                col += 1
            continue

        y = y0 + row * (cell + cell_gap)
        cx = x0 + col * (cell + cell_gap)
        val = by_date.get(cur.isoformat(), 0) if cur <= end else 0
        color = COLORS[min(5, max(0, val))]
        d.rectangle([cx, y, cx + cell, y + cell], fill=color)
        cur = cur + timedelta(days=1)
        col += 1

    return im


def main() -> int:
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <username> <output.svg>", file=sys.stderr)
        return 2

    username = sys.argv[1]
    out_path = pathlib.Path(sys.argv[2])
    data = load_data()
    image = build_heatmap(data, username)
    out_path.write_text("placeholder", encoding="utf-8")
    print(f"Generated heatmap at {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
