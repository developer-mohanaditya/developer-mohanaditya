#!/usr/bin/env python3
"""
Render a contribution stats card SVG from data/contributions.json.

Output is written to stats.svg next to this script by default.
"""

from __future__ import annotations

import pathlib
import sys
from datetime import date

import json

DATA_PATH = pathlib.Path(__file__).resolve().parent.parent / "data" / "contributions.json"
OUT_PATH = pathlib.Path(__file__).resolve().parent.parent / "stats.svg"


def load_data() -> dict[str, Any]:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Missing {DATA_PATH}")
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def svg_text(x: int, y: int, text: str, size: int = 14, fill: str = "#1f2328") -> str:
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-family="Helvetica, Arial, sans-serif">{text}</text>'


def render_card(data: dict[str, Any]) -> str:
    summary = data.get("summary", {})
    total = summary.get("total", 0)
    active = summary.get("active_days", 0)
    current = summary.get("current_streak", 0)
    longest = summary.get("longest_streak", 0)
    best = summary.get("best_day", 0)
    monthly = summary.get("monthly", {})

    tiles = [
        ("Contributions", f"{total}", "#0e4429"),
        ("Active Days", f"{active}", "#0e4429"),
        ("Current Streak", f"{current} days", "#0e4429"),
        ("Longest Streak", f"{longest} days", "#0e4429"),
        ("Best Day", f"{best}", "#0e4429"),
    ]

    tile_w = 120
    tile_h = 60
    gap = 10
    width = len(tiles) * tile_w + (len(tiles) - 1) * gap
    height = 140

    parts = []
    parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">')
    for i, (label, value, accent) in enumerate(tiles):
        x = i * (tile_w + gap)
        y = 10
        parts.append(f'<rect x="{x}" y="{y}" width="{tile_w}" height="{tile_h}" rx="8" fill="#f6f8fa" stroke="#d0d7de"/>')
        parts.append(svg_text(x + 10, y + 22, label, size=11, fill="#656d76"))
        parts.append(svg_text(x + 10, y + 44, value, size=18, fill=accent))
    parts.append(svg_text(10, height - 12, f"Last updated: {summary.get('updated_at', 'unknown')}", size=10, fill="#656d76"))
    parts.append("</svg>")
    return "\n".join(parts)


def main() -> int:
    data = load_data()
    svg = render_card(data)
    OUT_PATH.write_text(svg, encoding="utf-8")
    print(f"Wrote {OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
