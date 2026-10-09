"""Render a vertical 1080x1920 "Guess the word" kids Short (Arabic letters) with ffmpeg.

Usage: python3 build_short.py <out.mp4> [start_index] [count]
"""
import math
import subprocess
import sys
import tempfile
from pathlib import Path

import arabic_reshaper
from bidi.algorithm import get_display
from PIL import Image, ImageDraw, ImageFont

from build_workbook import AR_LETTERS

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
W, H, FPS = 1080, 1920, 30
BGS = ["#FF6B6B", "#4DABF7", "#69DB7C", "#9775FA", "#FFA94D", "#F783AC"]


def ar(t):
    return get_display(arabic_reshaper.reshape(t))


def font(size):
    return ImageFont.truetype(FONT, size, layout_engine=ImageFont.Layout.BASIC)


def centred(d, y, text, size, fill="white"):
    f = font(size)
    w = d.textlength(text, font=f)
    d.text(((W - w) / 2, y), text, font=f, fill=fill, stroke_width=max(2, size // 25), stroke_fill="#1F2A44")


def frame(letter, word, meaning, t, bg, idx, total):
    """t = seconds into this letter's 6s segment."""
    im = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(im)
    for k in range(12):  # floating bubbles
        x = (k * 173 + t * 40 * (1 + k % 3)) % W
        y = (k * 311 - t * 60 * (1 + k % 2)) % H
        d.ellipse([x, y, x + 60 + k * 4, y + 60 + k * 4], fill="#ffffff")
    im = Image.blend(Image.new("RGB", (W, H), bg), im, 0.25)
    d = ImageDraw.Draw(im)
    centred(d, 140, "Guess the word!", 80)
    centred(d, 250, ar("خمّن الكلمة!"), 80)
    scale = 1 + 0.06 * math.sin(t * 4)
    centred(d, 520, letter, int(420 * scale))
    if t < 3:
        n = 3 - int(t)
        centred(d, 1250, str(n), 220, fill="#FFD43B")
        centred(d, 1520, ar(f"تبدأ بحرف {letter}"), 70)
    else:
        centred(d, 1180, ar(word), 200, fill="#FFD43B")
        centred(d, 1450, meaning, 110)
    centred(d, 1760, f"{idx}/{total}  ·  Follow for more letters!", 48)
    return im


def build(out, start=0, count=3):
    letters = AR_LETTERS[start:start + count]
    with tempfile.TemporaryDirectory() as tmp:
        n = 0
        for i, (letter, _name, word, meaning) in enumerate(letters):
            for f in range(6 * FPS):
                frame(letter, word, meaning, f / FPS, BGS[(start + i) % len(BGS)], i + 1, len(letters)).save(
                    f"{tmp}/f{n:05d}.png")
                n += 1
        # simple cheerful tone bed: soft beep each countdown second + chime on reveal
        beeps = []
        for i in range(len(letters)):
            base = i * 6
            beeps += [f"sine=f=660:d=0.15,adelay={int((base + s) * 1000)}|{int((base + s) * 1000)}" for s in (0, 1, 2)]
            beeps += [f"sine=f=990:d=0.4,adelay={int((base + 3) * 1000)}|{int((base + 3) * 1000)}"]
        inputs, labels = [], []
        for k, b in enumerate(beeps):
            inputs += ["-f", "lavfi", "-i", b]
            labels.append(f"[{k + 1}:a]")
        dur = len(letters) * 6
        filt = "".join(labels) + f"amix=inputs={len(labels)}:normalize=0,volume=0.4,apad=whole_dur={dur}[a]"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", f"{tmp}/f%05d.png",
                        *inputs, "-filter_complex", filt, "-map", "0:v", "-map", "[a]", "-t", str(dur),
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "23", "-c:a", "aac", out], check=True)


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent))
    build(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 0, int(sys.argv[3]) if len(sys.argv) > 3 else 3)
