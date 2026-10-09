"""Generate the "Little Learners" bilingual (Arabic + English) kids activity workbook PDF.

Usage: python3 build_workbook.py <output_dir>
"""
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
M = 50  # margin
INK = HexColor("#1F2A44")
TRACE = HexColor("#9AA5B8")
ACCENTS = [HexColor(c) for c in ("#FF6B6B", "#FFA94D", "#FFD43B", "#69DB7C", "#4DABF7", "#9775FA", "#F783AC")]

EN_WORDS = {
    "A": "Apple", "B": "Ball", "C": "Cat", "D": "Dog", "E": "Egg", "F": "Fish", "G": "Goat",
    "H": "Hat", "I": "Ice cream", "J": "Juice", "K": "Kite", "L": "Lion", "M": "Moon",
    "N": "Nest", "O": "Owl", "P": "Pig", "Q": "Queen", "R": "Rain", "S": "Sun", "T": "Tree",
    "U": "Umbrella", "V": "Van", "W": "Whale", "X": "Box", "Y": "Yo-yo", "Z": "Zebra",
}
AR_LETTERS = [
    ("ا", "ألف", "أرنب", "Rabbit"), ("ب", "باء", "بطة", "Duck"), ("ت", "تاء", "تفاحة", "Apple"),
    ("ث", "ثاء", "ثعلب", "Fox"), ("ج", "جيم", "جمل", "Camel"), ("ح", "حاء", "حصان", "Horse"),
    ("خ", "خاء", "خروف", "Sheep"), ("د", "دال", "دب", "Bear"), ("ذ", "ذال", "ذرة", "Corn"),
    ("ر", "راء", "رمان", "Pomegranate"), ("ز", "زاي", "زرافة", "Giraffe"), ("س", "سين", "سمكة", "Fish"),
    ("ش", "شين", "شمس", "Sun"), ("ص", "صاد", "صقر", "Falcon"), ("ض", "ضاد", "ضفدع", "Frog"),
    ("ط", "طاء", "طائرة", "Plane"), ("ظ", "ظاء", "ظرف", "Envelope"), ("ع", "عين", "عصفور", "Bird"),
    ("غ", "غين", "غيمة", "Cloud"), ("ف", "فاء", "فيل", "Elephant"), ("ق", "قاف", "قطة", "Cat"),
    ("ك", "كاف", "كرة", "Ball"), ("ل", "لام", "ليمون", "Lemon"), ("م", "ميم", "موز", "Banana"),
    ("ن", "نون", "نحلة", "Bee"), ("ه", "هاء", "هدية", "Gift"), ("و", "واو", "وردة", "Flower"),
    ("ي", "ياء", "يد", "Hand"),
]
NUM_AR = ["٠", "١", "٢", "٣", "٤", "٥", "٦", "٧", "٨", "٩", "١٠"]
NUM_EN_WORD = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"]
NUM_AR_WORD = ["صفر", "واحد", "اثنان", "ثلاثة", "أربعة", "خمسة", "ستة", "سبعة", "ثمانية", "تسعة", "عشرة"]


def ar(text):
    return get_display(arabic_reshaper.reshape(text))


class Book:
    def __init__(self, path, title):
        self.c = canvas.Canvas(str(path), pagesize=letter)
        self.c.setTitle(title)
        self.c.setAuthor("Little Learners Studio")
        self.page = 0

    def new_page(self, accent=None, footer=True):
        if self.page:
            self.c.showPage()
        self.page += 1
        accent = accent or ACCENTS[self.page % len(ACCENTS)]
        c = self.c
        c.setStrokeColor(accent)
        c.setLineWidth(6)
        c.roundRect(20, 20, W - 40, H - 40, 24)
        if footer:
            c.setFont("Sans", 9)
            c.setFillColor(TRACE)
            c.drawCentredString(W / 2, 30, f"Little Learners · {self.page}")
            c.drawString(M, 30, "Name: ________________")
        return accent

    def save(self):
        self.c.save()


def header(c, text, accent, size=30, y=None):
    y = y or H - 85
    c.setFillColor(accent)
    c.roundRect(M, y - 14, W - 2 * M, size + 22, 16, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("SansBold", size)
    c.drawCentredString(W / 2, y, text)


def trace_text(c, text, x, y, size, centred=False, font="SansBold"):
    """Dashed outline text the child traces over."""
    c.saveState()
    c.setStrokeColor(TRACE)
    c.setLineWidth(1.6)
    c.setDash(4, 3)
    t = c.beginText()
    t.setTextRenderMode(1)
    t.setFont(font, size)
    if centred:
        x -= pdfmetrics.stringWidth(text, font, size) / 2
    t.setTextOrigin(x, y)
    t.textOut(text)
    c.drawText(t)
    c.restoreState()


def guide_lines(c, y, height, left=M + 10, right=W - M - 10):
    c.saveState()
    c.setStrokeColor(HexColor("#C9D3E3"))
    c.setLineWidth(1)
    c.line(left, y, right, y)
    c.line(left, y + height, right, y + height)
    c.setDash(3, 4)
    c.line(left, y + height / 2, right, y + height / 2)
    c.restoreState()


def draw_box(c, label, y=110, h=150):
    c.saveState()
    c.setStrokeColor(HexColor("#C9D3E3"))
    c.setDash(6, 4)
    c.setLineWidth(1.5)
    c.roundRect(M + 10, y, W - 2 * M - 20, h, 14)
    c.setFont("Sans", 11)
    c.setFillColor(TRACE)
    c.drawCentredString(W / 2, y + h - 18, label)
    c.restoreState()


# ---------- sections ----------

def cover(b):
    c = b.c
    b.new_page(ACCENTS[4], footer=False)
    for i in range(40):
        c.setFillColor(ACCENTS[i % len(ACCENTS)])
        rnd = random.Random(i)
        c.circle(rnd.uniform(40, W - 40), rnd.uniform(40, H - 40), rnd.uniform(4, 14), fill=1, stroke=0)
    c.setFillColor(white)
    c.roundRect(M, H / 2 - 150, W - 2 * M, 330, 30, fill=1, stroke=0)
    c.setFillColor(INK)
    c.setFont("SansBold", 40)
    c.drawCentredString(W / 2, H / 2 + 120, "Little Learners")
    c.setFont("Sans", 20)
    c.drawCentredString(W / 2, H / 2 + 85, "Arabic + English Activity Workbook")
    c.setFont("SansBold", 34)
    c.drawCentredString(W / 2, H / 2 + 25, ar("كتاب نشاطات الحروف والأرقام"))
    c.setFont("Sans", 15)
    c.drawCentredString(W / 2, H / 2 - 25, "A–Z  ·  Arabic Alif–Ya  ·  Numbers 0–10  ·  20 Mazes")
    c.drawCentredString(W / 2, H / 2 - 50, "Ages 3–6  ·  Print at home, use again and again")
    c.setFont("SansBold", 60)
    for i, ch in enumerate(["A", ar("ب"), "3", ar("ج"), "Z"]):
        c.setFillColor(ACCENTS[i])
        c.drawCentredString(W / 2 + (i - 2) * 90, H / 2 - 125, ch)


def how_to(b):
    c = b.c
    accent = b.new_page()
    header(c, "How to use this book", accent, 24)
    lines = [
        "1. Print single-sided on regular US Letter or A4 paper (choose 'Fit to page').",
        "2. Trace the dashed letters slowly, starting from the top.",
        "3. Say the letter sound and the word out loud together.",
        "4. Draw the picture in the box — creativity counts more than neatness!",
        "5. Do 1–2 pages a day. Short, happy sessions beat long ones.",
        "6. Tip: slide pages into a plastic sleeve and use a dry-erase marker to reuse.",
        "7. Finish the book? Award the certificate on the last page!",
    ]
    c.setFillColor(INK)
    c.setFont("Sans", 14)
    y = H - 150
    for line in lines:
        c.drawString(M + 10, y, line)
        y -= 32
    c.setFont("SansBold", 18)
    c.drawRightString(W - M - 10, y - 20, ar("للأهل: صفحة أو صفحتين يومياً تكفي"))
    c.setFont("Sans", 10)
    c.setFillColor(TRACE)
    c.drawCentredString(W / 2, 70, "© Little Learners Studio. Personal & single-classroom use. Do not resell or redistribute.")


def english_pages(b):
    c = b.c
    for i, (L, word) in enumerate(EN_WORDS.items()):
        accent = b.new_page(ACCENTS[i % len(ACCENTS)])
        header(c, f"{L} {L.lower()}   —   {L} is for {word}", accent, 26)
        trace_text(c, L, W / 2 - 110, H - 330, 200, centred=True)
        trace_text(c, L.lower(), W / 2 + 110, H - 330, 200, centred=True)
        # tracing rows
        for row, text in enumerate([L, L.lower(), word]):
            y = H - 420 - row * 75
            guide_lines(c, y, 44)
            size = 44
            step = pdfmetrics.stringWidth(text + "  ", "SansBold", size)
            x = M + 20
            while x + pdfmetrics.stringWidth(text, "SansBold", size) < W - M - 10:
                trace_text(c, text, x, y + 2, size)
                x += step
                if row == 2:
                    break
        draw_box(c, f"Draw a {word.lower()}!", y=70, h=150)


def arabic_pages(b):
    c = b.c
    for i, (letter_, name, word, meaning) in enumerate(AR_LETTERS):
        accent = b.new_page(ACCENTS[i % len(ACCENTS)])
        c.setFillColor(accent)
        c.roundRect(M, H - 99, W - 2 * M, 56, 16, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("SansBold", 26)
        c.drawCentredString(W / 2, H - 82, ar(f"حرف {name}  —  {letter_}  —  {word}"))
        trace_text(c, letter_, W / 2, H - 340, 230, centred=True)
        c.setFont("Sans", 12)
        c.setFillColor(TRACE)
        c.drawCentredString(W / 2, H - 365, f"{meaning}  =  " + ar(word))
        for row in range(2):
            y = H - 450 - row * 80
            guide_lines(c, y, 48)
            x = W - M - 70
            while x > M + 20:
                trace_text(c, letter_, x, y + 6, 46)
                x -= 70
        y = H - 610
        guide_lines(c, y, 48)
        trace_text(c, ar(word), W - M - 30 - pdfmetrics.stringWidth(ar(word), "SansBold", 46), y + 6, 46)
        draw_box(c, f"Draw: {meaning}", y=70, h=110)


def number_pages(b):
    c = b.c
    for n in range(11):
        accent = b.new_page(ACCENTS[n % len(ACCENTS)])
        header(c, f"{n}  ·  {NUM_EN_WORD[n]}  ·  " + ar(f"{NUM_AR_WORD[n]}  {NUM_AR[n]}"), accent, 26)
        trace_text(c, str(n), W / 2 - 120, H - 320, 190, centred=True)
        trace_text(c, NUM_AR[n], W / 2 + 120, H - 320, 190, centred=True)
        y = H - 410
        guide_lines(c, y, 48)
        x = M + 20
        while x < W - M - 60:
            trace_text(c, str(n), x, y + 6, 46)
            x += 60
        c.setFillColor(INK)
        c.setFont("Sans", 14)
        c.drawCentredString(W / 2, H - 450, f"Colour {n} circle{'s' if n != 1 else ''}!   " + ar(f"لوّن {NUM_AR[n]}"))
        c.setStrokeColor(INK)
        c.setLineWidth(2)
        for k in range(10):
            cx = M + 50 + (k % 5) * ((W - 2 * M - 100) / 4)
            cy = H - 500 - (k // 5) * 70
            c.circle(cx, cy, 28)
        draw_box(c, f"Draw {n} of something you love", y=70, h=120)


def make_maze(cols, rows, seed):
    rnd = random.Random(seed)
    walls = {(x, y): {"N", "S", "E", "W"} for x in range(cols) for y in range(rows)}
    dirs = {"N": (0, -1, "S"), "S": (0, 1, "N"), "E": (1, 0, "W"), "W": (-1, 0, "E")}
    stack, seen, parent = [(0, 0)], {(0, 0)}, {}
    while stack:
        x, y = stack[-1]
        options = [(d, x + dx, y + dy, opp) for d, (dx, dy, opp) in dirs.items()
                   if (x + dx, y + dy) in walls and (x + dx, y + dy) not in seen]
        if not options:
            stack.pop()
            continue
        d, nx, ny, opp = rnd.choice(options)
        walls[(x, y)].discard(d)
        walls[(nx, ny)].discard(opp)
        seen.add((nx, ny))
        parent[(nx, ny)] = (x, y)
        stack.append((nx, ny))
    path, node = [], (cols - 1, rows - 1)
    while node != (0, 0):
        path.append(node)
        node = parent[node]
    path.append((0, 0))
    return walls, path[::-1]


def draw_maze(c, walls, cols, rows, box, path=None):
    x0, y0, w, h = box
    cell = min(w / cols, h / rows)
    ox = x0 + (w - cell * cols) / 2
    oy = y0 + (h + cell * rows) / 2  # top edge
    px = lambda x: ox + x * cell
    py = lambda y: oy - y * cell
    c.setStrokeColor(INK)
    c.setLineWidth(max(1.5, cell / 10))
    c.setLineCap(1)
    for (x, y), ws in walls.items():
        if "N" in ws and (x, y) != (0, 0):
            c.line(px(x), py(y), px(x + 1), py(y))
        if "W" in ws:
            c.line(px(x), py(y), px(x), py(y + 1))
        if "S" in ws and (x, y) != (cols - 1, rows - 1):
            c.line(px(x), py(y + 1), px(x + 1), py(y + 1))
        if "E" in ws:
            c.line(px(x + 1), py(y), px(x + 1), py(y + 1))
    c.setFillColor(ACCENTS[3])
    r = min(cell * 0.35, 10)
    c.circle(px(0.5), py(0) + r + 3, r, fill=1, stroke=0)
    c.setFillColor(ACCENTS[0])
    c.circle(px(cols - 0.5), py(rows) - r - 3, r, fill=1, stroke=0)
    if path:
        c.setStrokeColor(ACCENTS[0])
        c.setLineWidth(max(2, cell / 5))
        p = c.beginPath()
        p.moveTo(px(0.5), py(0) + r + 3)
        for x, y in path:
            p.lineTo(px(x + 0.5), py(y + 0.5))
        p.lineTo(px(cols - 0.5), py(rows) - r - 3)
        c.drawPath(p, stroke=1, fill=0)


def maze_pages(b):
    c = b.c
    mazes = []
    for i in range(20):
        size = 5 + i // 2  # gets harder: 5x5 -> 14x14
        cols, rows = size, int(size * 1.25)
        walls, path = make_maze(cols, rows, seed=1000 + i)
        mazes.append((walls, cols, rows, path))
        accent = b.new_page(ACCENTS[i % len(ACCENTS)])
        header(c, f"Maze {i + 1}  ·  " + ar(f"متاهة {i + 1}"), accent, 24)
        c.setFont("Sans", 12)
        c.setFillColor(INK)
        c.drawCentredString(W / 2, H - 120, "Help the green ball reach the red ball!")
        draw_maze(c, walls, cols, rows, (M + 20, 100, W - 2 * M - 40, H - 280))
    # answer key: 4 per page
    for start in range(0, 20, 4):
        accent = b.new_page()
        header(c, f"Answers: Mazes {start + 1}–{start + 4}", accent, 20)
        for k in range(4):
            walls, cols, rows, path = mazes[start + k]
            bx = M + (k % 2) * ((W - 2 * M) / 2) + 10
            by = 80 + (1 - k // 2) * ((H - 220) / 2)
            draw_maze(c, walls, cols, rows, (bx, by, (W - 2 * M) / 2 - 20, (H - 260) / 2), path)


def certificate(b):
    c = b.c
    b.new_page(ACCENTS[2], footer=False)
    c.setStrokeColor(ACCENTS[5])
    c.setLineWidth(3)
    c.roundRect(50, 50, W - 100, H - 100, 20)
    c.setFillColor(INK)
    c.setFont("SansBold", 38)
    c.drawCentredString(W / 2, H - 180, "Certificate of Awesome!")
    c.setFont("SansBold", 30)
    c.drawCentredString(W / 2, H - 230, ar("شهادة تميّز"))
    c.setFont("Sans", 16)
    c.drawCentredString(W / 2, H - 300, "This certificate is proudly given to")
    c.line(W / 2 - 180, H - 370, W / 2 + 180, H - 370)
    c.drawCentredString(W / 2, H - 420, "for finishing the Little Learners workbook!")
    c.drawCentredString(W / 2, H - 450, ar("لإنهاء كتاب النشاطات بنجاح!"))
    for i in range(5):
        c.setFillColor(ACCENTS[i])
        star(c, W / 2 + (i - 2) * 70, H - 540, 26)
    c.setFillColor(INK)
    c.setFont("Sans", 13)
    c.drawString(110, 130, "Date: ______________")
    c.drawRightString(W - 110, 130, "Signed: ______________")


def star(c, cx, cy, r):
    import math
    p = c.beginPath()
    for k in range(10):
        rad = r if k % 2 == 0 else r * 0.45
        a = math.pi / 2 + k * math.pi / 5
        (p.moveTo if k == 0 else p.lineTo)(cx + rad * math.cos(a), cy + rad * math.sin(a))
    p.close()
    c.drawPath(p, fill=1, stroke=0)


def build(out_dir):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    b = Book(out / "Little-Learners-Arabic-English-Workbook.pdf", "Little Learners – Arabic + English Activity Workbook")
    cover(b)
    how_to(b)
    english_pages(b)
    arabic_pages(b)
    number_pages(b)
    maze_pages(b)
    certificate(b)
    b.save()
    # free sample / lead magnet: cover + 1 page per section
    s = Book(out / "FREE-SAMPLE-Little-Learners.pdf", "Little Learners – Free Sample")
    cover(s)
    EN_WORDS_backup = dict(EN_WORDS)
    EN_WORDS.clear(); EN_WORDS["A"] = "Apple"
    english_pages(s)
    EN_WORDS.update(EN_WORDS_backup)
    AR_backup = list(AR_LETTERS)
    del AR_LETTERS[1:]
    arabic_pages(s)
    AR_LETTERS[:] = AR_backup
    s.save()
    print("pages:", b.page)


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "product")
