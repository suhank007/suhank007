#!/usr/bin/env python3
"""Prep a headshot for ASCII conversion: remove background, boost local
contrast (CLAHE), composite onto white. Output: source-prepped.png"""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import remove

ROOT = Path(__file__).resolve().parent.parent


def prep(src_path: Path, out_path: Path) -> None:
    raw = Image.open(src_path).convert("RGBA")

    # 1. Remove background so the subject is isolated.
    cutout = remove(raw)

    # 2. Composite onto pure white (background maps to blank end of ramp).
    white_bg = Image.new("RGBA", cutout.size, (255, 255, 255, 255))
    composited = Image.alpha_composite(white_bg, cutout).convert("RGB")

    # 3. Boost local contrast with CLAHE so a flat face gets real
    # highlights and shadows.
    arr = cv2.cvtColor(np.array(composited), cv2.COLOR_RGB2BGR)
    lab = cv2.cvtColor(arr, cv2.COLOR_BGR2LAB)
    l_channel, a_channel, b_channel = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    l_channel = clahe.apply(l_channel)
    lab = cv2.merge((l_channel, a_channel, b_channel))
    contrasted = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

    gray = cv2.cvtColor(contrasted, cv2.COLOR_BGR2GRAY)
    Image.fromarray(gray).save(out_path)
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "source-photo.jpg"
    out = ROOT / "source-prepped.png"
    prep(src, out)
