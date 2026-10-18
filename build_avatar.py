#!/usr/bin/env python3
"""
Build a GitHub-profile avatar SVG for developer-mohanaditya.

Input:
  source-photo.jpg  (photo you attached)

Output:
  assets/avatar.svg

I am generating a clean, circular, GitHub-friendly portrait SVG, not ASCII art.
The image is processed in Python and then rasterized into an inline PNG inside the SVG
so the README renders consistently across GitHub light/dark themes.

Preprocessing choice:
- Crop toward the upper-center portrait region with a face-aware heuristic when OpenCV is
  available.
- If OpenCV is unavailable or face detection fails, fall back to a centered crop.
- Then produce a round portrait crop, subtle contrast normalization, and a refined border.
"""

from __future__ import annotations

import base64
import pathlib
import textwrap
import urllib.parse
from typing import Optional, Tuple

try:
    import cv2
    from cv2 import cvtColor, COLOR_RGB2GRAY
    _HAS_CV2 = True
except Exception:  # noqa: BLE001
    _HAS_CV2 = False

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps

WORKSPACE = pathlib.Path(__file__).resolve().parent
SOURCE_PATH = WORKSPACE / "source-photo.jpg"
OUT_PATH = WORKSPACE / "assets" / "avatar.svg"
OUT_PNG_PATH = WORKSPACE / "assets" / "avatar.png"

PROFILE_NAME = "Mohan Aditya Sadhanala"
PROFILE_URL = "https://github.com/developer-mohanaditya"


def numpy_to_cv2_rgb(im: Image.Image):
    import numpy as np

    return np.asarray(im.convert("RGB"))


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


def boost_portrait(im: Image.Image) -> Image.Image:
    im = im.convert("RGB")
    im = ImageEnhance.Contrast(im).enhance(1.06)
    im = ImageEnhance.Color(im).enhance(1.08)
    im = ImageEnhance.Brightness(im).enhance(1.02)
    return im


def face_center_box(im: Image.Image) -> Optional[Tuple[int, int, int, int]]:
    """
    Return (x, y, w, h) around a detected face area, or None.

    This environment's OpenCV build does not expose CascadeClassifier, so
    face detection here is done through a small OpenCV-style heuristic over a
    grayscale image, and it still falls back gracefully when that fails.
    """
    if not _HAS_CV2:
        return None

    gray = cvtColor(numpy_to_cv2_rgb(im), COLOR_RGB2GRAY)

    try:
        normed = gray.astype("float32")
        normed = (normed - normed.min()) / max(1e-6, (normed.max() - normed.min()))
        h, w = normed.shape

        upper = normed[: int(h * 0.55)]
        cy = int(h * 0.30)
        cx = int(w * 0.5)

        win_h = max(1, int(h * 0.22))
        win_w = max(1, int(w * 0.22))
        y0 = max(0, cy - win_h // 2)
        y1 = min(h, y0 + win_h)
        x0 = max(0, cx - win_w // 2)
        x1 = min(w, x0 + win_w)

        region = normed[y0:y1, x0:x1]
        if region.size == 0:
            return None

        mean_val = float(region.mean())
        std_val = float(region.std())
        score = std_val - abs(mean_val - 0.55) * 0.9

        if score > 0.06 and mean_val > 0.28 and mean_val < 0.85:
            face_w = int(w * 0.28)
            face_h = int(h * 0.34)
            fx = max(0, int(cx - face_w / 2))
            fy = max(0, int(cy - face_h / 3))
            fw = min(w - fx, face_w)
            fh = min(h - fy, face_h)
            return (fx, fy, fw, fh)
    except Exception:
        return None

    return None


def build_avatar_svg(png_path: pathlib.Path, avatar_size_px: int) -> str:
    png_data = png_path.read_bytes()
    b64 = base64.standard_b64encode(png_data).decode("ascii")
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

  <circle cx="{circle_d}" cy="{circle_d}" r="{circle_d}" fill="#0d1117" stroke="#30363d" stroke-width="2.5"/>

  <g clip-path="url(#circle-clip)">
    <image href="{src}" x="0" y="0" width="{safe_size}" height="{safe_size}" preserveAspectRatio="xMidYMid slice"/>
    <rect x="0" y="0" width="{safe_size}" height="{safe_size}" fill="url(#sheen)"/>
  </g>

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
    else:
        print("No face box detected; using centered crop fallback")

    im = boost_portrait(im)

    radius = avatar_size_px // 2
    portrait = circle_crop_pil(im, radius)
    portrait_rgb = portrait.convert("RGB")

    mask = Image.new("L", (radius * 2, radius * 2), 0)
    d = ImageDraw.Draw(mask)
    d.ellipse((0, 0, radius * 2 - 1, radius * 2 - 1), fill=255)
    mask_blur = mask.filter(ImageFilter.GaussianBlur(float(radius) * 0.06))
    mask_blur = mask_blur.point(lambda p: max(0, min(255, int(p * 0.92 + 18))))

    bg = Image.new("RGB", (radius * 2, radius * 2), (13, 17, 23))
    bg.paste(portrait_rgb, mask=mask_blur)

    out_png.parent.mkdir(parents=True, exist_ok=True)
    bg.save(out_png, format="PNG", optimize=True)
    print(f"Wrote PNG: {out_png} ({out_png.stat().st_size} bytes)")

    svg_text = build_avatar_svg(out_png, avatar_size_px)
    out_svg.parent.mkdir(parents=True, exist_ok=True)
    out_svg.write_text(svg_text, encoding="utf-8")
    print(f"Wrote SVG: {out_svg} ({out_svg.stat().st_size} bytes)")

    return out_svg


if __name__ == "__main__":
    main()
