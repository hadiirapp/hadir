"""Render real sheet screenshots via LibreOffice and compose 2000x2000 listing images.

Usage: python3 build_mockups.py <recalc.py path>   (run from the business folder after build_planner.py)
"""
import glob
import subprocess
import sys
import tempfile
from pathlib import Path

import arabic_reshaper
from bidi.algorithm import get_display
from openpyxl import load_workbook
from PIL import Image, ImageDraw, ImageFont

RECALC = sys.argv[1]
F = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
TMP = Path(tempfile.mkdtemp())


def font(s):
    return ImageFont.truetype(F, s, layout_engine=ImageFont.Layout.BASIC)


def ar(t):
    return get_display(arabic_reshaper.reshape(t))


def shot(lang, idx, rows=None):
    """Return a cropped PIL image of sheet #idx."""
    wb = load_workbook(f"product/Smart-Budget-Planner-{lang}.xlsx")
    ws = wb.worksheets[idx]
    wb.move_sheet(ws, offset=-idx)
    wb.active = 0
    for w in wb.worksheets:
        w.sheet_view.tabSelected = w is ws
    ws.page_setup.orientation = "landscape"
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 1
    if rows:
        ws.print_area = rows
    x = TMP / f"{lang}-{idx}.xlsx"
    wb.save(x)
    subprocess.run(["python3", RECALC, str(x), "90"], check=True, capture_output=True)
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(TMP), str(x)], check=True, capture_output=True)
    subprocess.run(["pdftoppm", "-r", "160", "-png", "-f", "1", "-l", "1", str(x.with_suffix(".pdf")), str(x.with_suffix(""))], check=True)
    im = Image.open(glob.glob(f"{x.with_suffix('')}-*.png")[0]).convert("RGB")
    bg = Image.new("RGB", im.size, "white")
    from PIL import ImageChops
    bbox = ImageChops.difference(im, bg).getbbox()
    return im.crop((bbox[0] - 20, bbox[1] - 20, bbox[2] + 20, bbox[3] + 20))


def card(img, bg, title, sub, out, badge):
    im = Image.new("RGB", (2000, 2000), bg)
    d = ImageDraw.Draw(im)
    for t, y, s in ((title, 70, 104), (sub, 205, 60)):
        w = d.textlength(t, font=font(s))
        d.text(((2000 - w) / 2, y), t, font=font(s), fill="white", stroke_width=4, stroke_fill="#134E4A")
    # laptop-ish frame
    img = img.copy()
    img.thumbnail((1760, 1350))
    fx, fy = (2000 - img.width) // 2, 340 + (1350 - img.height) // 2
    d.rounded_rectangle([fx - 30, fy - 60, fx + img.width + 30, fy + img.height + 30], 30, fill="#1F2937")
    for i, c in enumerate(("#EF4444", "#F59E0B", "#22C55E")):
        d.ellipse([fx + i * 40, fy - 42, fx + 24 + i * 40, fy - 18], fill=c)
    im.paste(img, (fx, fy))
    d.rounded_rectangle([300, 1800, 1700, 1940], 40, fill="#FDE047")
    w = d.textlength(badge, font=font(58))
    d.text(((2000 - w) / 2, 1838), badge, font=font(58), fill="#134E4A")
    im.save(out, quality=90)


if __name__ == "__main__":
    card(shot("EN", 3, "A1:M24"), "#0F766E", "Smart Budget Planner", "Excel + Google Sheets · auto dashboard",
         "marketing/listing-1-dashboard.jpg", "INSTANT DOWNLOAD")
    card(shot("EN", 2, "A1:F20"), "#2563EB", "Log it in seconds", "Dropdowns for type & category · auto totals",
         "marketing/listing-2-transactions.jpg", "1,000 TRANSACTION ROWS")
    card(shot("EN", 4, "A1:G10"), "#9333EA", "Savings Goals", "See % done + how much to save each month",
         "marketing/listing-3-goals.jpg", "GOALS · DEBT · BILLS")
    card(shot("EN", 5, "A1:G15"), "#DC2626", "Debt-Free Date", "Months to payoff + total interest, calculated",
         "marketing/listing-4-debt.jpg", "SNOWBALL METHOD")
    card(shot("AR", 3, "A1:M24"), "#0F766E", ar("مخطط الميزانية الذكي"), ar("نسخة عربية كاملة") + " · RTL",
         "marketing/listing-5-arabic.jpg", "ENGLISH + ARABIC")
