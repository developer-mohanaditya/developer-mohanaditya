#!/usr/bin/env python3
r"""Build a GitHub-profile avatar SVG for developer-mohanaditya.

Input:
  assets/source-photo.jpg  (photo you attached)

Output:
  assets/avatar.svg
  assets/avatar.png

I’m generating a clean, circular, GitHub-friendly portrait SVG, not ASCII art.
The image is processed in Python and then rasterized into an inline PNG inside the SVG
so the README renders consistently across GitHub light/dark themes.

Preprocessing choice:
- Detect the face region with OpenCV Haar cascades when available.
- If OpenCV is unavailable or face detection fails, fall back to a centered crop.
- Then produce a round portrait crop, subtle contrast normalization, and a refined border.

Dependencies:
  Pillow (already available here)
  opencv-python-headless only if you want face-aware cropping
"""

from __future__ import annotations

import base64
import io
import math
import pathlib
import textwrap
import urllib.parse
from typing import Optional, Tuple

try:
    import cv2
    from cv2 import cvtColor, COLOR_RGB2GRAY, equalizeHist
    _HAS_CV2 = True
except Exception:  # noqa: BLE001
    _HAS_CV2 = False

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps

WORKSPACE = pathlib.Path(__file__).resolve().parent
SOURCE_PATH = WORKSPACE / "assets" / "source-photo.jpg"
OUT_PATH = WORKSPACE / "assets" / "avatar.svg"
OUT_PNG_PATH = WORKSPACE / "assets" / "avatar.png"

PROFILE_NAME = "Mohan Aditya Sadhanala"
PROFILE_URL = "https://github.com/developer-mohanaditya"


def rgb_bytes_from_pil(im: Image.Image) -> bytes:
    if im.mode != "RGB":
        im = im.convert("RGB")
    return im.tobytes()


def round_mask(size: Tuple[int, int]) -> Image.Image:
    mask = Image.new("L", size, 0)
    d = ImageDraw.Draw(mask)
    d.ellipse((0, 0, size[0] - 1, size[1] - 1), fill=255)
    return mask


def circle_crop_pil(im: Image.Image, radius_px: int) -> Image.Image:
    size = radius_px * 2
    im = im.copy()
    im.thumbnail((size, size), Image.LANCZOS)
    w, h = im.size
    left = (w - size) / 2
    top = (h - size) / 2
    im = im.crop((max(0, left), max(0, top), min(w, left + size), min(h, top + size)))
    im = ImageOps.fit(im, (size, size), method=Image.LANCZOS, centering=(0.5, 0.5))
    return im


def boost_granite(im: Image.Image) -> Image.Image:
    im = im.convert("RGB")
    im = ImageEnhance.Contrast(im).enhance(1.06)
    im = ImageEnhance.Color(im).enhance(1.08)
    im = ImageEnhance.Brightness(im).enhance(1.02)
    return im


def soften_edges(im: Image.Image, radius_px: int) -> Image.Image:
    mask = round_mask((radius_px * 2, radius_px * 2))
    blurred = mask.filter(ImageFilter.GaussianBlur(float(radius_px) * 0.06))
    return im, blurred


def face_center_box(im: Image.Image) -> Optional[Tuple[int, int, int, int]]:
    """
    Return (x, y, w, h) around the detected face, or None.
    Uses the frontalface cascade that ships with OpenCV when available.
    """
    if not _HAS_CV2:
        return None
    rgb = cvtColor(numpy_to_cv2_rgb(im), COLOR_RGB2GRAY)
    models_dir = WORKSPACE / "models"
    frontal_xml = models_dir / "haarcascade_frontalface_default.xml"

    if hasattr(cv2, "CascadeClassifier"):
        if frontal_xml.exists():
            cascade = cv2.CascadeClassifier(str(frontal_xml))
            if not cascade.empty():
                gray = cvtColor(numpy_to_cv2_rgb(im), COLOR_RGB2GRAY)
                faces = cascade.detectMultiScale(gray, scaleFactor=1.08, minNeighbors=4, minSize=(40, 40))
                if len(faces) > 0:
                    return (int(faces[0][0]), int(faces[0][1]), int(faces[0][2]), int(faces[0][3]))
    return None
    faces = cascade.detectMultiScale(rgb, scaleFactor=1.1, minNeighbors=4, minSize=(40, 40))
    if len(faces) == 0:
        return None
    x, y, w, h = faces[0]
    return (int(x), int(y), int(w), int(h))


def numpy_to_cv2_rgb(im: Image.Image):
    import numpy as np
    arr = np.asarray(im.convert("RGB"))
    return arr


def dominant_bg_color(im: Image.Image) -> Tuple[int, int, int]:
    small = im.convert("RGB").resize((8, 8), Image.LANCZOS)
    pixels = list(small.getdata())
    r = sum(p[0] for p in pixels) // len(pixels)
    g = sum(p[1] for p in pixels) // len(pixels)
    b = sum(p[2] for p in pixels) // len(pixels)
    return (r, g, b)


def build_avatar_svg(png_path: pathlib.Path, avatar_size_px: int) -> str:
    png_data = png_path.read_bytes()
    b64 = base64.standard_b64encode(png_data).decode("ascii")
    enc = urllib.parse.quote_from_bytes(png_data, safe="")
    src = f"data:image/png;base64,{b64}"

    ns = 'xmlns="http://www.w3.org/2000/svg"'
    circle_d = avatar_size_px / 2
    safe_size = avatar_size_px

    svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg {ns} viewBox="0 0 {safe_size} {safe_size}" width="{safe_size}" height="{safe_size}">
  <defs>
    <radialGradient id="sheen" cx="40%" cy="35%" r="75%">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="0.18"/>
      <stop offset="55%" stop-color="#ffffff" stop-opacity="0.03"/>
      <stop offset="100%" stop-color="#000000" stop-opacity="0.10"/>
    </radialGradient>
    <clipPath id="circle-clip">
      <circle cx="{circle_d}" cy="{circle_d}" r="{circle_d}"/>
    </clipPath>
  </defs>

  <!-- outer ring -->
  <circle cx="{circle_d}" cy="{circle_d}" r="{circle_d}" fill="#0d1117" stroke="#30363d" stroke-width="2.5"/>
  <circle cx="{circle_d}" cy="{circle_d}" r="{circle_d - 1.5}" fill="none" stroke="#58a6ff" stroke-opacity="0.00"/>

  <!-- portrait -->
  <g clip-path="url(#circle-clip)">
    <image href="{src}" x="0" y="0" width="{safe_size}" height="{safe_size}" preserveAspectRatio="xMidYMid slice"/>
    <rect x="0" y="0" width="{safe_size}" height="{safe_size}" fill="url(#sheen)"/>
  </g>

  <!-- crisp inner line -->
  <circle cx="{circle_d}" cy="{circle_d}" r="{circle_d - 1}" fill="none" stroke="#1f6feb" stroke-opacity="0.25" stroke-width="1"/>
</svg>
"""
    return textwrap.dedent(svg).lstrip("\n")


def main(
    source: pathlib.Path = SOURCE_PATH,
    out_svg: pathlib.Path = OUT_PATH,
    out_png: pathlib.Path = OUT_PNG_PATH,
    avatar_size_px: int = 512,
) -> pathlib.Path:
    if not source.exists():
        raise FileNotFoundError(f"Source photo not found: {source}")

    im = Image.open(source)
    print(f"Loaded source: {source} | size={im.size} mode={im.mode}")

    face_box = face_center_box(im)
    if face_box is not None:
        print(f"Face box detected: {face_box}")
        fx, fy, fw, fh = face_box
        crop_w = int(fw * 2.4)
        crop_h = int(fh * 2.4)
        half = crop_w / 2
        left = max(0, int(fx + fw / 2 - half))
        top = max(0, int(fy + fh / 2 - crop_h / 2))
        right = min(im.width, left + crop_w)
        bottom = min(im.height, top + crop_h)
        left = max(0, right - crop_w)
        top = max(0, bottom - crop_h)
        im = im.crop((left, top, right, bottom))
        print(f"Cropped around face to {im.size}")

    im = boost_granite(im)

    radius = avatar_size_px // 2
    portrait = circle_crop_pil(im, radius)

    portrait_rgb = portrait.convert("RGB")
    portrait_rgb.save(out_png, format="PNG")
    print(f"Saved avatar PNG: {out_png} ({out_png.stat().st_size} bytes)")

    svg = build_avatar_svg(out_png, avatar_size_px)
    out_svg.write_text(svg, encoding="utf-8")
    print(f"Saved avatar SVG: {out_svg} ({out_svg.stat().st_size} bytes)")

    return out_svg


if __name__ == "__main__":
    main()
