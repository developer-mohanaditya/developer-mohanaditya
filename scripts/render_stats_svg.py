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
