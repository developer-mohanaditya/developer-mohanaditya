#!/usr/bin/env python3
"""Render the streak / numbers card from data/contributions.json (written daily by fetch_contributions.py) as a terminal-window SVG that sits beside ascii-art.gif. The canvas matches the portrait ratio (840 x 1125, i.e. 640:857) so the two panels line up at equal heights when the README shows them side by side at equal widths."""
import datetime
import json
import os
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "data", "contributions.json")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "stats.svg")
BG = "#0d1117"
BG2 = "#111722"
TILE = "#161b22"
FRAME = "#30363d"
MUTED = "#7d8590"
INK = "#e6edf3"
GREEN = "#39d353"
BAR = "#26a641"
W, H = 840, 1125
PAD = 20
TITLEBAR_H = 30
COLS, ROWS = 2, 3
GAP = 16
TILE_W = (W - PAD * 2 - GAP * (COLS - 1)) / COLS
TILE_H = 185
TILES_TOP = TITLEBAR_H + PAD + 4
CHART_TOP = TILES_TOP + ROWS * TILE_H + (ROWS - 1) * GAP + GAP
TILE_STAGGER = 0.15
SLIDE_DUR = 0.45
COUNT_DUR = 1.2
FRAMES = 16
BAR_START = TILE_STAGGER * COLS * ROWS + 0.4
BAR_STAGGER = 0.06
BAR_DUR = 0.6

def short(d):
    return datetime.date.fromisoformat(d).strftime("%b %-d")

def span(s):
    return f'{short(s["start"])} - {short(s["end"])}' if s["length"] else "-"

data = json.load(open(SRC))
cur, lng, best = data["current_streak"], data["longest_streak"], data["best_day"]
n_days = len(data["days"])
tiles = [("current streak", cur["length"], " days", span(cur), GREEN), ("longest streak", lng["length"], " days", span(lng), INK), ("contributions", data["total_contributions"], "", "in the last year", INK), ("active days", data["active_days"], f" / {n_days}", f'{data["active_days"] / n_days:.0%} of the year', INK), ("best day", best["count"], "", short(best["date"]), INK), ("avg / active day", data["avg_per_active_day"], "", "contributions", INK)]

def fmt(v, like):
    return f"{v:,.1f}" if isinstance(like, float) else f"{int(round(v)):,}"
