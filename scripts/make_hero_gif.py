#!/usr/bin/env python3
"""Compose the Higgsfield-generated portrait clip into a terminal-window
chrome frame (matching the other panels) and export it as an optimized
looping GIF.

This does NOT call Higgsfield itself — that step is interactive (upload
the headshot, generate with the desired prompt, download the result).
Once you have a rendered clip, point this script at it:

    python3 scripts/make_hero_gif.py path/to/portrait.mp4

Requires `ffmpeg` and `gifsicle` on PATH (`brew install ffmpeg gifsicle`).
"""
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FRAME_PNG = ROOT / "scripts" / "icon_cache" / "_chrome_frame.png"
OUT_GIF = ROOT / "hero-live.gif"

CONTENT_W, CONTENT_H = 300, 400
PAD = 10
TITLE_H = 34
W = CONTENT_W + PAD * 2
H = TITLE_H + CONTENT_H + PAD * 2
TITLE = "~/whoami --live"

BG = (13, 17, 23, 255)
BORDER = (48, 54, 61, 255)
TITLEBAR = (22, 27, 34, 255)
DOTS = [(255, 95, 86), (255, 189, 46), (39, 201, 63)]


def build_chrome_frame() -> Path:
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    r = 10
    d.rounded_rectangle([0, 0, W - 1, H - 1], radius=r, fill=BG, outline=BORDER, width=1)
    d.rectangle([0, r, W - 1, TITLE_H], fill=TITLEBAR)
    d.rounded_rectangle([0, 0, W - 1, TITLE_H + r], radius=r, fill=TITLEBAR)
    d.line([(0, TITLE_H), (W - 1, TITLE_H)], fill=BORDER, width=1)

    for i, c in enumerate(DOTS):
        cx, cy = 24 + i * 20, TITLE_H // 2
        d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=c)

    try:
        font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 12)
    except OSError:
        font = ImageFont.load_default()
    bbox = d.textbbox((0, 0), TITLE, font=font)
    tw = bbox[2] - bbox[0]
    d.text(((W - tw) / 2, TITLE_H / 2 - 7), TITLE, fill=(125, 133, 144, 255), font=font)

    # transparent hole where the video content shows through
    hole = Image.new("RGBA", (CONTENT_W, CONTENT_H), (0, 0, 0, 0))
    img.paste(hole, (PAD, TITLE_H), hole)

    FRAME_PNG.parent.mkdir(parents=True, exist_ok=True)
    img.save(FRAME_PNG)
    return FRAME_PNG


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True, capture_output=True)


def main(src_video: Path) -> None:
    for tool in ("ffmpeg", "gifsicle"):
        if shutil.which(tool) is None:
            sys.exit(f"error: {tool} not found on PATH (brew install {tool})")

    frame = build_chrome_frame()
    composited = ROOT / "scripts" / "icon_cache" / "_composited.mp4"
    raw_gif = ROOT / "scripts" / "icon_cache" / "_hero_raw.gif"

    run([
        "ffmpeg", "-y", "-loop", "1", "-i", str(frame), "-i", str(src_video),
        "-filter_complex",
        f"[1:v]scale={CONTENT_W}:{CONTENT_H}[vid];"
        f"[0:v][vid]overlay={PAD}:{TITLE_H}:shortest=1,format=yuv420p[out]",
        "-map", "[out]", "-t", "5.04", "-c:v", "libx264", "-crf", "18",
        str(composited),
    ])
    run([
        "ffmpeg", "-y", "-i", str(composited), "-vf",
        f"fps=10,scale={CONTENT_W}:-1:flags=lanczos,split[s0][s1];"
        "[s0]palettegen=stats_mode=diff:max_colors=160[p];"
        "[s1][p]paletteuse=dither=bayer",
        "-loop", "0", str(raw_gif),
    ])
    run(["gifsicle", "-O3", "--lossy=100", str(raw_gif), "-o", str(OUT_GIF)])

    print(f"Wrote {OUT_GIF} ({OUT_GIF.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: make_hero_gif.py <path-to-source-clip.mp4>")
    main(Path(sys.argv[1]))
