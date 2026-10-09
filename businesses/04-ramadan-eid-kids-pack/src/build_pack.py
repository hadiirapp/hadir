"""Generate the "Ramadan & Eid Kids Activity Pack" printable PDF (Arabic + English).

Usage: python3 build_pack.py <output_dir>
"""
import math
import random
import sys
from pathlib import Path

import arabic_reshaper
from bidi.algorithm import get_display
from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
pdfmetrics.registerFont(TTFont("Sans", FONT_DIR + "DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("SansBold", FONT_DIR + "DejaVuSans-Bold.ttf"))

W, H = letter
M = 50
INK = HexColor("#1E1B4B")
SOFT = HexColor("#A5B4FC")
GOLD = HexColor("#F59E0B")
NAVY = HexColor("#312E81")
ACC = [HexColor(c) for c in ("#7C3AED", "#F59E0B", "#0EA5E9", "#10B981", "#EC4899", "#6366F1")]


def ar(t):
    return get_display(arabic_reshaper.reshape(t))


class Book:
    def __init__(self, path):
        self.c = canvas.Canvas(str(path), pagesize=letter)
        self.c.setTitle("Ramadan & Eid Kids Activity Pack")
        self.c.setAuthor("Little Learners Studio")
        self.n = 0

    def page(self, accent=None, footer=True):
        if self.n:
            self.c.showPage()
        self.n += 1
        a = accent or ACC[self.n % len(ACC)]
        c = self.c
        c.setStrokeColor(a)
        c.setLineWidth(5)
        c.roundRect(20, 20, W - 40, H - 40, 22)
        # little stars in corners
        c.setFillColor(GOLD)
        for x, y in ((40, H - 40), (W - 40, H - 40), (40, 40), (W - 40, 40)):
            star(c, x, y, 9)
        if footer:
            c.setFont("Sans", 9)
            c.setFillColor(SOFT)
            c.drawCentredString(W / 2, 30, f"Ramadan & Eid Activity Pack · {self.n}")
        return a


def header(c, en, ar_txt, a, y=None):
    y = y or H - 95
    c.setFillColor(a)
    c.roundRect(M, y - 12, W - 2 * M, 50, 16, fill=1, stroke=0)
    c.setFillColor(white)
    a_txt = ar(ar_txt)
    size = 22
    while size > 12 and pdfmetrics.stringWidth(en, "SansBold", size) + pdfmetrics.stringWidth(a_txt, "SansBold", size) > W - 2 * M - 60:
        size -= 1
    c.setFont("SansBold", size)
    c.drawString(M + 18, y + 3, en)
    c.drawRightString(W - M - 18, y + 3, a_txt)


def star(c, cx, cy, r, fill=1, stroke=0):
    p = c.beginPath()
    for k in range(10):
        rad = r if k % 2 == 0 else r * 0.45
        a = math.pi / 2 + k * math.pi / 5
        (p.moveTo if k == 0 else p.lineTo)(cx + rad * math.cos(a), cy + rad * math.sin(a))
    p.close()
    c.drawPath(p, fill=fill, stroke=stroke)


def crescent(c, cx, cy, r, fill=1, stroke=0, bg=white):
    """Crescent drawn as the difference of two circles (outline mode draws an arc shape)."""
    p = c.beginPath()
    # outer arc from angle 60 to 300 (counter-clockwise), inner arc back
    p.arc(cx - r, cy - r, cx + r, cy + r, 60, 240)
    off = r * 0.45
    r2 = r * 0.82
    # inner circle centred to the right; find the matching inner arc
    p.arcTo(cx + off - r2, cy - r2, cx + off + r2, cy + r2, 252, -144)
    p.close()
    c.drawPath(p, fill=fill, stroke=stroke)


def colouring_setup(c):
    c.setStrokeColor(INK)
    c.setFillColor(white)
    c.setLineWidth(3)
    c.setLineJoin(1)
    c.setLineCap(1)


# ---------------- colouring pictures (pure vector, original) ----------------

def draw_lantern(c, cx, cy, s):
    colouring_setup(c)
    # ring + cap
    c.circle(cx, cy + 2.35 * s, 0.18 * s, fill=0)
    p = c.beginPath()
    p.moveTo(cx - 0.55 * s, cy + 1.6 * s); p.lineTo(cx, cy + 2.15 * s); p.lineTo(cx + 0.55 * s, cy + 1.6 * s); p.close()
    c.drawPath(p, fill=0, stroke=1)
    c.rect(cx - 0.7 * s, cy + 1.45 * s, 1.4 * s, 0.15 * s)
    # body (hexagonal lantern)
    p = c.beginPath()
    p.moveTo(cx - 0.7 * s, cy + 1.45 * s); p.lineTo(cx - 0.95 * s, cy + 0.6 * s); p.lineTo(cx - 0.7 * s, cy - 0.9 * s)
    p.lineTo(cx + 0.7 * s, cy - 0.9 * s); p.lineTo(cx + 0.95 * s, cy + 0.6 * s); p.lineTo(cx + 0.7 * s, cy + 1.45 * s); p.close()
    c.drawPath(p, fill=0, stroke=1)
    c.line(cx - 0.95 * s, cy + 0.6 * s, cx + 0.95 * s, cy + 0.6 * s)
    c.line(cx - 0.3 * s, cy + 1.45 * s, cx - 0.35 * s, cy - 0.9 * s)
    c.line(cx + 0.3 * s, cy + 1.45 * s, cx + 0.35 * s, cy - 0.9 * s)
    # flame window
    p = c.beginPath()
    p.moveTo(cx, cy + 0.45 * s); p.curveTo(cx + 0.25 * s, cy + 0.1 * s, cx + 0.2 * s, cy - 0.3 * s, cx, cy - 0.35 * s)
    p.curveTo(cx - 0.2 * s, cy - 0.3 * s, cx - 0.25 * s, cy + 0.1 * s, cx, cy + 0.45 * s)
    c.drawPath(p, fill=0, stroke=1)
    # base
    c.rect(cx - 0.85 * s, cy - 1.15 * s, 1.7 * s, 0.25 * s)
    p = c.beginPath()
    p.moveTo(cx - 0.5 * s, cy - 1.15 * s); p.lineTo(cx, cy - 1.55 * s); p.lineTo(cx + 0.5 * s, cy - 1.15 * s)
    c.drawPath(p, fill=0, stroke=1)


def draw_mosque(c, cx, cy, s):
    colouring_setup(c)
    # main hall
    c.rect(cx - 1.4 * s, cy - 1.2 * s, 2.8 * s, 1.3 * s)
    # dome
    p = c.beginPath()
    p.moveTo(cx - 0.9 * s, cy + 0.1 * s)
    p.curveTo(cx - 0.95 * s, cy + 1.1 * s, cx - 0.2 * s, cy + 1.3 * s, cx, cy + 1.55 * s)
    p.curveTo(cx + 0.2 * s, cy + 1.3 * s, cx + 0.95 * s, cy + 1.1 * s, cx + 0.9 * s, cy + 0.1 * s)
    c.drawPath(p, fill=0, stroke=1)
    c.line(cx, cy + 1.55 * s, cx, cy + 1.8 * s)
    c.setFillColor(white)
    crescent(c, cx, cy + 1.95 * s, 0.15 * s, fill=0, stroke=1)
    # door
    p = c.beginPath()
    p.moveTo(cx - 0.35 * s, cy - 1.2 * s); p.lineTo(cx - 0.35 * s, cy - 0.5 * s)
    p.curveTo(cx - 0.35 * s, cy - 0.15 * s, cx + 0.35 * s, cy - 0.15 * s, cx + 0.35 * s, cy - 0.5 * s)
    p.lineTo(cx + 0.35 * s, cy - 1.2 * s)
    c.drawPath(p, fill=0, stroke=1)
    # windows
    for dx in (-0.95, 0.95):
        p = c.beginPath()
        x = cx + dx * s
        p.moveTo(x - 0.18 * s, cy - 0.7 * s); p.lineTo(x - 0.18 * s, cy - 0.3 * s)
        p.curveTo(x - 0.18 * s, cy - 0.08 * s, x + 0.18 * s, cy - 0.08 * s, x + 0.18 * s, cy - 0.3 * s)
        p.lineTo(x + 0.18 * s, cy - 0.7 * s); p.close()
        c.drawPath(p, fill=0, stroke=1)
    # minarets
    for dx in (-1.75, 1.75):
        x = cx + dx * s
        c.rect(x - 0.18 * s, cy - 1.2 * s, 0.36 * s, 2.3 * s)
        c.rect(x - 0.26 * s, cy + 0.55 * s, 0.52 * s, 0.12 * s)
        p = c.beginPath()
        p.moveTo(x - 0.18 * s, cy + 1.1 * s); p.lineTo(x, cy + 1.55 * s); p.lineTo(x + 0.18 * s, cy + 1.1 * s)
        c.drawPath(p, fill=0, stroke=1)
    c.line(cx - 2.2 * s, cy - 1.2 * s, cx + 2.2 * s, cy - 1.2 * s)


def draw_gift(c, cx, cy, s):
    colouring_setup(c)
    c.rect(cx - 1.1 * s, cy - 1.2 * s, 2.2 * s, 1.6 * s)
    c.rect(cx - 1.25 * s, cy + 0.4 * s, 2.5 * s, 0.45 * s)
    c.rect(cx - 0.18 * s, cy - 1.2 * s, 0.36 * s, 2.05 * s)
    for sign in (-1, 1):
        p = c.beginPath()
        p.moveTo(cx, cy + 0.85 * s)
        p.curveTo(cx + sign * 0.3 * s, cy + 1.6 * s, cx + sign * 1.0 * s, cy + 1.4 * s, cx + sign * 0.6 * s, cy + 0.95 * s)
        p.close()
        c.drawPath(p, fill=0, stroke=1)
    for i in range(6):  # polka dots to colour
        c.circle(cx - 0.7 * s + (i % 3) * 0.6 * s + (0.3 * s if i // 3 else 0), cy - 0.35 * s - (i // 3) * 0.5 * s, 0.1 * s)


def draw_moon_stars(c, cx, cy, s):
    colouring_setup(c)
    crescent(c, cx - 0.3 * s, cy, 1.5 * s, fill=0, stroke=1)
    rnd = random.Random(7)
    for _ in range(9):
        x = cx + rnd.uniform(0.3, 1.9) * s
        y = cy + rnd.uniform(-1.6, 1.6) * s
        star(c, x, y, rnd.uniform(0.12, 0.3) * s, fill=0, stroke=1)


def draw_drum(c, cx, cy, s):
    """Musaharati drum + stick."""
    colouring_setup(c)
    c.ellipse(cx - 1.2 * s, cy + 0.5 * s, cx + 1.2 * s, cy + 0.9 * s)
    c.line(cx - 1.2 * s, cy + 0.7 * s, cx - 1.2 * s, cy - 0.8 * s)
    c.line(cx + 1.2 * s, cy + 0.7 * s, cx + 1.2 * s, cy - 0.8 * s)
    p = c.beginPath()
    p.arc(cx - 1.2 * s, cy - 1.0 * s, cx + 1.2 * s, cy - 0.6 * s, 180, 180)
    c.drawPath(p, fill=0, stroke=1)
    for k in range(7):  # zig-zag straps
        x0 = cx - 1.2 * s + k * (2.4 * s / 7)
        c.line(x0, cy + 0.6 * s, x0 + 2.4 * s / 14, cy - 0.75 * s)
        c.line(x0 + 2.4 * s / 14, cy - 0.75 * s, x0 + 2.4 * s / 7, cy + 0.6 * s)
    c.line(cx + 0.6 * s, cy + 1.0 * s, cx + 1.6 * s, cy + 2.0 * s)
    c.circle(cx + 1.65 * s, cy + 2.05 * s, 0.16 * s)


def draw_bubble_text(c, text, cx, cy, size):
    c.saveState()
    c.setStrokeColor(INK)
    c.setLineWidth(2.5)
    t = c.beginText()
    t.setTextRenderMode(1)
    t.setFont("SansBold", size)
    t.setTextOrigin(cx - pdfmetrics.stringWidth(text, "SansBold", size) / 2, cy)
    t.textOut(text)
    c.drawText(t)
    c.restoreState()


# ---------------- puzzles ----------------

def word_search(words, size, seed, letters):
    rnd = random.Random(seed)
    grid = [[None] * size for _ in range(size)]
    dirs = [(1, 0), (0, 1), (1, 1)]
    placed = []
    for w in sorted(words, key=len, reverse=True):
        for _ in range(500):
            dx, dy = rnd.choice(dirs)
            x, y = rnd.randrange(size), rnd.randrange(size)
            cells = [(x + dx * i, y + dy * i) for i in range(len(w))]
            if all(0 <= a < size and 0 <= b < size and grid[b][a] in (None, w[i]) for i, (a, b) in enumerate(cells)):
                for i, (a, b) in enumerate(cells):
                    grid[b][a] = w[i]
                placed.append((w, cells))
                break
        else:
            raise RuntimeError("could not place " + w)
    for row in grid:
        for i, v in enumerate(row):
            if v is None:
                row[i] = rnd.choice(letters)
    return grid, placed


def draw_grid(c, grid, x0, y0, cell, rtl=False, solution=None):
    n = len(grid)
    c.setFont("SansBold", cell * 0.55)
    if solution:
        c.setStrokeColor(GOLD)
        c.setLineWidth(cell * 0.6)
        c.setLineCap(1)
        for _, cells in solution:
            (ax, ay), (bx, by) = cells[0], cells[-1]
            if rtl:
                ax, bx = n - 1 - ax, n - 1 - bx
            c.setStrokeAlpha(0.45)
            c.line(x0 + (ax + .5) * cell, y0 - (ay + .5) * cell, x0 + (bx + .5) * cell, y0 - (by + .5) * cell)
        c.setStrokeAlpha(1)
    c.setFillColor(INK)
    for y in range(n):
        for x in range(n):
            col = n - 1 - x if rtl else x
            c.drawCentredString(x0 + (col + .5) * cell, y0 - (y + .5) * cell - cell * 0.2, grid[y][x])
    c.setStrokeColor(SOFT)
    c.setLineWidth(1)
    c.rect(x0, y0 - n * cell, n * cell, n * cell)


def make_maze(cols, rows, seed):
    rnd = random.Random(seed)
    walls = {(x, y): {"N", "S", "E", "W"} for x in range(cols) for y in range(rows)}
    dirs = {"N": (0, -1, "S"), "S": (0, 1, "N"), "E": (1, 0, "W"), "W": (-1, 0, "E")}
    stack, seen, parent = [(0, 0)], {(0, 0)}, {}
    while stack:
        x, y = stack[-1]
        opts = [(d, x + dx, y + dy, o) for d, (dx, dy, o) in dirs.items() if (x + dx, y + dy) in walls and (x + dx, y + dy) not in seen]
        if not opts:
            stack.pop()
            continue
        d, nx, ny, o = rnd.choice(opts)
        walls[(x, y)].discard(d); walls[(nx, ny)].discard(o)
        seen.add((nx, ny)); parent[(nx, ny)] = (x, y); stack.append((nx, ny))
    path, node = [], (cols - 1, rows - 1)
    while node != (0, 0):
        path.append(node); node = parent[node]
    return walls, [(0, 0)] + path[::-1]


def draw_maze(c, walls, cols, rows, box, path=None):
    x0, y0, w, h = box
    cell = min(w / cols, h / rows)
    ox, oy = x0 + (w - cell * cols) / 2, y0 + (h + cell * rows) / 2
    px, py = (lambda x: ox + x * cell), (lambda y: oy - y * cell)
    c.setStrokeColor(INK); c.setLineWidth(max(1.5, cell / 9)); c.setLineCap(1)
    for (x, y), ws in walls.items():
        if "N" in ws and (x, y) != (0, 0): c.line(px(x), py(y), px(x + 1), py(y))
        if "W" in ws: c.line(px(x), py(y), px(x), py(y + 1))
        if "S" in ws and (x, y) != (cols - 1, rows - 1): c.line(px(x), py(y + 1), px(x + 1), py(y + 1))
        if "E" in ws: c.line(px(x + 1), py(y), px(x + 1), py(y + 1))
    if path:
        c.setStrokeColor(GOLD); c.setLineWidth(max(2, cell / 4))
        p = c.beginPath(); p.moveTo(px(.5), py(0) + 4)
        for x, y in path: p.lineTo(px(x + .5), py(y + .5))
        p.lineTo(px(cols - .5), py(rows) - 4)
        c.drawPath(p, stroke=1, fill=0)
    return px(.5), py(0), px(cols - .5), py(rows)


# ---------------- pages ----------------

def cover(b):
    c = b.c
    b.page(NAVY, footer=False)
    c.setFillColor(NAVY)
    c.roundRect(22, 22, W - 44, H - 44, 20, fill=1, stroke=0)
    rnd = random.Random(3)
    c.setFillColor(GOLD)
    for _ in range(45):
        star(c, rnd.uniform(40, W - 40), rnd.uniform(40, H - 40), rnd.uniform(3, 8))
    c.setFillColor(HexColor("#FDE68A"))
    crescent(c, W - 150, H - 160, 70)
    c.setFillColor(white)
    c.setFont("SansBold", 48)
    c.drawCentredString(W / 2, H / 2 + 110, "Ramadan & Eid")
    c.setFont("SansBold", 30)
    c.drawCentredString(W / 2, H / 2 + 65, "Kids Activity Pack")
    c.setFillColor(HexColor("#FDE68A"))
    c.setFont("SansBold", 32)
    c.drawCentredString(W / 2, H / 2 + 5, ar("نشاطات رمضان والعيد للأطفال"))
    c.setFillColor(white)
    c.setFont("Sans", 15)
    c.drawCentredString(W / 2, H / 2 - 40, "Good-deeds calendar · Prayer & Quran trackers · Colouring")
    c.drawCentredString(W / 2, H / 2 - 62, "Word searches · Mazes · Journal · Bunting · Eid cards & gift tags")
    c.drawCentredString(W / 2, H / 2 - 92, "Ages 4–10 · Arabic + English · Print at home")
    c.saveState()
    c.translate(W / 2 - 160, 150)
    draw_lantern(c, 0, 0, 38)
    c.restoreState()
    c.saveState()
    c.translate(W / 2 + 160, 150)
    draw_lantern(c, 0, 0, 38)
    c.restoreState()


def how_to(b):
    c = b.c
    a = b.page()
    header(c, "Welcome!", "أهلاً وسهلاً", a)
    c.setFillColor(INK)
    c.setFont("Sans", 11.5)
    lines = [
        "• Print on US Letter or A4 (choose 'Fit to page'). Card stock works best for bunting & cards.",
        "• Pin the Good Deeds Calendar on the fridge: colour one lantern for each day of Ramadan.",
        "• Use the Prayer and Quran trackers to build gentle daily habits. Stars, not stress!",
        "• Cut out the 30 Good Deeds cards, fold them and put them in a jar. Pick one each day.",
        "• Colouring pages, word searches and mazes are great quiet time before iftar.",
        "• Before Eid: make the bunting, write the Eid cards and add gift tags to the presents.",
        "• Answer keys are at the back. Eid Mubarak to your family!",
    ]
    y = H - 150
    for ln in lines:
        c.drawString(M + 10, y, ln)
        y -= 30
    c.setFont("SansBold", 18)
    for t in ("اطبع الصفحات على ورق عادي أو مقوّى", "علّقوا تقويم الحسنات على البراد ولوّنوا فانوس كل يوم",
              "قصّوا بطاقات الحسنات واسحبوا وحدة كل يوم", "عيد مبارك وكل عام وأنتم بخير"):
        c.drawRightString(W - M - 10, y - 10, ar(t))
        y -= 34
    c.setFont("Sans", 9)
    c.setFillColor(SOFT)
    c.drawCentredString(W / 2, 60, "© Little Learners Studio · personal & single-classroom use · do not resell or share the file")


def calendar(b):
    c = b.c
    a = b.page(GOLD)
    header(c, "30 Days of Good Deeds", "ثلاثون يوماً من الحسنات", a)
    c.setFont("Sans", 12)
    c.setFillColor(INK)
    c.drawCentredString(W / 2, H - 125, "Colour a lantern every day you do a good deed!  ·  " + ar("لوّن فانوساً كل يوم تعمل فيه عملاً طيباً"))
    cols, rows = 5, 6
    cw, ch = (W - 2 * M) / cols, (H - 230) / rows
    for i in range(30):
        x = M + (i % cols) * cw
        y = H - 150 - (i // cols + 1) * ch
        c.setStrokeColor(SOFT)
        c.setLineWidth(1.5)
        c.roundRect(x + 4, y + 4, cw - 8, ch - 8, 10)
        c.setFillColor(a)
        c.setFont("SansBold", 13)
        c.drawString(x + 12, y + ch - 24, str(i + 1))
        c.saveState()
        c.translate(x + cw / 2, y + ch / 2 - 6)
        draw_lantern(c, 0, 0, ch / 7.2)
        c.restoreState()


def prayer_tracker(b):
    c = b.c
    a = b.page(ACC[2])
    header(c, "My Prayer Tracker", "متابعة صلواتي", a)
    prayers = [("Fajr", "الفجر"), ("Dhuhr", "الظهر"), ("Asr", "العصر"), ("Maghrib", "المغرب"), ("Isha", "العشاء")]
    top, left = H - 150, M + 110
    cw = (W - left - M) / 5
    rh = (top - 70) / 31
    c.setFont("SansBold", 10)
    for j, (en, a_) in enumerate(prayers):
        c.setFillColor(INK)
        c.drawCentredString(left + (j + .5) * cw, top + 8, en)
        c.drawCentredString(left + (j + .5) * cw, top - 6, ar(a_))
    for i in range(30):
        y = top - (i + 1.5) * rh
        c.setFillColor(INK)
        c.setFont("Sans", 10)
        c.drawString(M + 10, y - 3, f"Day {i + 1}")
        c.drawRightString(left - 10, y - 3, ar(f"يوم {i + 1}"))
        for j in range(5):
            c.setStrokeColor(SOFT)
            c.setLineWidth(1)
            star(c, left + (j + .5) * cw, y, rh * 0.42, fill=0, stroke=1)


def quran_tracker(b):
    c = b.c
    a = b.page(ACC[3])
    header(c, "My Quran Journey", "رحلتي مع القرآن", a)
    c.setFont("Sans", 12)
    c.setFillColor(INK)
    c.drawCentredString(W / 2, H - 125, "Colour a moon for each part (juz') or surah you read or listen to.")
    cols = 5
    r = 34
    for i in range(30):
        x = M + 50 + (i % cols) * ((W - 2 * M - 100) / (cols - 1))
        y = H - 200 - (i // cols) * 95
        c.setStrokeColor(INK)
        c.setLineWidth(2)
        c.setFillColor(white)
        c.circle(x, y, r, fill=0, stroke=1)
        c.setFont("SansBold", 16)
        c.setFillColor(a)
        c.drawCentredString(x, y - 6, str(i + 1))


COLOURING = [
    ("Ramadan Lantern", "فانوس رمضان", draw_lantern, 95),
    ("The Mosque", "المسجد", draw_mosque, 85),
    ("Crescent Moon & Stars", "الهلال والنجوم", draw_moon_stars, 110),
    ("Eid Gift", "هدية العيد", draw_gift, 110),
    ("The Musaharati Drum", "طبلة المسحراتي", draw_drum, 95),
]


def colouring_pages(b):
    c = b.c
    for en, a_, fn, s in COLOURING:
        a = b.page()
        header(c, en, a_, a)
        fn(c, W / 2, H / 2 - 20, s)
    a = b.page(GOLD)
    header(c, "Colour the words!", "لوّن الكلمات", a)
    draw_bubble_text(c, "Ramadan", W / 2, H - 260, 92)
    draw_bubble_text(c, "Kareem", W / 2, H - 380, 92)
    draw_bubble_text(c, ar("رمضان كريم"), W / 2, H - 530, 100)
    draw_bubble_text(c, "Eid Mubarak", W / 2, 110, 70)


EN_WORDS = ["RAMADAN", "FASTING", "IFTAR", "SUHOOR", "LANTERN", "MOON", "DATES", "QURAN", "PRAYER", "CHARITY", "EID", "FAMILY"]
AR_WORDS = ["رمضان", "صيام", "افطار", "سحور", "فانوس", "هلال", "تمر", "قران", "صلاة", "صدقة", "عيد", "اسرة"]
AR_FILL = list("ابتثجحخدذرزسشصضطظعغفقكلمنهوي")


def word_searches(b):
    c = b.c
    out = []
    for lang, words, letters, seed in (("en", EN_WORDS, list("ABCDEFGHIJKLMNOPRSTUWY"), 11), ("ar", AR_WORDS, AR_FILL, 12)):
        grid, placed = word_search(words, 12, seed, letters)
        out.append((lang, grid, placed))
        a = b.page()
        header(c, "Word Search", "البحث عن الكلمات", a)
        cell = 34
        x0 = (W - 12 * cell) / 2
        draw_grid(c, grid, x0, H - 140, cell, rtl=lang == "ar")
        c.setFont("SansBold", 14)
        c.setFillColor(INK)
        for i, w in enumerate(words):
            x = M + 30 + (i % 4) * ((W - 2 * M - 60) / 4)
            y = H - 140 - 12 * cell - 40 - (i // 4) * 26
            label = w if lang == "en" else ar(w)
            c.drawString(x, y, "☐ " + label if lang == "en" else label + "  ☐")
        c.setFont("Sans", 10)
        c.setFillColor(SOFT)
        c.drawCentredString(W / 2, 60, "Words go across, down or diagonally." if lang == "en" else ar("الكلمات أفقية أو عمودية أو مائلة") + "  ·  letters are shown unjoined")
    return out


def mazes(b):
    c = b.c
    out = []
    for i, (cols, rows, en, a_) in enumerate(((9, 11, "Help the lantern reach the mosque!", "ساعد الفانوس يوصل للمسجد"),
                                              (13, 16, "Find the way to the Eid gift!", "لاقي الطريق لهدية العيد"))):
        walls, path = make_maze(cols, rows, 40 + i)
        out.append((walls, cols, rows, path))
        a = b.page()
        header(c, f"Maze {i + 1}", f"متاهة {i + 1}", a)
        c.setFont("Sans", 12)
        c.setFillColor(INK)
        c.drawCentredString(W / 2, H - 125, en + "  ·  " + ar(a_))
        sx, sy, ex, ey = draw_maze(c, walls, cols, rows, (M + 30, 120, W - 2 * M - 60, H - 330))
        c.saveState(); c.translate(sx, sy + 32); draw_lantern(c, 0, 0, 11); c.restoreState()
        c.saveState(); c.translate(ex, ey - 30); (draw_mosque if i == 0 else draw_gift)(c, 0, 0, 10); c.restoreState()
    return out


def journal(b):
    c = b.c
    for en_title, ar_title, prompts in (
        ("My Ramadan Journal", "مذكراتي في رمضان", ["Today I am thankful for…", "A good deed I did today…", "My favourite iftar food…", "Something new I learned…", "My dua for my family…"]),
        ("My Eid Day", "يوم العيد", ["On Eid morning I…", "I wore…", "I visited…", "My favourite Eid gift / treat…", "Draw your Eid day!"]),
    ):
        a = b.page()
        header(c, en_title, ar_title, a)
        y = H - 150
        for p in prompts:
            c.setFont("SansBold", 13)
            c.setFillColor(a)
            c.drawString(M + 10, y, p)
            c.setStrokeColor(SOFT)
            c.setLineWidth(1)
            for k in range(2 if p.startswith("Draw") is False else 0):
                c.line(M + 10, y - 26 - k * 26, W - M - 10, y - 26 - k * 26)
            y -= 95
        if en_title == "My Eid Day":
            c.setDash(6, 4)
            c.roundRect(M + 10, 70, W - 2 * M - 20, y + 60 - 70, 12)
            c.setDash()


DEEDS = [("Help set the iftar table", "ساعد بتحضير سفرة الإفطار"), ("Give a hug to your parents", "اعطِ أهلك حضن"),
         ("Share a toy", "شارك لعبتك"), ("Say something kind", "قل كلمة طيبة"), ("Give charity", "تصدّق"),
         ("Read a short surah", "اقرأ سورة قصيرة"), ("Smile at everyone", "ابتسم للجميع"), ("Tidy your room", "رتّب غرفتك"),
         ("Call your grandparents", "اتصل بجدك وجدتك"), ("Feed a bird or cat", "أطعم عصفوراً أو قطة"),
         ("Make dua for a friend", "ادعُ لصديقك"), ("Help wash the dishes", "ساعد بغسل الصحون"),
         ("Say thank you 5 times", "قل شكراً خمس مرات"), ("Water a plant", "اسقِ نبتة"), ("Make a card for someone", "اصنع بطاقة لأحد"),
         ("Pick up litter", "التقط القمامة"), ("Share your dates", "شارك تمرك"), ("Be patient today", "كن صبوراً اليوم"),
         ("Learn a new dua", "تعلّم دعاء جديد"), ("Help a sibling", "ساعد أخاك أو أختك"), ("Visit a neighbour", "زُر جارك"),
         ("Give your old clothes", "تبرّع بملابسك القديمة"), ("Say salam first", "ابدأ بالسلام"), ("No complaining today", "بلا تذمّر اليوم"),
         ("Pray on time", "صلِّ على الوقت"), ("Draw a picture for mum", "ارسم صورة لماما"), ("Help cook suhoor", "ساعد بتحضير السحور"),
         ("Forgive someone", "سامح أحداً"), ("Listen without interrupting", "استمع دون مقاطعة"), ("Thank Allah for 3 things", "احمد ربك على ثلاث نعم")]


def deeds_cards(b):
    c = b.c
    for page in range(2):
        a = b.page(GOLD)
        header(c, "Good Deeds Jar Cards", "بطاقات مرطبان الحسنات", a)
        cols, rows = 3, 5
        cw, ch = (W - 2 * M) / cols, (H - 200) / rows
        c.setDash(5, 4)
        for i in range(15):
            n = page * 15 + i
            en, a_ = DEEDS[n]
            x = M + (i % cols) * cw
            y = H - 140 - (i // cols + 1) * ch
            c.setStrokeColor(SOFT)
            c.rect(x, y, cw, ch)
            c.setFillColor(ACC[n % len(ACC)])
            star(c, x + 18, y + ch - 18, 8)
            c.setFillColor(INK)
            fs = 10.5
            while pdfmetrics.stringWidth(en, "SansBold", fs) > cw - 16:
                fs -= 0.5
            c.setFont("SansBold", fs)
            c.drawCentredString(x + cw / 2, y + ch / 2 + 8, en)
            c.setFont("SansBold", 13)
            c.drawCentredString(x + cw / 2, y + ch / 2 - 16, ar(a_))
        c.setDash()
    # jar label
    a = b.page()
    header(c, "Jar Label", "ملصق المرطبان", a)
    c.setStrokeColor(INK)
    c.setLineWidth(3)
    c.roundRect(M + 40, H / 2 - 120, W - 2 * M - 80, 240, 30)
    c.setFillColor(INK)
    c.setFont("SansBold", 40)
    c.drawCentredString(W / 2, H / 2 + 30, "My Good Deeds Jar")
    c.setFont("SansBold", 40)
    c.drawCentredString(W / 2, H / 2 - 40, ar("مرطبان حسناتي"))
    c.setFillColor(GOLD)
    for k in range(5):
        star(c, W / 2 + (k - 2) * 50, H / 2 - 90, 12)


def bunting(b):
    c = b.c
    pennants = list("RAMADAN") + ["★"] + list("KAREEM") + [ar("رمضان"), ar("كريم"), ar("عيد"), ar("مبارك")]
    for i in range(0, len(pennants), 2):
        a = b.page(footer=False)
        for j, txt in enumerate(pennants[i:i + 2]):
            x0 = M + j * (W - 2 * M) / 2
            w = (W - 2 * M) / 2 - 10
            top = H - 80
            col = ACC[(i + j) % len(ACC)]
            c.setStrokeColor(col)
            c.setLineWidth(3)
            p = c.beginPath()
            p.moveTo(x0, top); p.lineTo(x0 + w, top); p.lineTo(x0 + w / 2, 120); p.close()
            c.drawPath(p, fill=0, stroke=1)
            c.setDash(4, 4)
            c.setStrokeColor(SOFT)
            c.line(x0, top - 25, x0 + w, top - 25)
            c.setDash()
            c.setFont("Sans", 8)
            c.setFillColor(SOFT)
            c.drawCentredString(x0 + w / 2, top - 18, "fold & glue over string")
            if txt == "★":
                c.setFillColor(GOLD)
                star(c, x0 + w / 2, top - 200, 60)
            else:
                size = 150 if len(txt) == 1 else 70
                draw_bubble_text(c, txt, x0 + w / 2, top - 250, size)


def eid_cards(b):
    c = b.c
    a = b.page(footer=False)
    msgs = [("Eid Mubarak!", "عيد مبارك"), ("Happy Eid!", "عيد سعيد"), ("Eid Mubarak!", "كل عام وأنتم بخير"), ("With love", "مع حبي")]
    cw, ch = (W - 2 * M) / 2, (H - 2 * M) / 2
    c.setDash(5, 4)
    for i, (en, a_) in enumerate(msgs):
        x = M + (i % 2) * cw
        y = H - M - (i // 2 + 1) * ch
        c.setStrokeColor(SOFT)
        c.setLineWidth(1)
        c.rect(x, y, cw, ch)
        c.setDash()
        c.saveState()
        c.translate(x + cw / 2, y + ch / 2 + 40)
        (draw_lantern if i % 2 == 0 else draw_moon_stars)(c, 0, 0, 30 if i % 2 == 0 else 28)
        c.restoreState()
        c.setFillColor(INK)
        c.setFont("SansBold", 20)
        c.drawCentredString(x + cw / 2, y + 70, en)
        c.drawCentredString(x + cw / 2, y + 42, ar(a_))
        c.setFont("Sans", 10)
        c.drawCentredString(x + cw / 2, y + 18, "To: ____________   From: ____________")
        c.setDash(5, 4)
    c.setDash()


def gift_tags(b):
    c = b.c
    a = b.page(footer=False)
    cols, rows = 2, 4
    cw, ch = (W - 2 * M) / cols, (H - 2 * M) / rows
    for i in range(8):
        x = M + (i % cols) * cw + 15
        y = H - M - (i // cols + 1) * ch + 12
        w, h = cw - 30, ch - 24
        col = ACC[i % len(ACC)]
        c.setStrokeColor(col)
        c.setLineWidth(3)
        p = c.beginPath()
        p.moveTo(x + 40, y); p.lineTo(x + w, y); p.lineTo(x + w, y + h); p.lineTo(x + 40, y + h); p.lineTo(x, y + h / 2); p.close()
        c.drawPath(p, fill=0, stroke=1)
        c.circle(x + 22, y + h / 2, 7)
        c.setFillColor(INK)
        c.setFont("SansBold", 18)
        c.drawCentredString(x + w / 2 + 20, y + h - 40, "Eid Mubarak")
        c.drawCentredString(x + w / 2 + 20, y + h - 66, ar("عيد مبارك"))
        c.setFont("Sans", 11)
        c.drawString(x + 60, y + 35, "To: ______________")
        c.drawString(x + 60, y + 14, "From: ____________")


def certificate(b):
    c = b.c
    b.page(GOLD, footer=False)
    c.setFillColor(INK)
    c.setFont("SansBold", 40)
    c.drawCentredString(W / 2, H - 170, "Ramadan Star Award")
    c.setFont("SansBold", 32)
    c.drawCentredString(W / 2, H - 220, ar("نجم رمضان"))
    c.setFont("Sans", 16)
    c.drawCentredString(W / 2, H - 290, "This award is proudly given to")
    c.line(W / 2 - 180, H - 360, W / 2 + 180, H - 360)
    c.drawCentredString(W / 2, H - 410, "for fasting, praying, and doing good deeds all Ramadan!")
    c.drawCentredString(W / 2, H - 440, ar("للصيام والصلاة وفعل الخير طوال شهر رمضان!"))
    c.setFillColor(GOLD)
    star(c, W / 2, H - 560, 60)
    c.setFillColor(INK)
    c.setFont("Sans", 13)
    c.drawString(110, 120, "Date: ______________")
    c.drawRightString(W - 110, 120, "Signed: ______________")


def answers(b, ws, mz):
    c = b.c
    a = b.page()
    header(c, "Answer Keys", "الحلول", a)
    cell = 17
    for k, (lang, grid, placed) in enumerate(ws):
        draw_grid(c, grid, M + 20 + k * (W - 2 * M) / 2, H - 150, cell, rtl=lang == "ar", solution=placed)
    for k, (walls, cols, rows, path) in enumerate(mz):
        draw_maze(c, walls, cols, rows, (M + 20 + k * (W - 2 * M) / 2, 80, (W - 2 * M) / 2 - 40, 330), path)


def build(out_dir):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    b = Book(out / "Ramadan-Eid-Kids-Activity-Pack.pdf")
    cover(b); how_to(b); calendar(b); prayer_tracker(b); quran_tracker(b)
    colouring_pages(b)
    ws = word_searches(b)
    mz = mazes(b)
    journal(b); deeds_cards(b); bunting(b); eid_cards(b); gift_tags(b); certificate(b)
    answers(b, ws, mz)
    b.c.save()
    print("pages:", b.n)


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "product")
