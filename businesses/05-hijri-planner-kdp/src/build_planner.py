"""Generate the 2027 Hijri + Gregorian weekly planner: KDP paperback interior, KDP cover, and a printable PDF.

Usage: python3 build_planner.py <output_dir>

KDP spec used: trim 8.5" x 11", no bleed, white paper (0.002252"/page spine), inside margin 0.625", outside 0.5".
Odd pages are right-hand pages, so every 2-page spread starts on an even page.
"""
import datetime as dt
import sys
import warnings
from pathlib import Path

import arabic_reshaper
from bidi.algorithm import get_display
from hijridate import Gregorian
from reportlab.lib.colors import HexColor, white
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

warnings.filterwarnings("ignore")
FD = "/usr/share/fonts/truetype/dejavu/"
pdfmetrics.registerFont(TTFont("Sans", FD + "DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("SansBold", FD + "DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Serif", FD + "DejaVuSerif.ttf"))
pdfmetrics.registerFont(TTFont("SerifBold", FD + "DejaVuSerif-Bold.ttf"))

YEAR = 2027
W, H = 8.5 * inch, 11 * inch
INSIDE, OUTSIDE, TOP, BOTTOM = 0.625 * inch, 0.5 * inch, 0.55 * inch, 0.55 * inch
INK = HexColor("#1F2937")
GREEN = HexColor("#0F5132")
GOLD = HexColor("#B8860B")
LINE = HexColor("#D1D5DB")
SOFT = HexColor("#F3F4F1")
MUTED = HexColor("#6B7280")

H_EN = ["Muharram", "Safar", "Rabi' al-Awwal", "Rabi' al-Thani", "Jumada al-Ula", "Jumada al-Akhirah", "Rajab",
        "Sha'ban", "Ramadan", "Shawwal", "Dhu al-Qa'dah", "Dhu al-Hijjah"]
H_AR = ["محرم", "صفر", "ربيع الأول", "ربيع الآخر", "جمادى الأولى", "جمادى الآخرة", "رجب", "شعبان", "رمضان", "شوال",
        "ذو القعدة", "ذو الحجة"]
G_EN = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
G_AR = ["كانون الثاني / يناير", "شباط / فبراير", "آذار / مارس", "نيسان / أبريل", "أيار / مايو", "حزيران / يونيو",
        "تموز / يوليو", "آب / أغسطس", "أيلول / سبتمبر", "تشرين الأول / أكتوبر", "تشرين الثاني / نوفمبر", "كانون الأول / ديسمبر"]
D_EN = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
D_AR = ["الاثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت", "الأحد"]
PRAYERS = [("F", "الفجر"), ("D", "الظهر"), ("A", "العصر"), ("M", "المغرب"), ("I", "العشاء")]
EVENTS = [  # (hijri month, day, English, Arabic)
    (9, 1, "1st of Ramadan", "أول رمضان"),
    (9, 27, "27th night of Ramadan (Laylat al-Qadr is sought in the odd nights)", "ليلة ٢٧ رمضان"),
    (10, 1, "Eid al-Fitr", "عيد الفطر"),
    (12, 1, "First 10 days of Dhu al-Hijjah begin", "بداية عشر ذي الحجة"),
    (12, 9, "Day of Arafah", "يوم عرفة"),
    (12, 10, "Eid al-Adha", "عيد الأضحى"),
    (1, 1, "Islamic New Year", "رأس السنة الهجرية"),
    (1, 10, "Day of Ashura", "يوم عاشوراء"),
]


def ar(t):
    return get_display(arabic_reshaper.reshape(t))


def hijri(d):
    return Gregorian(d.year, d.month, d.day).to_hijri()


def hstr(d, short=False):
    h = hijri(d)
    return f"{h.day} {H_EN[h.month - 1]}" + ("" if short else f" {h.year}")


def events_for(year):
    out = []
    d = dt.date(year, 1, 1)
    while d.year == year:
        h = hijri(d)
        for m, day, en, a in EVENTS:
            if h.month == m and h.day == day:
                out.append((d, en, a))
        d += dt.timedelta(days=1)
    return out


class Book:
    def __init__(self, path):
        self.c = canvas.Canvas(str(path), pagesize=(W, H))
        self.c.setTitle(f"{YEAR} Hijri & Gregorian Weekly Planner")
        self.c.setAuthor("Noor Planners")
        self.n = 0

    def page(self):
        if self.n:
            self.c.showPage()
        self.n += 1
        right = self.n % 2 == 1
        self.x0 = INSIDE if right else OUTSIDE
        self.x1 = W - (OUTSIDE if right else INSIDE)
        self.y1, self.y0 = H - TOP, BOTTOM
        self.c.setFont("Sans", 7)
        self.c.setFillColor(MUTED)
        (self.c.drawRightString if right else self.c.drawString)(self.x1 if right else self.x0, self.y0 - 14, str(self.n))
        return self

    @property
    def w(self):
        return self.x1 - self.x0

    def save(self):
        self.c.save()


def title_bar(b, en, ar_txt, sub=None, size=20):
    c = b.c
    c.setFillColor(GREEN)
    c.rect(b.x0, b.y1 - 40, b.w, 40, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("SerifBold", size)
    c.drawString(b.x0 + 12, b.y1 - 28, en)
    c.setFont("SansBold", size - 2)
    c.drawRightString(b.x1 - 12, b.y1 - 28, ar(ar_txt))
    if sub:
        c.setFillColor(GOLD)
        c.setFont("Sans", 9.5)
        c.drawString(b.x0 + 2, b.y1 - 54, sub)
    return b.y1 - (62 if sub else 50)


def lines(c, x0, x1, ytop, ybot, gap=18):
    c.setStrokeColor(LINE)
    c.setLineWidth(0.6)
    y = ytop - gap
    while y > ybot + 2:
        c.line(x0, y, x1, y)
        y -= gap


def box(c, x, y, w, h, fill=None):
    c.setStrokeColor(LINE)
    c.setLineWidth(0.8)
    if fill:
        c.setFillColor(fill)
    c.rect(x, y, w, h, fill=1 if fill else 0, stroke=1)


# ---------------- front matter ----------------

def title_page(b):
    c = b.page().c
    c.setFillColor(GREEN)
    c.setFont("SerifBold", 54)
    c.drawCentredString(W / 2, H - 3.2 * inch, str(YEAR))
    c.setFont("SerifBold", 26)
    c.drawCentredString(W / 2, H - 3.8 * inch, "Hijri & Gregorian Weekly Planner")
    h0, h1 = hijri(dt.date(YEAR, 1, 1)), hijri(dt.date(YEAR, 12, 31))
    c.setFillColor(GOLD)
    c.setFont("SansBold", 26)
    c.drawCentredString(W / 2, H - 4.5 * inch, ar(f"مفكرة {YEAR} الأسبوعية · هجري وميلادي"))
    c.setFont("Sans", 13)
    c.setFillColor(INK)
    c.drawCentredString(W / 2, H - 5.0 * inch, f"{h0.year} – {h1.year} AH  ·  Prayer tracker  ·  Ramadan planner  ·  Islamic dates")
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.2)
    c.line(W / 2 - 1.5 * inch, H - 5.3 * inch, W / 2 + 1.5 * inch, H - 5.3 * inch)
    c.setFont("Sans", 12)
    c.drawCentredString(W / 2, 3.2 * inch, "This planner belongs to")
    c.line(W / 2 - 2 * inch, 2.6 * inch, W / 2 + 2 * inch, 2.6 * inch)
    c.drawCentredString(W / 2, 2.0 * inch, ar("هذه المفكرة لـ"))


def info_page(b):
    b.page()
    c = b.c
    y = title_bar(b, "How to use", "طريقة الاستخدام")
    c.setFillColor(INK)
    c.setFont("Sans", 10.5)
    txt = [
        "• Every day shows the Gregorian date and the Hijri date (Umm al-Qura calendar).",
        "• Tick the five prayer circles each day: F Fajr · D Dhuhr · A Asr · M Maghrib · I Isha.",
        "• Each month opens with a calendar, the month's Islamic dates, goals and a habit tracker.",
        "• A 30-day Ramadan planner sits just before February. Ramadan begins around 8 Feb 2027.",
        "• Weeks run Monday to Sunday. Friday (Jumu'ah) is highlighted.",
        "",
        "Note: Hijri dates follow the Umm al-Qura calculation. Local moon sighting can shift",
        "dates by one day. Please confirm Ramadan and Eid with your local mosque.",
    ]
    for t in txt:
        y -= 20
        c.drawString(b.x0 + 6, y, t)
    y -= 40
    c.setFont("SansBold", 13)
    for t in ("كل يوم فيه التاريخ الميلادي والهجري (تقويم أم القرى)",
              "علّم على دوائر الصلوات الخمس كل يوم",
              "كل شهر يبدأ بتقويم ومناسبات وأهداف ومتابعة عادات",
              "مخطط رمضان لثلاثين يوماً قبل شهر شباط",
              "التواريخ الهجرية حسابية وقد تختلف يوماً حسب رؤية الهلال"):
        y -= 26
        c.drawRightString(b.x1 - 6, y, ar(t))
    c.setFont("Sans", 8)
    c.setFillColor(MUTED)
    c.drawCentredString(W / 2, b.y0 + 10, "© Noor Planners. All rights reserved.")


def year_glance(b):
    b.page()
    c = b.c
    y = title_bar(b, f"{YEAR} at a Glance", "السنة في لمحة")
    cols, rows = 3, 4
    cw, ch = b.w / cols, (y - b.y0 - 10) / rows
    for m in range(12):
        x = b.x0 + (m % cols) * cw
        top = y - (m // cols) * ch
        c.setFillColor(GREEN)
        c.setFont("SerifBold", 11)
        c.drawString(x + 8, top - 16, G_EN[m])
        d1 = dt.date(YEAR, m + 1, 1)
        h_a, h_b = hijri(d1), hijri((d1.replace(day=28) + dt.timedelta(days=4)).replace(day=1) - dt.timedelta(days=1))
        c.setFillColor(GOLD)
        c.setFont("Sans", 6.5)
        c.drawString(x + 8, top - 26, f"{H_EN[h_a.month - 1]} – {H_EN[h_b.month - 1]} {h_b.year}")
        cell = (cw - 16) / 7
        c.setFillColor(MUTED)
        c.setFont("SansBold", 6.5)
        for i, dn in enumerate("MTWTFSS"):
            c.drawCentredString(x + 8 + (i + .5) * cell, top - 38, dn)
        c.setFont("Sans", 7.5)
        d = d1
        row = 0
        while d.month == m + 1:
            col = d.weekday()
            ev = any(e[0] == d for e in EVENTS_Y)
            c.setFillColor(GOLD if ev else (GREEN if col == 4 else INK))
            c.drawCentredString(x + 8 + (col + .5) * cell, top - 50 - row * 12, str(d.day))
            if col == 6:
                row += 1
            d += dt.timedelta(days=1)


def islamic_dates(b):
    b.page()
    c = b.c
    y = title_bar(b, f"Islamic Dates {YEAR}", f"المناسبات الإسلامية {YEAR}")
    y -= 10
    for d, en, a in EVENTS_Y:
        y -= 34
        c.setFillColor(SOFT)
        c.rect(b.x0, y - 8, b.w, 28, fill=1, stroke=0)
        c.setFillColor(GREEN)
        c.setFont("SansBold", 11)
        c.drawString(b.x0 + 8, y, d.strftime("%a %d %b %Y"))
        c.setFillColor(INK)
        c.setFont("Sans", 9.5)
        c.drawString(b.x0 + 1.75 * inch, y, en.split(" (")[0])
        c.setFont("SansBold", 11)
        c.drawRightString(b.x1 - 8, y, ar(a))
        c.setFont("Sans", 7)
        c.setFillColor(MUTED)
        c.drawString(b.x0 + 1.75 * inch, y - 10, hstr(d))
    c.setFont("Sans", 8.5)
    c.setFillColor(MUTED)
    c.drawString(b.x0, b.y0 + 10, "Umm al-Qura calculation. Local moon sighting may differ by one day.")


def goals_page(b):
    b.page()
    c = b.c
    y = title_bar(b, f"My {YEAR} Intentions", "نواياي لهذه السنة")
    areas = [("Faith", "ديني"), ("Family", "عائلتي"), ("Health", "صحتي"), ("Work & Study", "عملي ودراستي"),
             ("Money", "مالي"), ("Personal growth", "نفسي")]
    bh = (y - b.y0) / 3 - 8
    bw = b.w / 2 - 6
    for i, (en, a) in enumerate(areas):
        x = b.x0 + (i % 2) * (bw + 12)
        top = y - (i // 2) * (bh + 8)
        box(c, x, top - bh, bw, bh)
        c.setFillColor(GREEN)
        c.setFont("SansBold", 11)
        c.drawString(x + 8, top - 16, en)
        c.drawRightString(x + bw - 8, top - 16, ar(a))
        lines(c, x + 8, x + bw - 8, top - 22, top - bh)


# ---------------- spreads ----------------

def ramadan_spread(b):
    start = next(dt.date(YEAR, 1, 1) + dt.timedelta(days=i) for i in range(366)
                 if hijri(dt.date(YEAR, 1, 1) + dt.timedelta(days=i)).month == 9)
    for half in range(2):
        b.page()
        c = b.c
        y = title_bar(b, f"Ramadan {hijri(start).year} Planner", "مخطط رمضان",
                      f"Expected start: {start.strftime('%A %d %B %Y')} (confirm locally)" if half == 0 else None)
        hdr = ["Day", "Date", "Fast", "5 prayers", "Taraweeh", "Quran", "Good deed / Dua"]
        widths = [0.45, 1.05, 0.45, 1.3, 0.7, 0.75]
        widths.append(b.w / inch - sum(widths))
        x = b.x0
        c.setFont("SansBold", 8.5)
        c.setFillColor(GREEN)
        for h_, wd in zip(hdr, widths):
            c.drawString(x + 4, y - 14, h_)
            x += wd * inch
        rh = (y - 24 - b.y0) / 15
        for r in range(15):
            day = half * 15 + r
            d = start + dt.timedelta(days=day)
            ry = y - 24 - (r + 1) * rh
            if r % 2 == 0:
                c.setFillColor(SOFT)
                c.rect(b.x0, ry, b.w, rh, fill=1, stroke=0)
            c.setFillColor(INK)
            c.setFont("SansBold", 10)
            c.drawString(b.x0 + 6, ry + rh / 2 - 4, str(day + 1))
            c.setFont("Sans", 8)
            c.drawString(b.x0 + 0.45 * inch + 4, ry + rh / 2, d.strftime("%a %d %b"))
            c.setFillColor(MUTED)
            c.setFont("Sans", 6.5)
            # Umm al-Qura may give a 29-day Ramadan; the 30th row is kept for regions that complete 30 days
            c.drawString(b.x0 + 0.45 * inch + 4, ry + rh / 2 - 10,
                         hstr(d, short=True) if hijri(d).month == 9 else "if Ramadan has 30 days")
            c.setStrokeColor(INK)
            c.setLineWidth(0.7)
            cx = b.x0 + 1.5 * inch + 0.22 * inch
            c.circle(cx, ry + rh / 2, 6)
            for k in range(5):
                c.circle(b.x0 + 1.95 * inch + 0.12 * inch + k * 0.24 * inch, ry + rh / 2, 5)
            c.circle(b.x0 + 3.25 * inch + 0.35 * inch, ry + rh / 2, 6)
            c.rect(b.x0 + 3.95 * inch + 0.1 * inch, ry + rh / 2 - 6, 0.55 * inch, 12)


def month_spread(b, m):
    d1 = dt.date(YEAR, m, 1)
    # left: calendar grid
    b.page()
    c = b.c
    hm = sorted({(hijri(d1 + dt.timedelta(days=i)).month) for i in range(31) if (d1 + dt.timedelta(days=i)).month == m},
                key=lambda x: (x - hijri(d1).month) % 12)
    y = title_bar(b, f"{G_EN[m - 1]} {YEAR}", G_AR[m - 1], " · ".join(f"{H_EN[x - 1]} ({ar(H_AR[x - 1])})" for x in hm))
    cw = b.w / 7
    c.setFont("SansBold", 8.5)
    for i in range(7):
        c.setFillColor(GREEN if i == 4 else INK)
        c.drawCentredString(b.x0 + (i + .5) * cw, y - 12, D_EN[i][:3].upper())
        c.drawCentredString(b.x0 + (i + .5) * cw, y - 24, ar(D_AR[i]))
    first_col = d1.weekday()
    ndays = ((d1.replace(day=28) + dt.timedelta(days=4)).replace(day=1) - dt.timedelta(days=1)).day
    nrows = (first_col + ndays + 6) // 7
    ch = (y - 32 - b.y0) / nrows
    for k in range(nrows * 7):
        col, row = k % 7, k // 7
        x, top = b.x0 + col * cw, y - 32 - row * ch
        dn = k - first_col + 1
        box(c, x, top - ch, cw, ch, SOFT if col == 4 else None)
        if 1 <= dn <= ndays:
            d = dt.date(YEAR, m, dn)
            h = hijri(d)
            c.setFillColor(INK)
            c.setFont("SerifBold", 14)
            c.drawString(x + 5, top - 17, str(dn))
            c.setFillColor(GOLD if h.day == 1 else MUTED)
            c.setFont("Sans" if h.day != 1 else "SansBold", 6.5)
            c.drawRightString(x + cw - 4, top - 12, f"{h.day}" + (f" {H_EN[h.month - 1][:9]}" if h.day == 1 else ""))
            ev = [e for e in EVENTS_Y if e[0] == d]
            if ev:
                c.setFillColor(GOLD)
                c.setFont("SansBold", 6)
                words, line, ly = ev[0][1].split(" (")[0].split(), "", top - 30
                for wd in words:
                    if pdfmetrics.stringWidth(line + " " + wd, "SansBold", 6) > cw - 8:
                        c.drawString(x + 4, ly, line.strip()); ly -= 8; line = ""
                    line += " " + wd
                c.drawString(x + 4, ly, line.strip())
    # right: goals, dates, habits
    b.page()
    c = b.c
    y = title_bar(b, "Goals & Habits", "أهداف وعادات", G_EN[m - 1])
    half = b.w / 2 - 6
    gh = 2.5 * inch
    for i, (en, a) in enumerate((("This month's goals", "أهداف الشهر"), ("Islamic dates & reminders", "مناسبات وتذكيرات"))):
        x = b.x0 + i * (half + 12)
        box(c, x, y - gh, half, gh)
        c.setFillColor(GREEN)
        c.setFont("SansBold", 9.5)
        c.drawString(x + 6, y - 14, en)
        c.drawRightString(x + half - 6, y - 14, ar(a))
        if i == 1:
            ev = [e for e in EVENTS_Y if e[0].month == m]
            yy = y - 32
            for d, en_, a_ in ev:
                c.setFillColor(GOLD)
                c.setFont("SansBold", 8)
                c.drawString(x + 6, yy, d.strftime("%d %b"))
                c.setFillColor(INK)
                c.setFont("Sans", 7.5)
                c.drawString(x + 44, yy, en_.split(" (")[0][:34])
                yy -= 14
            lines(c, x + 6, x + half - 6, yy + 4, y - gh, 16)
        else:
            lines(c, x + 6, x + half - 6, y - 18, y - gh, 16)
    y -= gh + 14
    c.setFillColor(GREEN)
    c.setFont("SansBold", 10)
    c.drawString(b.x0, y, "Habit tracker")
    c.drawRightString(b.x1, y, ar("متابعة العادات"))
    y -= 8
    label_w = 1.3 * inch
    cell = (b.w - label_w) / 31
    rows = 8
    rh = 18
    c.setFont("Sans", 6)
    for dn in range(31):
        c.setFillColor(MUTED if dn < ndays else LINE)
        c.drawCentredString(b.x0 + label_w + (dn + .5) * cell, y - 9, str(dn + 1))
    for r in range(rows):
        ty = y - 14 - (r + 1) * rh
        c.setStrokeColor(LINE)
        c.line(b.x0, ty, b.x0 + label_w - 4, ty)
        for dn in range(ndays):
            c.rect(b.x0 + label_w + dn * cell + 1, ty + 2, cell - 2, rh - 4)
    y = y - 14 - rows * rh - 16
    box(c, b.x0, b.y0, b.w, y - b.y0)
    c.setFillColor(GREEN)
    c.setFont("SansBold", 9.5)
    c.drawString(b.x0 + 6, y - 14, "Notes")
    c.drawRightString(b.x1 - 6, y - 14, ar("ملاحظات"))
    lines(c, b.x0 + 6, b.x1 - 6, y - 18, b.y0, 17)


def day_box(b, x, top, w, h, d):
    c = b.c
    fri = d.weekday() == 4
    box(c, x, top - h, w, h)
    c.setFillColor(SOFT if not fri else HexColor("#E7F1EA"))
    c.rect(x, top - 30, w, 30, fill=1, stroke=0)
    c.setFillColor(GREEN)
    c.setFont("SerifBold", 18)
    c.drawString(x + 8, top - 23, str(d.day))
    c.setFont("SansBold", 9)
    c.setFillColor(INK)
    c.drawString(x + 34, top - 13, D_EN[d.weekday()] + (" · Jumu'ah" if fri else ""))
    c.setFont("Sans", 7.5)
    c.setFillColor(GOLD)
    c.drawString(x + 34, top - 24, hstr(d) + ("" if d.year == YEAR else f"  ({d.year})"))
    c.setFont("SansBold", 10)
    c.setFillColor(INK)
    c.drawRightString(x + w - 120, top - 19, ar(D_AR[d.weekday()]))
    # prayer circles
    for k, (p, _) in enumerate(PRAYERS):
        cx = x + w - 104 + k * 21
        c.setStrokeColor(GREEN)
        c.setLineWidth(0.8)
        c.circle(cx, top - 15, 7.5)
        c.setFillColor(GREEN)
        c.setFont("SansBold", 6.5)
        c.drawCentredString(cx, top - 17.5, p)
    ev = [e for e in EVENTS_Y if e[0] == d]
    y = top - 30
    if ev:
        c.setFillColor(GOLD)
        c.setFont("SansBold", 8)
        c.drawString(x + 8, y - 11, "★ " + ev[0][1].split(" (")[0])
        c.drawRightString(x + w - 8, y - 11, ar(ev[0][2]))
        y -= 14
    lines(c, x + 8, x + w - 8, y, top - h, 17)


def week_spread(b, monday, wk):
    days = [monday + dt.timedelta(days=i) for i in range(7)]
    rng = f"Week {wk} · {days[0].strftime('%d %b')} – {days[6].strftime('%d %b %Y')}   ·   {hstr(days[0], True)} – {hstr(days[6])}"
    # left page: Mon-Thu
    b.page()
    c = b.c
    c.setFillColor(GREEN)
    c.setFont("SansBold", 9)
    c.drawString(b.x0, b.y1 - 10, rng)
    top = b.y1 - 18
    h = (top - b.y0) / 4 - 6
    for i in range(4):
        day_box(b, b.x0, top - i * (h + 8), b.w, h, days[i])
    # right page: Fri-Sun + priorities
    b.page()
    c = b.c
    c.setFillColor(GREEN)
    c.setFont("SansBold", 9)
    c.drawRightString(b.x1, b.y1 - 10, ar("أولويات الأسبوع") + "   ·   Weekly priorities & to-do")
    top = b.y1 - 18
    for i in range(3):
        day_box(b, b.x0, top - i * (h + 8), b.w, h, days[4 + i])
    y = top - 3 * (h + 8)
    half = b.w / 2 - 6
    for i, (en, a) in enumerate((("Priorities", "الأولويات"), ("To-do", "المهام"))):
        x = b.x0 + i * (half + 12)
        box(c, x, y - h, half, h)
        c.setFillColor(GREEN)
        c.setFont("SansBold", 9)
        c.drawString(x + 6, y - 13, en)
        c.drawRightString(x + half - 6, y - 13, ar(a))
        yy = y - 30
        c.setStrokeColor(LINE)
        while yy > y - h + 6:
            c.rect(x + 8, yy - 1, 7, 7)
            c.line(x + 20, yy - 2, x + half - 8, yy - 2)
            yy -= 17


def notes_page(b):
    b.page()
    c = b.c
    y = title_bar(b, "Notes", "ملاحظات", size=16)
    lines(c, b.x0, b.x1, y, b.y0, 20)


EVENTS_Y = []


def weeks_by_month():
    monday = dt.date(YEAR, 1, 1) - dt.timedelta(days=dt.date(YEAR, 1, 1).weekday())
    out = {m: [] for m in range(1, 13)}
    wk = 1
    while monday <= dt.date(YEAR, 12, 31):
        thu = monday + dt.timedelta(days=3)
        m = 1 if thu.year < YEAR else (12 if thu.year > YEAR else thu.month)
        out[m].append((monday, wk))
        monday += dt.timedelta(days=7)
        wk += 1
    return out


def build_interior(path):
    EVENTS_Y[:] = events_for(YEAR)
    b = Book(path)
    title_page(b)      # 1 (right)
    info_page(b)       # 2
    year_glance(b)     # 3
    islamic_dates(b)   # 4
    goals_page(b)      # 5
    weeks = weeks_by_month()
    for m in range(1, 13):
        if m == 2:
            ramadan_spread(b)
        month_spread(b, m)
        for monday, wk in weeks[m]:
            week_spread(b, monday, wk)
    while b.n < 150 or b.n % 2:
        notes_page(b)
    b.save()
    return b.n


def build_cover(path, pages):
    spine = pages * 0.002252 * inch
    bleed = 0.125 * inch
    cw, ch = 2 * W + spine + 2 * bleed, H + 2 * bleed
    c = canvas.Canvas(str(path), pagesize=(cw, ch))
    c.setTitle("Cover")
    c.setFillColor(GREEN)
    c.rect(0, 0, cw, ch, fill=1, stroke=0)
    front_x = bleed + W + spine
    # geometric border on front
    c.setStrokeColor(GOLD)
    c.setLineWidth(2)
    c.rect(front_x + 0.45 * inch, bleed + 0.45 * inch, W - 0.9 * inch, H - 0.9 * inch)
    c.setLineWidth(0.8)
    c.rect(front_x + 0.55 * inch, bleed + 0.55 * inch, W - 1.1 * inch, H - 1.1 * inch)
    # 8-point star motif
    cx, cy = front_x + W / 2, bleed + H * 0.62
    for rot in (0, 45):
        c.saveState()
        c.translate(cx, cy)
        c.rotate(rot)
        c.rect(-1.1 * inch, -1.1 * inch, 2.2 * inch, 2.2 * inch)
        c.restoreState()
    c.circle(cx, cy, 0.95 * inch)
    c.setFillColor(GOLD)
    c.setFont("SerifBold", 46)
    c.drawCentredString(cx, cy - 16, str(YEAR))
    c.setFillColor(white)
    c.setFont("SerifBold", 30)
    c.drawCentredString(cx, bleed + H * 0.36, "Hijri & Gregorian")
    c.drawCentredString(cx, bleed + H * 0.36 - 38, "Weekly Planner")
    c.setFillColor(HexColor("#F5DEB3"))
    c.setFont("SansBold", 26)
    c.drawCentredString(cx, bleed + H * 0.36 - 90, ar("مفكرة هجرية وميلادية"))
    c.setFillColor(white)
    c.setFont("Sans", 12.5)
    c.drawCentredString(cx, bleed + 1.15 * inch, "Prayer tracker · Ramadan planner · Islamic dates · Monthly & weekly spreads")
    # spine
    if pages >= 80:
        c.saveState()
        c.translate(bleed + W + spine / 2, bleed + H / 2)
        c.rotate(90)
        c.setFillColor(GOLD)
        c.setFont("SansBold", min(14, spine * 0.55))
        c.drawCentredString(0, -min(14, spine * 0.55) / 3, f"{YEAR} HIJRI & GREGORIAN PLANNER")
        c.restoreState()
    # back
    bx = bleed
    c.setFillColor(white)
    c.setFont("SerifBold", 18)
    c.drawString(bx + 0.8 * inch, bleed + H - 1.6 * inch, "Plan your year around what matters most.")
    c.setFont("Sans", 12)
    y = bleed + H - 2.2 * inch
    for t in ["• Every day shows Gregorian + Hijri dates (Umm al-Qura)",
              "• Five daily prayer check-circles",
              "• 30-day Ramadan planner: fasting, prayers, Taraweeh, Quran",
              "• Monthly calendars with Islamic dates, goals and habit trackers",
              "• 53 weekly spreads, Monday to Sunday, Jumu'ah highlighted",
              f"• {pages} pages · 8.5 x 11 in · bilingual English / العربية"]:
        c.drawString(bx + 0.8 * inch, y, t if "العربية" not in t else t.replace("العربية", ar("العربية")))
        y -= 24
    c.setFillColor(white)  # barcode area must stay clear (KDP places it): 2" x 1.2" bottom-right of back cover
    c.rect(bx + W - 0.25 * inch - 2 * inch, bleed + 0.25 * inch, 2 * inch, 1.2 * inch, fill=1, stroke=0)
    c.save()
    return cw / inch, ch / inch, spine / inch


def build_printable(src, dst):
    """Printable digital version = same interior (sold on Etsy/Gumroad)."""
    import shutil
    shutil.copy(src, dst)


if __name__ == "__main__":
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "product")
    out.mkdir(parents=True, exist_ok=True)
    interior = out / f"KDP-interior-{YEAR}-Hijri-Planner-8.5x11.pdf"
    n = build_interior(interior)
    w, h, s = build_cover(out / f"KDP-cover-{YEAR}-Hijri-Planner.pdf", n)
    build_printable(interior, out / f"Printable-{YEAR}-Hijri-Gregorian-Planner.pdf")
    print(f"pages={n} cover={w:.4f}x{h:.4f}in spine={s:.4f}in")
