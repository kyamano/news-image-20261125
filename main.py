#!/usr/bin/env python3
"""news-image-20261125: draw one 1024x1024 PNG summing up the world's
news of Wednesday 25 November 2026.

Pure Python 3 standard library only (zlib, struct, os, math). No network,
no files read, no timestamps, no randomness: two runs write identical bytes.

Layout: a newspaper front page. Masthead, a hero story with a hand-drawn
globe, nine more stories in a 3x3 card grid, and a 20-item "day in brief"
strip, then a sources footer.
"""

import math
import os
import struct
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- font
# 5x7 bitmap font, one glyph = seven rows of five bits ('#' set, '.' clear).
# Written out by hand for this entry only.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "a": ("00000", "00000", "01110", "00001", "01111", "10001", "01111"),
    "b": ("10000", "10000", "11110", "10001", "10001", "10001", "11110"),
    "c": ("00000", "00000", "01110", "10000", "10000", "10001", "01110"),
    "d": ("00001", "00001", "01111", "10001", "10001", "10001", "01111"),
    "e": ("00000", "00000", "01110", "10001", "11111", "10000", "01110"),
    "f": ("00110", "01001", "01000", "11110", "01000", "01000", "01000"),
    "g": ("00000", "01111", "10001", "10001", "01111", "00001", "01110"),
    "h": ("10000", "10000", "11110", "10001", "10001", "10001", "10001"),
    "i": ("00100", "00000", "01100", "00100", "00100", "00100", "01110"),
    "j": ("00010", "00000", "00110", "00010", "00010", "10010", "01100"),
    "k": ("10000", "10000", "10010", "10100", "11000", "10100", "10010"),
    "l": ("01100", "00100", "00100", "00100", "00100", "00100", "01110"),
    "m": ("00000", "00000", "11010", "10101", "10101", "10101", "10101"),
    "n": ("00000", "00000", "11110", "10001", "10001", "10001", "10001"),
    "o": ("00000", "00000", "01110", "10001", "10001", "10001", "01110"),
    "p": ("00000", "00000", "11110", "10001", "10001", "11110", "10000"),
    "q": ("00000", "00000", "01111", "10001", "10001", "01111", "00001"),
    "r": ("00000", "00000", "10110", "11001", "10000", "10000", "10000"),
    "s": ("00000", "00000", "01111", "10000", "01110", "00001", "11110"),
    "t": ("00100", "00100", "01110", "00100", "00100", "00100", "00011"),
    "u": ("00000", "00000", "10001", "10001", "10001", "10011", "01101"),
    "v": ("00000", "00000", "10001", "10001", "10001", "01010", "00100"),
    "w": ("00000", "00000", "10001", "10101", "10101", "10101", "01010"),
    "x": ("00000", "00000", "10001", "01010", "00100", "01010", "10001"),
    "y": ("00000", "10001", "10001", "10001", "01111", "00001", "01110"),
    "z": ("00000", "00000", "11111", "00010", "00100", "01000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '"': ("01010", "01010", "01010", "00000", "00000", "00000", "00000"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "*": ("00000", "00100", "10101", "01110", "10101", "00100", "00000"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    ",": ("00000", "00000", "00000", "00000", "00100", "00100", "01000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "00110", "00110"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    ":": ("00000", "00110", "00110", "00000", "00110", "00110", "00000"),
    ";": ("00000", "00110", "00110", "00000", "00110", "00100", "01000"),
    "<": ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    ">": ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "@": ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    "[": ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    "]": ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    "|": ("00100", "00100", "00100", "00100", "00100", "00100", "00100"),
    "~": ("00000", "00000", "01001", "10110", "00000", "00000", "00000"),
}

# ---------------------------------------------------------------- palette
PAPER = (246, 241, 231)
CARD = (255, 253, 246)
INK = (25, 25, 25)
SOFT = (107, 98, 89)
RED = (168, 35, 26)
NAVY = (29, 78, 137)
GOLD = (176, 124, 22)
RULE = (216, 207, 188)
WHITE = (255, 255, 255)
SKY = (214, 231, 240)
SEA = (163, 196, 216)


class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        for i in range(w * h):
            self.px[i * 3] = bg[0]
            self.px[i * 3 + 1] = bg[1]
            self.px[i * 3 + 2] = bg[2]

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i] = c[0]
            self.px[i + 1] = c[1]
            self.px[i + 2] = c[2]

    def fill(self, x, y, w, h, c):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i] = c[0]
                self.px[i + 1] = c[1]
                self.px[i + 2] = c[2]

    def rect(self, x, y, w, h, c, t=1):
        self.fill(x, y, w, t, c)
        self.fill(x, y + h - t, w, t, c)
        self.fill(x, y, t, h, c)
        self.fill(x + w - t, y, t, h, c)

    def line(self, x0, y0, x1, y1, c):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def thick_line(self, x0, y0, x1, y1, c, t=2):
        for ox in range(t):
            for oy in range(t):
                self.line(x0 + ox, y0 + oy, x1 + ox, y1 + oy, c)

    def circle(self, cx, cy, r, c, t=2):
        steps = max(48, r * 6)
        for k in range(steps):
            a = 2.0 * math.pi * k / steps
            x = int(round(cx + r * math.cos(a)))
            y = int(round(cy + r * math.sin(a)))
            self.fill(x - t // 2, y - t // 2, t, t, c)

    def filled_circle(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            dx = int(round(math.sqrt(max(0, r * r - (yy - cy) ** 2))))
            self.fill(cx - dx, yy, 2 * dx + 1, 1, c)

    def ellipse(self, cx, cy, rx, ry, c, t=2):
        steps = max(48, (rx + ry) * 3)
        for k in range(steps):
            a = 2.0 * math.pi * k / steps
            x = int(round(cx + rx * math.cos(a)))
            y = int(round(cy + ry * math.sin(a)))
            self.fill(x - t // 2, y - t // 2, t, t, c)

    # ---- text ----
    def text_w(self, s, scale):
        return len(s) * 6 * scale - scale

    def draw_text(self, s, x, y, scale, c):
        cx = x
        for ch in s:
            g = FONT.get(ch)
            if g is None:
                g = FONT["?"]
            for row in range(7):
                bits = g[row]
                for col in range(5):
                    if bits[col] == "1":
                        self.fill(cx + col * scale, y + row * scale,
                                  scale, scale, c)
            cx += 6 * scale
        return cx

    def draw_text_centered(self, s, cx, y, scale, c):
        x = cx - self.text_w(s, scale) // 2
        return self.draw_text(s, x, y, scale, c)

    def wrap(self, s, width, scale):
        """Greedy word wrap; returns list of lines fitting pixel width."""
        words = s.split(" ")
        lines = []
        cur = ""
        for wd in words:
            trial = wd if not cur else cur + " " + wd
            if self.text_w(trial, scale) <= width:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
        return lines


def write_png(cv, path):
    raw = bytearray()
    stride = W * 3
    for y in range(H):
        raw.append(0)  # filter: none
        raw += cv.px[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", comp)
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


# ---------------------------------------------------------------- content
HERO_KICKER = "TOP STORY  -  TRADE"
HERO_HEAD = ["TARIFF SHOCK:", "US HITS 14 PARTNERS"]
HERO_DECK = (
    "Trump proposes new duties on 14 trading partners after an 8-month "
    "probe into 'excess capacity'. China faces 20% on top of first-term "
    "tariffs; India up to 25%."
)

# (kicker, headline, deck) for the nine grid cards, stories 2-10.
CARDS = [
    ("HORMUZ", "MINES IN THE STRAIT",
     "Iran says two oil tankers and an LNG carrier struck naval mines in "
     "the Strait of Hormuz and caught fire."),
    ("SPACE", "PAKISTAN REACHES SPACE",
     "China's Shenzhou-24 lifts off with Muhammad Zeeshan Ali, Pakistan's "
     "first astronaut, bound for Tiangong."),
    ("PACIFIC", "A NEW PACIFIC PACT",
     "Australia and Solomon Islands sign a treaty making Canberra the "
     "islands' 'primary security partner'."),
    ("IOWA, USA", "FIVE TONS, ONE BLAST",
     "The US Army detonates nearly five tons of unstable lead azide at its "
     "Iowa ammunition plant."),
    ("CAIRO", "RING ROAD INFERNO",
     "A fuel tanker overturns on Cairo's ring road and bursts into flames, "
     "killing at least 31 people."),
    ("CYBER", "CIA SYSTEMS BREACHED",
     "Unclassified CIA and ODNI systems are breached, the NYT reports - the "
     "latest hit on US intelligence."),
    ("RIYADH", "HOUTHIS CLAIM STRIKES",
     "Yemen's Houthis claim attacks on Riyadh's financial district and the "
     "Ras Tanura refinery."),
    ("DHAKA", "A 36% PAY RISE",
     "Bangladesh raises garment workers' minimum wage 36% to 17,000 taka "
     "after weeks of protests."),
    ("MARKETS", "THE AI RALLY FIZZLES",
     "Asian markets dive as AI doubts return: Seoul -6.2%, Taiwan -4.8%, "
     "Tokyo -2.8%."),
]

BRIEFS = [
    "Mississippi: plane crash kills six",
    "Eisenkot wins first coalition partner",
    "Chess: Gukesh-Sindarov draw, 1-1",
    "Beijing hits back over Huawei verdict",
    "Cartagena: hostages freed, gunman killed",
    "Met Police 'still institutionally racist'",
    "Denmark bans headscarves in court",
    "Australia passes Digital Duty of Care",
    "34 nations to Russia: stop tear gas",
    "Golden Dragon drills open in Cambodia",
    "India condemns Houthi Riyadh attack",
    "Harimau Shakti: India-Malaysia drills",
    "Wang Yi presses Dutch on Nexperia row",
    "Refugee died after UK Eswatini move",
    "Trump: Iran war funded to January",
    "Iran claims two US drones shot down",
    "Silchar airport gets Cabinet approval",
    "No sign Beijing directed Alice Huang",
    "India: Hasina return 'separate' issue",
    "Wang Yi urges UK to back free trade",
]


def draw_globe(cv, cx, cy, r):
    """A simple wireframe globe with a few story dots."""
    cv.filled_circle(cx, cy, r, SKY)
    # land-ish blobs, abstract on purpose
    cv.filled_circle(cx - r // 3, cy - r // 4, r // 3, SEA)
    cv.filled_circle(cx + r // 2, cy + r // 3, r // 4, SEA)
    cv.filled_circle(cx + r // 5, cy - r // 2, r // 5, SEA)
    cv.circle(cx, cy, r, NAVY, 3)
    cv.ellipse(cx, cy, r // 2, r, NAVY, 2)
    cv.ellipse(cx, cy, r, r // 3, NAVY, 2)
    cv.line(cx - r, cy, cx + r, cy, NAVY)
    # story dots
    for dx, dy in [(-30, -18), (24, -30), (38, 14), (-8, 30), (52, -6)]:
        cv.filled_circle(cx + dx, cy + dy, 4, RED)


def build():
    cv = Canvas(W, H, PAPER)

    # ---- masthead ----
    cv.draw_text_centered("MAKE.FUN  -  NEWS-IMAGE-20261125", W // 2, 20, 1, SOFT)
    cv.draw_text_centered("THE WORLD IN ONE DAY", W // 2, 40, 6, INK)
    cv.draw_text_centered("WEDNESDAY 25 NOVEMBER 2026", W // 2, 92, 2, RED)
    cv.fill(24, 118, W - 48, 3, INK)
    cv.fill(24, 124, W - 48, 1, INK)

    # ---- hero ----
    hy, hh = 136, 158
    cv.fill(24, hy, W - 48, hh, CARD)
    cv.rect(24, hy, W - 48, hh, RULE, 1)
    draw_globe(cv, 118, hy + hh // 2, 66)
    tx = 214
    cv.draw_text(HERO_KICKER, tx, hy + 12, 2, RED)
    y = hy + 36
    for line in HERO_HEAD:
        cv.draw_text(line, tx, y, 3, INK)
        y += 26
    deck_lines = cv.wrap(HERO_DECK, W - 48 - tx - 16, 2)
    y = hy + 92
    for line in deck_lines[:3]:
        cv.draw_text(line, tx, y, 2, SOFT)
        y += 19

    # ---- grid of nine stories ----
    gx, gy = 22, 308
    cw, ch, gap = 318, 116, 13
    for idx, (kick, head, deck) in enumerate(CARDS):
        col = idx % 3
        row = idx // 3
        x = gx + col * (cw + gap)
        yy = gy + row * (ch + 10)
        cv.fill(x, yy, cw, ch, CARD)
        cv.rect(x, yy, cw, ch, RULE, 1)
        # number badge
        cv.fill(x, yy, 30, 30, RED)
        num = str(idx + 2)
        nx = x + 15 - cv.text_w(num, 2) // 2
        cv.draw_text(num, nx, yy + 8, 2, WHITE)
        cv.draw_text(kick, x + 40, yy + 8, 2, NAVY)
        head_lines = cv.wrap(head, cw - 20, 2)
        hyy = yy + 32
        for line in head_lines[:2]:
            cv.draw_text(line, x + 10, hyy, 2, INK)
            hyy += 18
        cv.fill(x + 10, yy + 68, cw - 20, 1, RULE)
        deck_lines = cv.wrap(deck, cw - 20, 1)
        dyy = yy + 76
        for line in deck_lines[:3]:
            cv.draw_text(line, x + 10, dyy, 1, SOFT)
            dyy += 10

    # ---- briefs strip ----
    by = 700
    cv.draw_text("THE DAY IN BRIEF", 24, by, 2, INK)
    cv.draw_text("20 MORE STORIES", W - 24 - cv.text_w("20 MORE STORIES", 2),
                 by, 2, RED)
    cv.fill(24, by + 20, W - 48, 2, INK)
    col_w = (W - 48 - 24) // 2
    for i, item in enumerate(BRIEFS):
        col = i % 2
        row = i // 2
        x = 24 + col * (col_w + 24)
        y = by + 34 + row * 22
        cv.filled_circle(x + 3, y + 5, 3, GOLD)
        cv.draw_text(item, x + 14, y, 2, INK)

    # ---- footer ----
    fy = 700 + 34 + 10 * 22 + 14
    cv.fill(24, fy, W - 48, 1, RULE)
    cv.draw_text_centered(
        "Sources: Reuters, AP, AFP, Al Jazeera, CNN, BBC, The Hindu, Nikkei, "
        "SCMP, NYT, WSJ - 25 Nov 2026", W // 2, fy + 10, 1, SOFT)
    cv.draw_text_centered(
        "30 stories: 10 in depth, 20 in brief. Drawn by code, no photos.",
        W // 2, fy + 24, 1, SOFT)
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(out_dir, exist_ok=True)
    cv = build()
    write_png(cv, os.path.join(out_dir, "entry.png"))


if __name__ == "__main__":
    main()
