#!/usr/bin/env python3
"""Build-time renderer for the news-image-20261119 entry.

Renders a newspaper front page for Thursday 19 November 2026 with PIL
(crisp vector text, no garbled AI text) around the AI-generated hero
illustration in assets/. Run once locally; the committed entry.png is what
the entry program copies to /output/entry.png.

Facts (all reported on 18-19 Nov 2026, checked against live news on 19 Nov
morning Beijing time):
- Anthropic IPO priced Wed evening at $83, above the $70-$78 range:
  980m shares, $81.3bn raise, the largest IPO ever, ~$1.5tn fully diluted;
  first trade Thu 19 Nov as ANT on Nasdaq; $26bn private placement from
  seven partners incl. Nvidia $10bn.
- Nvidia Q3 (Tue evening): revenue $115.8bn +103% YoY, EPS $2.68 vs $2.47
  expected; Q4 guide $130bn vs ~$125.3bn; data-centre $107.6bn; board
  rejected reinstating Jensen Huang. Shares still fell 2.89% Wed to
  $150.96, a fifth straight fall and a 52-week low; AMD +5.3%, Broadcom
  +3.65%.
- Fed Oct minutes (released Wed 2pm ET): 10-2 vote to hold at 3.75-4.00%;
  almost all officials expect further hikes; Gov. Waller called for a
  50bp December hike; markets price ~95%+ for 25bp on Dec 8-9.
- APEC Shenzhen: first-ever Trump-Xi-Putin trilateral Thu 19 Nov; Xi
  pledged lower tariffs and wider market access; Putin sees "big
  potential benefit"; Ukraine, Iran, trade, AI and nuclear on the agenda.
- Gulf: Iran drones hit Kuwait's Ali Al Salem air base and Bahrain early
  Wed; US struck an IRGC missile site on Qeshm Island Tue; a tanker hit
  in Hormuz, 11 crew hurt, 1 missing.
- Ukraine: Kerch bridge hit for a second day, part of the road span fell;
  UK GBP240m missile package.
- Gaza: ceasefire fragile; six killed in Israeli strikes Wed 18 Nov;
  Board of Peace warns the truce may collapse.
- Markets Wed 18 Nov close: S&P 500 7,323.63 -0.23% (5th straight loss),
  Nasdaq 24,429.89 +0.42%, Dow 50,198.17 -1.11%; gold ~$3,729, down
  ~3% (lowest since Sep 2025); 10-yr ~5.07%; dollar index ~103.8, a
  19-month high.
- GTA VI launches Thu 19 Nov on PS5 and Xbox Series X|S (212GB preload).
"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
HERO = os.path.join(
    HERE, "assets",
    "media-generation-hero-chip-globe-20261119-0-6d5682d6-2ff6-4fd2-bc84-f9be2e5fdab4.webp")
OUT = os.path.join(HERE, "entry.png")

W, H = 1024, 1024
M = 30  # margin
PAPER = (246, 241, 231)
INK = (17, 17, 17)
RED = (155, 28, 28)
NAVY = (16, 32, 64)
GREY = (90, 86, 78)

F_SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
F_SERIF_R = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
F_SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
F_SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
F_SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def centered(draw, y, text, fnt, fill=INK):
    draw.text((W // 2, y), text, font=fnt, fill=fill, anchor="ma")
    return y + fnt.size


def rule(draw, y, w=2, x0=M, x1=W - M):
    draw.line([(x0, y), (x1, y)], fill=INK, width=w)


img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)

# ---- masthead ----
y = 16
centered(d, y, "O N E   D A Y  ·  O N E   P A G E", font(F_SANS_B, 15), GREY)
y = 38
centered(d, y, "THE WORLD", font(F_SERIF, 96))
y = 138
rule(d, y, 3)
rule(d, y + 5, 1)
y = 152
centered(d, y, "THURSDAY,  19 NOVEMBER 2026", font(F_SERIF, 31), RED)
y = 190
rule(d, y, 1)

# ---- lead headline + deck ----
y = 202
centered(d, y, "ANTHROPIC DEBUTS AT $83", font(F_SERIF, 56))
y = 262
deck = ("The Claude-maker prices above its range in the largest IPO ever — "
        "and starts trading today as ANT")
for line in wrap(d, deck, font(F_SANS, 20), W - 2 * M - 40):
    centered(d, y, line, font(F_SANS, 20))
    y += 26

# ---- hero image ----
hero = Image.open(HERO).convert("RGB")  # 2736x912
# crop a wide band: chip + horizon + market skyline
cw, ch = hero.size
band_w = W - 2 * M
band_h = 290
crop_h = int(cw * band_h / band_w)
top = int((ch - crop_h) * 0.15)
hero = hero.crop((0, top, cw, top + crop_h))
hero = hero.resize((band_w, band_h), Image.LANCZOS)
img.paste(hero, (M, y + 8))
y = y + 8 + 290 + 8
d.text((M, y), "A golden chip over a world waking to a record listing: AI money "
       "sets the tone for a day of summits, war and rate-watch.  (Illustration)",
       font=font(F_SERIF_I, 15), fill=GREY)
y += 24

# ---- markets ticker ----
d.rectangle([M, y, W - M, y + 34], fill=NAVY)
d.text((W // 2, y + 17),
       "S&P 500  −0.23% Wed  ·  NASDAQ  +0.42%  ·  DOW  −1.11%  ·  "
       "GOLD ~$3,729, −3%  ·  DOLLAR at 19-mo high",
       font=font(F_SANS_B, 16), fill=(255, 255, 255), anchor="mm")
y += 34 + 10

# ---- story grid: 2 cols x 3 rows ----
stories = [
    ("NVIDIA",
     "Beat the Street, still fell 2.89%",
     "Revenue $115.8bn, up 103%; $130bn guide. Shares hit a 52-week low "
     "as the board ruled out Huang's return."),
    ("THE FED",
     "Waller wants a 50bp December hike",
     "October vote was 10-2 to hold at 3.75-4.00%; a December 25bp hike "
     "is ~95% priced for Dec 8-9."),
    ("APEC · SHENZHEN",
     "Trump, Xi and Putin meet today",
     "First-ever trilateral of the three leaders; Xi pledges lower "
     "tariffs, Putin sees \"big potential benefit\"."),
    ("THE GULF",
     "Iran drones hit Kuwait and Bahrain",
     "US struck an IRGC site on Qeshm Island; a tanker is hit in Hormuz, "
     "11 crew hurt and one missing."),
    ("UKRAINE",
     "Kerch bridge hit a second day",
     "Part of the road span fell into the strait; the UK sends £240m of "
     "missiles as allies rush arms."),
    ("GAZA",
     "Fragile ceasefire under strain",
     "Six killed in Israeli strikes on Wednesday; the Board of Peace "
     "warns the truce may collapse."),
]
col_w = (W - 2 * M - 24) // 2
row_h = 84
gx0 = M
for i, (kick, head, body) in enumerate(stories):
    cx = gx0 + (i % 2) * (col_w + 24)
    cy = y + (i // 2) * row_h
    d.text((cx, cy), kick, font=font(F_SANS_B, 14), fill=RED)
    hl = wrap(d, head, font(F_SERIF, 23), col_w)
    hy = cy + 19
    for line in hl[:1]:
        d.text((cx, hy), line, font=font(F_SERIF, 23), fill=INK)
        hy += 27
    by = hy + 1
    for line in wrap(d, body, font(F_SANS, 15), col_w)[:2]:
        d.text((cx, by), line, font=font(F_SANS, 15), fill=(51, 51, 51))
        by += 19
    if i % 2 == 0:
        d.line([(cx + col_w + 12, cy), (cx + col_w + 12, cy + row_h - 12)],
               fill=(200, 192, 175), width=1)

y = y + 3 * row_h + 2
rule(d, y, 1)
y += 8
d.text((M, y), "ALSO:  GTA VI launches today on PS5 and Xbox  ·  AMD +5.3%, "
       "Broadcom +3.7%  ·  10-yr yield ~5.07%",
       font=font(F_SANS_B, 14), fill=INK)
y += 24
d.text((W // 2, y), "Every story above happened or was first reported on "
       "Thursday 19 November 2026.",
       font=font(F_SERIF_I, 14), fill=GREY, anchor="ma")

img.save(OUT, "JPEG", quality=88, optimize=True)
print("saved", OUT, os.path.getsize(OUT), "bytes")
