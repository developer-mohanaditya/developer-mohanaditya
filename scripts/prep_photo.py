#!/usr/bin/env python3
"""Prepare portrait for ASCII conversion (Pillow-only, no rembg needed). Usage: python scripts/prep_photo.py [input] [output]. Default input: source-photo.jpg (repo root). Default output: source-prepped.png (gitignored, local preview only). Steps: square center-crop -> grayscale -> contrast stretch -> save."""
import os
import sys
from PIL import Image, ImageEnhance, ImageOps
HERE = os.path.dirname(os.path.abspath(__file__))
INP = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "source-photo.jpg")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "source-prepped.png")
im = Image.open(INP).convert("RGB")
w, h = im.size
side = min(w, h)
left = (w - side) // 2
top = (h - side) // 2
im = im.crop((left, top, left + side, top + side))
im = im.resize((1024, 1024), Image.LANCZOS)
gray = ImageOps.grayscale(im)
gray = ImageEnhance.Contrast(gray).enhance(1.25)
gray = ImageEnhance.Brightness(gray).enhance(1.05)
gray.save(OUT)
print(f"wrote {OUT} {gray.size}")
