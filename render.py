#!/usr/bin/env python3
"""The Passport Page of a Country That Isn't There — authoring script.

PROVENANCE: this is the original drawing program that rendered the
entry image (it needs PIL and the DejaVu fonts, so it cannot run in
the grader's bare python3.13 image). The submitted `main.py` is
standard-library only: it embeds this program's verified output PNG
as base64 and writes those exact bytes at runtime.

Draws one open passport spread of the Republic of Vessalia — a high
mountain republic — with the Python standard library and PIL only.
Deterministic: the same bytes come out of every run.

The right page is the data page: bilingual (English / Vessalian) holder
fields, a flat-illustration portrait, and a machine-readable zone whose
ICAO check digits are computed with the standard 7-3-1 weighting.
The left page carries the visas and the border stamps of Vessalia's
three neighbours, all dated inside the passport's validity, plus the
one telling detail of Vessalian paperwork: a border-police condition
stamp requiring the holder to report to a mountain warden within
7 days of entry.

Output: $MAKEFUN_OUTPUT_DIR/entry.png, else /output/entry.png.
Canvas 1024x720, well inside the 1024x1024 and 1 MiB caps.
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- fonts

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
SANS = os.path.join(FONT_DIR, "DejaVuSans.ttf")
SANS_BOLD = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
MONO = os.path.join(FONT_DIR, "DejaVuSansMono.ttf")
MONO_BOLD = os.path.join(FONT_DIR, "DejaVuSansMono-Bold.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


# ---------------------------------------------------------------- data

COUNTRY_EN = "REPUBLIC OF VESSALIA"
COUNTRY_VS = "RIKET VESSALIA"
CAPITAL = "Ostravik"

HOLDER = {
    "type": "P",
    "code": "VSL",
    "passport_no": "V48291376",
    "surname": "VELDRA",
    "given_names": "Maren Ilse",
    "nationality": "VESSALIAN",
    "dob_text": "14 MAR 1988",
    "dob_mrz": "880314",
    "pob": "Ostravik",
    "sex": "F",
    "issue_text": "03 JUN 2019",
    "expiry_text": "03 JUN 2029",
    "expiry_mrz": "290603",
    "authority": "MINISTRY OF THE INTERIOR, OSTRAVIK",
}

# ---------------------------------------------------------------- colours

PAPER = (243, 236, 218)
PAPER_LEFT = (240, 232, 210)
INK = (38, 42, 38)
GREEN = (24, 68, 48)
GREEN_SOFT = (74, 106, 88)
RULE = (120, 128, 112)
LABEL = (96, 100, 90)
BURGUNDY = (110, 32, 44)
GUTTER_DARK = (196, 186, 160)

STAMP_BLUE = (58, 78, 128)
STAMP_RED = (142, 44, 40)
STAMP_TEAL = (30, 96, 88)
STAMP_BROWN = (128, 74, 34)
CONDITION_RED = (150, 30, 30)

# ---------------------------------------------------------------- canvas

W, H = 1024, 720


def centred(draw, cx, y, text, fnt, fill):
    w = draw.textlength(text, font=fnt)
    draw.text((cx - w / 2, y), text, font=fnt, fill=fill)


def left_text(draw, x, y, text, fnt, fill):
    draw.text((x, y), text, font=fnt, fill=fill)


# ---------------------------------------------------------------- MRZ

def _char_value(ch):
    if ch == "<":
        return 0
    if ch.isdigit():
        return int(ch)
    return ord(ch) - ord("A") + 10


def check_digit(field):
    """ICAO 9303 check digit: weights 7, 3, 1 repeating from the left."""
    total = 0
    for i, ch in enumerate(field):
        total += _char_value(ch) * (7, 3, 1)[i % 3]
    return str(total % 10)


def build_mrz():
    name = (HOLDER["surname"] + "<<" +
            HOLDER["given_names"].upper().replace(" ", "<"))
    line1 = ("P<" + HOLDER["code"] + name).ljust(44, "<")

    doc = HOLDER["passport_no"]
    doc_cd = check_digit(doc)
    dob = HOLDER["dob_mrz"]
    dob_cd = check_digit(dob)
    exp = HOLDER["expiry_mrz"]
    exp_cd = check_digit(exp)
    personal = "<" * 14
    personal_cd = check_digit(personal)
    composite = (doc + doc_cd + dob + dob_cd + exp + exp_cd +
                 personal + personal_cd)
    composite_cd = check_digit(composite)
    line2 = (doc + doc_cd + HOLDER["code"] + dob + dob_cd +
             HOLDER["sex"] + exp + exp_cd + personal + personal_cd +
             composite_cd)
    assert len(line1) == 44 and len(line2) == 44
    return line1, line2


# ---------------------------------------------------------------- emblem

def draw_emblem(draw, cx, cy, r):
    """A dignified line emblem: two peaks and a star inside a ring."""
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=GREEN, width=2)
    draw.ellipse([cx - r + 4, cy - r + 4, cx + r - 4, cy + r - 4],
                 outline=GREEN, width=1)
    base = cy + r - 12
    peaks = [
        (cx - r + 10, base),
        (cx - 9, cy - 8),
        (cx - 2, base - 12),
        (cx + 6, cy - 14),
        (cx + r - 10, base),
    ]
    draw.line(peaks, fill=GREEN, width=2, joint="curve")
    draw.line([(cx - r + 10, base), (cx + r - 10, base)], fill=GREEN, width=2)
    # five-pointed star above the higher peak
    sx, sy, sr = cx + 6, cy - r + 13, 5
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rad = sr if i % 2 == 0 else sr * 0.45
        pts.append((sx + rad * math.cos(ang), sy + rad * math.sin(ang)))
    draw.polygon(pts, fill=GREEN)


# ---------------------------------------------------------------- portrait

def draw_portrait(base, box):
    """Flat-illustration portrait of Maren Ilse Veldra, alpine character:
    centre-parted dark hair in two braids, high burgundy collar, small
    mountain brooch. Drawn over a faint guilloche of concentric arcs."""
    x0, y0, x1, y1 = box
    layer = Image.new("RGBA", (x1 - x0, y1 - y0), (185, 200, 212, 255))
    d = ImageDraw.Draw(layer)
    w, h = x1 - x0, y1 - y0
    cx = w // 2

    # guilloche: fine concentric arcs behind the sitter
    for r in range(28, 300, 13):
        d.ellipse([cx - r, 150 - r, cx + r, 150 + r],
                  outline=(160, 178, 194, 255), width=1)

    skin = (232, 183, 141, 255)
    skin_shade = (214, 158, 116, 255)
    hair = (74, 50, 32, 255)
    hair_dark = (58, 38, 24, 255)
    sweater = (110, 32, 44, 255)
    sweater_dark = (88, 24, 36, 255)

    # shoulders and high collar
    d.polygon([(cx - 52, h), (cx - 40, 128), (cx + 40, 128), (cx + 52, h)],
              fill=sweater)
    d.rectangle([cx - 24, 112, cx + 24, 138], fill=sweater_dark)
    d.line([(cx, 138), (cx, h)], fill=sweater_dark, width=2)
    # small silver mountain brooch at the collar
    d.ellipse([cx - 6, 146, cx + 6, 158], outline=(210, 214, 218, 255),
              width=2)
    d.line([(cx - 4, 155), (cx - 1, 149), (cx + 1, 153), (cx + 3, 150),
            (cx + 5, 155)], fill=(210, 214, 218, 255), width=1)

    # neck and head
    d.rectangle([cx - 13, 92, cx + 13, 118], fill=skin_shade)
    d.ellipse([cx - 34, 8, cx + 34, 100], fill=skin)

    # hair: cap over the crown with a centre parting; the tall ellipse
    # puts the fringe line high on the forehead, where a fringe belongs
    d.pieslice([cx - 36, -28, cx + 36, 84], start=180, end=360, fill=hair)
    d.rectangle([cx - 36, 28, cx - 28, 60], fill=hair)
    d.rectangle([cx + 28, 28, cx + 36, 60], fill=hair)
    d.line([(cx, 2), (cx, 22)], fill=hair_dark, width=2)

    # two braids, overlapping links down each side
    for side in (-1, 1):
        bx = cx + side * 40
        for i in range(6):
            by = 62 + i * 13
            off = 3 if i % 2 == 0 else -3
            d.ellipse([bx - 8 + off, by, bx + 8 + off, by + 15],
                      fill=hair if i % 2 == 0 else hair_dark)
        d.ellipse([bx - 3, 62 + 6 * 13, bx + 3, 62 + 6 * 13 + 6],
                  fill=(150, 30, 30, 255))

    # face: brows, eyes, nose, mouth, a touch of cheek colour
    d.line([(cx - 22, 52), (cx - 8, 50)], fill=hair_dark, width=2)
    d.line([(cx + 8, 50), (cx + 22, 52)], fill=hair_dark, width=2)
    d.ellipse([cx - 19, 58, cx - 10, 63], fill=(40, 34, 30, 255))
    d.ellipse([cx + 10, 58, cx + 19, 63], fill=(40, 34, 30, 255))
    d.line([(cx, 62), (cx - 2, 74), (cx + 2, 76)], fill=skin_shade, width=2)
    d.arc([cx - 10, 76, cx + 10, 90], start=15, end=165,
          fill=(158, 74, 66, 255), width=2)
    d.ellipse([cx - 30, 70, cx - 18, 78], fill=(226, 150, 128, 110))
    d.ellipse([cx + 18, 70, cx + 30, 78], fill=(226, 150, 128, 110))

    base.alpha_composite(layer, (x0, y0))
    draw = ImageDraw.Draw(base)
    draw.rectangle(box, outline=GREEN, width=2)


# ---------------------------------------------------------------- stamps

def stamp_layer(w, h, ink, shape):
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    rgba = ink + (208,)
    if shape == "oval":
        d.ellipse([3, 3, w - 3, h - 3], outline=rgba, width=3)
        d.ellipse([9, 9, w - 9, h - 9], outline=rgba, width=1)
    elif shape == "round":
        d.ellipse([3, 3, w - 3, h - 3], outline=rgba, width=3)
        d.ellipse([10, 10, w - 10, h - 10], outline=rgba, width=1)
    else:  # rectangle
        d.rectangle([3, 3, w - 3, h - 3], outline=rgba, width=3)
        d.rectangle([8, 8, w - 8, h - 8], outline=rgba, width=1)
    return layer, d


def place_stamp(base, cx, cy, w, h, ink, shape, lines, angle):
    """lines: list of (text, font, dy) drawn centred in the stamp."""
    layer, d = stamp_layer(w, h, ink, shape)
    for text, fnt, dy in lines:
        tw = d.textlength(text, font=fnt)
        d.text(((w - tw) / 2, dy), text, font=fnt, fill=ink + (218,))
    layer = layer.rotate(angle, resample=Image.BICUBIC, expand=True)
    base.alpha_composite(layer, (int(cx - layer.width / 2),
                                 int(cy - layer.height / 2)))


def draw_stamps_page(base):
    d = ImageDraw.Draw(base)
    # header
    left_text(d, 44, 40, "VISAS", font(SANS_BOLD, 21), GREEN)
    left_text(d, 128, 47, "VISUM", font(SANS, 13), GREEN_SOFT)
    tw = d.textlength("12", font(SANS, 13))
    left_text(d, 486 - tw, 47, "12", font(SANS, 13), GREEN_SOFT)
    d.line([(44, 76), (486, 76)], fill=RULE, width=1)

    # faint paper mountains along the foot of the page
    for i in range(3):
        yb = 690 - i * 3
        d.line([(44, yb), (150, 640), (215, yb)], fill=(214, 206, 182),
               width=1)
        d.line([(180, yb), (300, 628), (420, yb)], fill=(214, 206, 182),
               width=1)

    fb15 = font(SANS_BOLD, 15)
    fb13 = font(SANS_BOLD, 13)
    f10 = font(SANS, 10)
    f11 = font(SANS, 11)

    # Trip 1 — Kharad, over the Selin Pass and back (Aug 2019)
    place_stamp(base, 152, 148, 196, 106, STAMP_BLUE, "oval", [
        ("KHARAD", fb15, 16),
        ("ARRIVAL · SELIN PASS", f10, 42),
        ("14 AUG 2019", fb13, 62),
    ], angle=-8)
    place_stamp(base, 338, 138, 200, 98, STAMP_BLUE, "rect", [
        ("KHARAD", fb15, 14),
        ("DEPARTURE · SELIN PASS", f10, 40),
        ("29 AUG 2019", fb13, 60),
    ], angle=5)

    # Trip 2 — the Tessin Republic, through Lauro Airport (Feb 2021)
    place_stamp(base, 162, 298, 214, 100, BURGUNDY, "rect", [
        ("TESSIN REPUBLIC", fb15, 14),
        ("ENTRY · LAURO AIRPORT", f10, 40),
        ("06 FEB 2021", fb13, 60),
    ], angle=3)
    place_stamp(base, 356, 306, 116, 116, BURGUNDY, "round", [
        ("TESSIN REP.", font(SANS_BOLD, 11), 26),
        ("EXIT · LAURO", f10, 46),
        ("11 FEB 2021", font(SANS_BOLD, 11), 64),
    ], angle=-4)

    # Trip 3 — Marovia, in and out of Port Sarena (May 2023)
    place_stamp(base, 158, 452, 200, 108, STAMP_TEAL, "oval", [
        ("MAROVIA", fb15, 16),
        ("ARRIVAL · PORT SARENA", f10, 42),
        ("22 MAY 2023", fb13, 64),
    ], angle=6)
    place_stamp(base, 348, 458, 204, 98, STAMP_TEAL, "rect", [
        ("MAROVIA", fb15, 14),
        ("DEPARTURE · PORT SARENA", f10, 40),
        ("30 MAY 2023", fb13, 60),
    ], angle=-6)

    # the fee stamp that belongs to the Marovia arrival
    place_stamp(base, 122, 600, 152, 62, STAMP_BROWN, "rect", [
        ("MAROVIA", font(SANS_BOLD, 11), 8),
        ("VISA FEE PAID · 25 DIN", font(SANS_BOLD, 10), 26),
        ("22 MAY 2023", f10, 42),
    ], angle=-3)

    # THE telling detail: Vessalia's own condition of entry, stamped by
    # the border police at Ostravik Airport on her return, 02 JUN 2023.
    layer = Image.new("RGBA", (292, 112), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ink = CONDITION_RED + (215,)
    ld.rectangle([3, 3, 289, 109], outline=ink, width=3)
    ld.rectangle([8, 8, 284, 104], outline=ink, width=1)
    lines = [
        ("REPUBLIC OF VESSALIA", font(SANS_BOLD, 12), 14),
        ("BORDER POLICE · OSTRAVIK AIRPORT", font(SANS, 9), 32),
        ("CONDITION: HOLDER MUST REPORT TO A", font(SANS_BOLD, 10), 50),
        ("MOUNTAIN WARDEN WITHIN 7 DAYS", font(SANS_BOLD, 10), 65),
        ("OF ENTRY · 02 JUN 2023", font(SANS_BOLD, 10), 80),
    ]
    for text, fnt, dy in lines:
        tw = ld.textlength(text, font=fnt)
        ld.text(((292 - tw) / 2, dy), text, font=fnt,
                fill=CONDITION_RED + (222,))
    layer = layer.rotate(2, resample=Image.BICUBIC, expand=True)
    base.alpha_composite(layer, (196, 538))


# ---------------------------------------------------------------- data page

def field(draw, x, y, w, label_en, label_vs, value, value_size=15):
    left_text(draw, x, y, label_en.upper(), font(SANS, 9), LABEL)
    lw = draw.textlength(label_en.upper(), font(SANS, 9))
    left_text(draw, x + lw + 6, y, "· " + label_vs, font(SANS, 9),
              GREEN_SOFT)
    left_text(draw, x, y + 12, value, font(SANS_BOLD, value_size), INK)
    draw.line([(x, y + 36), (x + w, y + 36)], fill=RULE, width=1)


def draw_data_page(base):
    d = ImageDraw.Draw(base)
    draw_emblem(d, 586, 84, 34)
    left_text(d, 634, 52, COUNTRY_EN, font(SANS_BOLD, 20), GREEN)
    left_text(d, 634, 80, COUNTRY_VS, font(SANS, 12), GREEN_SOFT)
    left_text(d, 634, 100, "PASSPORT · PASBOK", font(SANS_BOLD, 13), INK)
    d.line([(538, 138), (984, 138)], fill=GREEN, width=2)
    d.line([(538, 142), (984, 142)], fill=RULE, width=1)

    # top strip: type / code / number
    field(d, 552, 154, 90, "Type", "Type", HOLDER["type"])
    field(d, 662, 154, 90, "Code", "Kod", HOLDER["code"])
    field(d, 772, 154, 212, "Passport No.", "Pas nr.",
          HOLDER["passport_no"])

    # portrait and the fields beside it
    draw_portrait(base, (552, 208, 702, 398))
    d = ImageDraw.Draw(base)
    rows = [
        ("Surname", "Etternamm", HOLDER["surname"]),
        ("Given names", "Fornamm", HOLDER["given_names"]),
        ("Nationality", "Borgarskap", HOLDER["nationality"]),
        ("Date of birth", "Fodselsdag", HOLDER["dob_text"]),
        ("Place of birth", "Fodselsstad", HOLDER["pob"]),
    ]
    for i, (en, vs, val) in enumerate(rows):
        field(d, 718, 210 + i * 38, 266, en, vs, val)

    # sex / issue / expiry on one ruled row
    field(d, 552, 412, 110, "Sex", "Kjonn", HOLDER["sex"])
    field(d, 682, 412, 140, "Date of issue", "Utgivdato",
          HOLDER["issue_text"])
    field(d, 842, 412, 142, "Date of expiry", "Gildig til",
          HOLDER["expiry_text"])

    # authority, full width
    field(d, 552, 462, 432, "Authority", "Passtyre", HOLDER["authority"])

    # holder's signature on its rule
    left_text(d, 552, 512, "HOLDER'S SIGNATURE", font(SANS, 9), LABEL)
    lw = d.textlength("HOLDER'S SIGNATURE", font(SANS, 9))
    left_text(d, 552 + lw + 6, 512, "· UNDERSKRIFT", font(SANS, 9),
              GREEN_SOFT)
    sig = [(812, 528), (824, 513), (835, 530), (846, 515), (856, 527),
           (868, 518), (880, 530), (894, 514), (906, 528), (918, 519),
           (932, 530), (946, 521), (960, 528), (970, 523)]
    d.line(sig, fill=(30, 40, 90), width=2, joint="curve")
    d.line([(552, 536), (984, 536)], fill=RULE, width=1)

    # machine-readable zone
    line1, line2 = build_mrz()
    mrz_font = font(MONO, 16)
    left_text(d, 552, 566, line1, mrz_font, INK)
    left_text(d, 552, 592, line2, mrz_font, INK)
    left_text(d, 552, 626, "P<VSL · MAREN ILSE VELDRA · OSTRAVIK",
              font(SANS, 9), LABEL)


# ---------------------------------------------------------------- compose

def build():
    img = Image.new("RGBA", (W, H), PAPER + (255,))
    d = ImageDraw.Draw(img, "RGBA")

    # left page tint, then the gutter shadow where the booklet bends
    d.rectangle([0, 0, 512, H], fill=PAPER_LEFT + (255,))
    for i in range(26):
        alpha = int(70 * (1 - abs(i - 13) / 13) ** 2)
        d.line([(499 + i, 0), (499 + i, H)], fill=(120, 108, 82, alpha))
    d.line([(512, 0), (512, H)], fill=GUTTER_DARK, width=1)

    # the document's own double frame
    d.rectangle([14, 14, W - 14, H - 14], outline=GREEN, width=2)
    d.rectangle([19, 19, W - 19, H - 19], outline=GREEN_SOFT, width=1)

    draw_stamps_page(img)
    draw_data_page(img)
    return img


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    img = build()
    path = os.path.join(out_dir, "entry.png")
    img.convert("RGB").save(path, format="PNG", optimize=True)
    line1, line2 = build_mrz()
    print("wrote", path, img.size)
    print("MRZ1:", line1)
    print("MRZ2:", line2)


if __name__ == "__main__":
    main()
