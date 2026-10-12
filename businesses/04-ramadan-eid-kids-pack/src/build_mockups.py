"""Listing images (2000x2000) + free sample PDF from the real pack pages.

Usage: python3 src/build_mockups.py   (after build_pack.py)
"""
import glob
import subprocess
import tempfile

import arabic_reshaper
from bidi.algorithm import get_display
from PIL import Image, ImageDraw, ImageFont
from pypdf import PdfReader, PdfWriter

F = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
PDF = "product/Ramadan-Eid-Kids-Activity-Pack.pdf"


def font(s):
    return ImageFont.truetype(F, s, layout_engine=ImageFont.Layout.BASIC)


def ar(t):
    return get_display(arabic_reshaper.reshape(t))


def pages(nums):
    tmp = tempfile.mkdtemp()
    out = {}
    for n in nums:
        subprocess.run(["pdftoppm", "-r", "110", "-png", "-f", str(n), "-l", str(n), PDF, f"{tmp}/p{n}"], check=True)
        out[n] = Image.open(glob.glob(f"{tmp}/p{n}-*.png")[0]).convert("RGBA")
    return out


def text(d, t, y, s, fill="white"):
    w = d.textlength(t, font=font(s))
    d.text(((2000 - w) / 2, y), t, font=font(s), fill=fill, stroke_width=5, stroke_fill="#1E1B4B")


def card(P, bg, title, sub, picks, badge, out):
    im = Image.new("RGBA", (2000, 2000), bg)
    d = ImageDraw.Draw(im)
    text(d, title, 60, 104)
    text(d, sub, 200, 64, "#FDE68A")
    n = len(picks)
    angles, offs = {1: ([0], [0]), 3: ([-8, 0, 8], [-520, 0, 520])}[n]
    for i in sorted(range(n), key=lambda i: -abs(offs[i])):
        pg = P[picks[i]].copy()
        pg.thumbnail((1000, 1300) if n > 1 else (1150, 1450))
        sh = Image.new("RGBA", (pg.width + 40, pg.height + 40), (0, 0, 0, 0))
        ImageDraw.Draw(sh).rectangle([20, 20, pg.width + 20, pg.height + 20], fill=(0, 0, 0, 90))
        sh.paste(pg, (0, 0))
        r = sh.rotate(angles[i], expand=True, resample=Image.BICUBIC)
        im.alpha_composite(r, (1000 + offs[i] - r.width // 2, 1060 - r.height // 2 + (40 if offs[i] else 0)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([250, 1800, 1750, 1940], 40, fill="#F59E0B")
    w = d.textlength(badge, font=font(58))
    d.text(((2000 - w) / 2, 1836), badge, font=font(58), fill="#1E1B4B")
    im.convert("RGB").save(out, quality=90)


if __name__ == "__main__":
    P = pages([1, 3, 4, 5, 6, 7, 11, 13, 14, 15, 19, 21, 30, 31, 32])
    card(P, "#312E81", "Ramadan & Eid Kids Pack", ar("نشاطات رمضان والعيد") + " · 33 pages", [3, 1, 6], "INSTANT DOWNLOAD", "marketing/listing-1-hero.jpg")
    card(P, "#7C3AED", "Build Ramadan habits", "Good deeds · Prayer · Quran trackers", [4, 3, 5], "PRINT & PIN ON THE FRIDGE", "marketing/listing-2-trackers.jpg")
    card(P, "#0EA5E9", "Quiet-time fun before iftar", "Colouring · Word search (EN + AR) · Mazes", [7, 13, 15], "ANSWER KEYS INCLUDED", "marketing/listing-3-activities.jpg")
    card(P, "#EC4899", "Get ready for Eid!", "Bunting · Eid cards · Gift tags · Award", [21, 30, 31], "AGES 4–10", "marketing/listing-4-eid.jpg")
    card(P, "#10B981", "30 Good Deeds Jar Cards", "Pick one every day of Ramadan", [19], "ARABIC + ENGLISH", "marketing/listing-5-deeds.jpg")
    r, w = PdfReader(PDF), PdfWriter()
    for i in (0, 2, 5):
        w.add_page(r.pages[i])
    with open("product/FREE-SAMPLE-Ramadan-Pack.pdf", "wb") as f:
        w.write(f)
