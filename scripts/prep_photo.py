#!/usr/bin/env python3
"""Prepare portrait for ASCII conversion (Pillow-only, no rembg needed).
Preserves source aspect ratio (e.g. 3:4 portrait) -- no square crop.
Usage: python scripts/prep_photo.py [input] [output].
Default input: source-photo.jpg (repo root).
Default output: source-prepped.png (gitignored, local preview only)."""
import os
import sys
from PIL import Image, ImageEnhance, ImageOps
from PIL.ImageOps import exif_transpose
HERE = os.path.dirname(os.path.abspath(__file__))
INP = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "source-photo.jpg")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "source-prepped.png")
im = Image.open(INP)
try:
    im = exif_transpose(im)
except Exception:
    pass
im = im.convert("RGB")
w, h = im.size
# Keep full frame -- only downscale so longest side is 1024, preserve 3:4.
scale = min(1.0, 1024 / max(w, h))
if scale < 1.0:
    im = im.resize((round(w * scale), round(h * scale)), Image.LANCZOS)
gray = ImageOps.grayscale(im)
gray = ImageEnhance.Contrast(gray).enhance(1.25)
gray = ImageEnhance.Brightness(gray).enhance(1.05)
gray.save(OUT)
print(f"wrote {OUT} {gray.size} (src {w}x{h}, aspect {h/w:.3f})")
