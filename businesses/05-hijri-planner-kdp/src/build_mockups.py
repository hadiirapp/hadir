"""Listing images (2000x2000) from the real cover and interior spreads.

Usage: python3 src/build_mockups.py   (after build_planner.py)
"""
import glob
import subprocess
import tempfile

import arabic_reshaper
from bidi.algorithm import get_display
from PIL import Image, ImageDraw, ImageFont

F = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
INT = "product/KDP-interior-2027-Hijri-Planner-8.5x11.pdf"
COV = "product/KDP-cover-2027-Hijri-Planner.pdf"
TMP = tempfile.mkdtemp()


def font(s):
    return ImageFont.truetype(F, s, layout_engine=ImageFont.Layout.BASIC)


def ar(t):
    return get_display(arabic_reshaper.reshape(t))


def render(pdf, n, dpi=110):
    subprocess.run(["pdftoppm", "-r", str(dpi), "-png", "-f", str(n), "-l", str(n), pdf, f"{TMP}/r{n}"], check=True)
    return Image.open(sorted(glob.glob(f"{TMP}/r{n}-*.png"))[-1]).convert("RGB")


def spread(a, b):
    a, b = render(INT, a), render(INT, b)
    s = Image.new("RGB", (a.width + b.width + 6, a.height), "#9CA3AF")
    s.paste(a, (0, 0))
    s.paste(b, (a.width + 6, 0))
    return s


def card(img, title, sub, badge, out, maxsize=(1800, 1350)):
    im = Image.new("RGB", (2000, 2000), "#0F5132")
    d = ImageDraw.Draw(im)
    for t, y, s, col in ((title, 70, 96, "white"), (sub, 195, 58, "#F5DEB3")):
        w = d.textlength(t, font=font(s))
        d.text(((2000 - w) / 2, y), t, font=font(s), fill=col)
    img = img.copy()
    img.thumbnail(maxsize)
    x, y = (2000 - img.width) // 2, 310 + (1420 - img.height) // 2
    d.rectangle([x + 16, y + 16, x + img.width + 16, y + img.height + 16], fill="#0A3622")
    im.paste(img, (x, y))
    d.rounded_rectangle([300, 1810, 1700, 1940], 40, fill="#B8860B")
    w = d.textlength(badge, font=font(54))
    d.text(((2000 - w) / 2, 1845), badge, font=font(54), fill="white")
    im.save(out, quality=90)


if __name__ == "__main__":
    cov = render(COV, 1, 120)
    front = cov.crop((cov.width - int(cov.width * 8.625 / 17.5878), 0, cov.width, cov.height))
    card(front, "2027 Hijri & Gregorian Planner", ar("مفكرة هجرية وميلادية ٢٠٢٧"), "150 PAGES · 8.5 x 11", "marketing/listing-1-cover.jpg", (1100, 1400))
    card(spread(8, 9), "Weekly spreads", "Gregorian + Hijri date · 5 prayer circles · Jumu'ah", "53 WEEKS · MON–SUN", "marketing/listing-2-weekly.jpg")
    card(spread(6, 7), "Monthly calendars", "Islamic dates · goals · habit tracker", "12 MONTHS", "marketing/listing-3-monthly.jpg")
    card(spread(18, 19), "30-day Ramadan planner", "Fasting · prayers · Taraweeh · Quran · good deeds", "RAMADAN 1448 / 2027", "marketing/listing-4-ramadan.jpg")
