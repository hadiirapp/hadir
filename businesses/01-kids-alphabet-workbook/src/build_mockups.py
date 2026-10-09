"""Build 2000x2000 marketplace listing images from real workbook pages.

Usage: python3 build_mockups.py   (run from the business folder, after build_workbook.py)
"""
import glob
import subprocess
import tempfile

import arabic_reshaper
from bidi.algorithm import get_display
from PIL import Image, ImageDraw, ImageFont

F = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
PDF = "product/Little-Learners-Arabic-English-Workbook.pdf"


def font(s):
    return ImageFont.truetype(F, s, layout_engine=ImageFont.Layout.BASIC)


def ar(t):
    return get_display(arabic_reshaper.reshape(t))


def text(d, t, y, s):
    w = d.textlength(t, font=font(s))
    d.text(((2000 - w) / 2, y), t, font=font(s), fill="white", stroke_width=5, stroke_fill="#1F2A44")


def load_pages(nums):
    tmp = tempfile.mkdtemp()
    out = {}
    for n in nums:
        subprocess.run(["pdftoppm", "-r", "110", "-png", "-f", str(n), "-l", str(n), PDF, f"{tmp}/p{n}"], check=True)
        out[n] = Image.open(glob.glob(f"{tmp}/p{n}-*.png")[0]).convert("RGBA")
    return out


def card(pages, bg, title, sub, picks, footer, out):
    im = Image.new("RGBA", (2000, 2000), bg)
    d = ImageDraw.Draw(im)
    text(d, title, 60, 110)
    text(d, sub, 200, 68)
    n = len(picks)
    angles = {1: [0], 2: [-6, 6], 3: [-8, 0, 8]}[n]
    offsets = {1: [0], 2: [-300, 300], 3: [-520, 0, 520]}[n]
    order = sorted(range(n), key=lambda i: -abs(offsets[i]))  # middle page on top
    for i in order:
        pg = pages[picks[i]].copy()
        pg.thumbnail((1000, 1300) if n > 1 else (1150, 1450))
        shadow = Image.new("RGBA", (pg.width + 40, pg.height + 40), (0, 0, 0, 0))
        ImageDraw.Draw(shadow).rectangle([20, 20, pg.width + 20, pg.height + 20], fill=(0, 0, 0, 90))
        shadow.paste(pg, (0, 0))
        rot = shadow.rotate(angles[i], expand=True, resample=Image.BICUBIC)
        x = 1000 + offsets[i] - rot.width // 2
        y = 1060 - rot.height // 2 + (40 if offsets[i] else 0)
        im.alpha_composite(rot, (x, y))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([250, 1800, 1750, 1940], 40, fill="#1F2A44")
    w = d.textlength(footer, font=font(60))
    d.text(((2000 - w) / 2, 1835), footer, font=font(60), fill="#FFD43B")
    im.convert("RGB").save(out, quality=90)


if __name__ == "__main__":
    p = load_pages([1, 3, 4, 29, 31, 57, 62, 70, 80, 93])
    card(p, "#4DABF7", "93-Page Kids Workbook", ar("عربي + إنجليزي") + "  ·  Ages 3–6", [3, 1, 29],
         "INSTANT DOWNLOAD · PRINTABLE", "marketing/listing-1-hero.jpg")
    card(p, "#FF6B6B", "Trace A–Z + Alif–Ya", "Big dashed letters · words · drawing", [4, 31, 62],
         "54 LETTER PAGES", "marketing/listing-2-letters.jpg")
    card(p, "#69DB7C", "Numbers 0–10 + 20 Mazes", "Gets harder page by page · answer key", [57, 70, 80],
         "11 NUMBER PAGES + 20 MAZES", "marketing/listing-3-numbers-mazes.jpg")
    card(p, "#9775FA", "Finish = Certificate!", "Print at home · reuse in a sheet protector", [93],
         "PERFECT FOR HOME & CLASSROOM", "marketing/listing-4-certificate.jpg")
