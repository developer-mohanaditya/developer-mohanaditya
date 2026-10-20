#!/usr/bin/env python3
"""
Prepare portrait for ASCII conversion (Pillow-only, no rembg needed).

  python scripts/prep_photo.py [input] [output]

Default input: assets/source-photo.jpg
Default output: source-prepped.png (repo root, gitignored, for local preview)

Steps: square center-crop -> grayscale -> contrast stretch -> save.
make_ascii_svg.py can also read the JPG directly, so this is optional
but improves legibility for busy backgrounds.
"""
import os
import sys
from PIL import Image, ImageEnhance, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
INP = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "assets", "source-photo.jpg")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "source-prepped.png")

im = Image.open(INP).convert("RGB")
# center square crop
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
