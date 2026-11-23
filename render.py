"""Render the news-image-20261123 front page: 1024x1024, drawn from
scratch with PIL. No external images, no photographs, no copied
artwork: every pixel is produced by the shapes and text below.

Layout follows the Q1 guide quadrant (user-supplied newspaper
wireframe): a masthead with a double rule, a large lead zone with a
red headline band and a drawn scene panel on the right, then a
three-by-two grid of story cards below, and a footer strip. The
page is a Monday paper: its masthead date is 23 November 2026.

Deterministic: no clock, no randomness, no network. Running this
twice writes byte-identical PNGs.
"""

import hashlib
import os

from PIL import Image, ImageDraw, ImageFont

W = 1024
H = 1024
MARGIN = 28

INK = (17, 17, 17)
PAPER = (255, 255, 255)
GREY = (102, 102, 102)
LIGHT = (237, 238, 240)
PANEL_LINE = (120, 120, 120)
RED = (176, 0, 32)
RED_DARK = (140, 0, 25)
OCEAN = (168, 198, 223)
LAND = (122, 154, 91)
SEA_LINE = (90, 120, 150)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    """Load a DejaVu font; fail loudly if the file is missing."""
    path = os.path.join(FONT_DIR, name)
    if not os.path.isfile(path):
        raise FileNotFoundError("missing font file: %s" % path)
    return ImageFont.truetype(path, size)


def serif_bold(size):
    return font("DejaVuSerif-Bold.ttf", size)


def serif(size):
    return font("DejaVuSerif.ttf", size)


def sans(size):
    return font("DejaVuSans.ttf", size)


def sans_bold(size):
    return font("DejaVuSans-Bold.ttf", size)


SERIF_BOLD = serif_bold
SERIF = serif
SANS = sans
SANS_BOLD = sans_bold


def wrap(draw, text, fnt, max_width):
    """Greedy word wrap; returns a list of lines that fit max_width.

    A single word wider than max_width raises instead of overflowing.
    """
    lines = []
    for para in text.split("\n"):
        words = para.split()
        if not words:
            lines.append("")
            continue
        for word in words:
            if draw.textlength(word, font=fnt) > max_width:
                raise ValueError(
                    "single word too wide (%r, %d px > %d px)"
                    % (word, draw.textlength(word, font=fnt), max_width))
        cur = words[0]
        for word in words[1:]:
            trial = cur + " " + word
            if draw.textlength(trial, font=fnt) <= max_width:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        lines.append(cur)
    return lines


def check_width(draw, text, fnt, max_width, where):
    """Assert a single-line draw fits; fail loudly instead of clipping."""
    width = draw.textlength(text, font=fnt)
    if width > max_width:
        raise ValueError(
            "%s: %d px wide, max %d: %r" % (where, width, max_width, text))


def draw_lines(draw, lines, x, y, fnt, fill, leading):
    """Draw lines top-down; return the y just below the last line."""
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def fit_text(draw, text, fnt, max_width, max_lines, where):
    """Wrap text and assert it fits; fail loudly instead of clipping."""
    lines = wrap(draw, text, fnt, max_width)
    if len(lines) > max_lines:
        raise ValueError(
            "%s: %d lines, max %d: %r" % (where, len(lines), max_lines, text)
        )
    return lines


LEAD_HEADLINE = "COP31 COLLAPSES — NO CLIMATE DEAL"
LEAD_KICKER = "ANTALYA  ·  SUNDAY"
LEAD_BODY = (
    "Two weeks of talks and two days of overtime ended on Sunday with "
    "no deal. The European Union and others rejected a final draft "
    "that never mentioned fossil fuels. The draft also dropped a "
    "$120bn adaptation target for poorer countries. UN chief "
    "António Guterres said he was \u201cdeeply disappointed\u201d. It "
    "is the first climate summit to end with no agreement since 2009."
)

CARDS = [
    {
        "kicker": "WASHINGTON  ·  SUNDAY",
        "headline": "Democrats take 258+ — biggest since 1992",
        "body": (
            "Democrat Chuck Hubbard beat 11-term Rep. Virginia Foxx by "
            "about 330 votes in North Carolina on Sunday, clinching "
            "seat 258. Democrats are up 44; four races uncalled."
        ),
        "fact": "44 gained  ·  173+ Rep.  ·  4 uncalled",
    },
    {
        "kicker": "WELLINGTON  ·  MONDAY",
        "headline": "India six wickets from a famous win",
        "body": (
            "At lunch on the final day in Wellington, New Zealand were "
            "157 for 4, still 195 behind India\u2019s 720 for 9 "
            "declared. India need six wickets in two sessions."
        ),
        "fact": "Rahul 136  ·  Pant 128  ·  1st Test Day 5",
    },
    {
        "kicker": "NEW DELHI  ·  MONDAY",
        "headline": "Modi meets Nepal's Shah in Delhi",
        "body": (
            "The two prime ministers meet in person in Delhi today, "
            "with a $2bn aid package, three new air routes and "
            "the L626 corridor on the agenda. No outcome yet."
        ),
        "fact": "$500m flood  ·  $1bn loan  ·  $500m highway",
    },
    {
        "kicker": "BANTEN  ·  MONDAY",
        "headline": "Search resumes — 29 still missing",
        "body": (
            "The search resumes on Monday at the burnt candy factory "
            "in Banten. Police removed 24 body bags on Sunday; 29 "
            "workers are still missing and eight are unconfirmed."
        ),
        "fact": "24 returned  ·  4 treated  ·  8 unconfirmed",
    },
    {
        "kicker": "GULF OF FINLAND  ·  SUNDAY",
        "headline": "Sparta II towed out of Finnish waters",
        "body": (
            "The drone-hit Russian cargo ship was towed out of Finnish "
            "waters on Sunday. All 16 crew were evacuated; one was "
            "slightly hurt. Finland says Ukraine likely struck it."
        ),
        "fact": "121 m  ·  Oboronlogistika  ·  to Kaliningrad",
    },
]

SOURCES_TEXT = (
    "Reuters · AP · AFP · Al Jazeera · UN News · "
    "The Hindu · Deccan Herald · Straits Times · CNA. All six "
    "stories verified against two or more wire sources. Outcomes "
    "still pending at press time are stated as such."
)


def draw_globe(draw, cx, cy, r):
    """A symbolic globe with a crack: ocean, land blobs, red fault.

    All internal geometry is defined for r=95 and scaled by r/95,
    so the blobs and the crack stay inside the rim at any radius.
    """
    s = r / 95.0

    def pt(dx, dy):
        return (cx + dx * s, cy + dy * s)

    def box(x0, y0, x1, y1):
        return [cx + x0 * s, cy + y0 * s, cx + x1 * s, cy + y1 * s]

    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=OCEAN,
                 outline=SEA_LINE, width=3)
    # Land masses: overlapping ellipses so no blob reads as a plain
    # circle; all centred inside the rim so none spills past it.
    blobs = [
        (box(-52, -48, 6, 2), box(-34, -30, 22, 12)),
        (box(8, -62, 58, -8), box(22, -44, 66, -2)),
        (box(-58, 12, -6, 62), box(-44, 30, 8, 70)),
        (box(12, 18, 60, 58), box(26, 34, 68, 66)),
    ]
    for box_a, box_b in blobs:
        draw.ellipse(box_a, fill=LAND)
        draw.ellipse(box_b, fill=LAND)
    # The crack: an irregular fault with a short branch — not a
    # regular zigzag, so it reads as a fracture, not a chart line.
    crack = [pt(*p) for p in [
        (-82, -18), (-52, -44), (-30, -12), (-6, -38), (18, -6),
        (44, -34), (70, -8), (84, -22),
    ]]
    draw.line(crack, fill=RED, width=7, joint="curve")
    draw.line(crack, fill=RED_DARK, width=2, joint="curve")
    branch = [pt(*p) for p in [(-6, -38), (6, -58), (-2, -74)]]
    draw.line(branch, fill=RED, width=5, joint="curve")


def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # Outer frame.
    d.rectangle([8, 8, W - 9, H - 9], outline=INK, width=2)

    # ---- Masthead (Q1: boxes left/right, double rule below). ----
    top = MARGIN
    weekday_font = SANS_BOLD(16)
    check_width(d, "MONDAY", weekday_font, 200, "masthead weekday")
    d.text((MARGIN, top), "MONDAY", font=weekday_font, fill=INK)
    date_text = "23 NOVEMBER 2026"
    check_width(d, date_text, weekday_font, 300, "masthead date")
    dw = d.textlength(date_text, font=weekday_font)
    d.text((W - MARGIN - dw, top), date_text, font=weekday_font,
           fill=INK)
    title = "Six Stories, One Monday"
    title_font = SERIF_BOLD(48)
    check_width(d, title, title_font, W - 2 * MARGIN, "masthead title")
    tw = d.textlength(title, font=title_font)
    d.text(((W - tw) / 2, top + 22), title, font=title_font, fill=INK)
    rule_y = top + 92
    d.rectangle([MARGIN, rule_y, W - MARGIN, rule_y + 4], fill=INK)
    d.rectangle([MARGIN, rule_y + 9, W - MARGIN, rule_y + 10], fill=INK)

    # ---- Lead zone (Q1: big photo slot right, text columns left). ----
    lead_top = rule_y + 24
    band_h = 64
    d.rectangle([MARGIN, lead_top, W - MARGIN, lead_top + band_h], fill=RED)
    head_font = SERIF_BOLD(38)
    hw = d.textlength(LEAD_HEADLINE, font=head_font)
    if hw > W - 2 * MARGIN - 16:
        raise ValueError("lead headline too wide: %d px" % hw)
    d.text(((W - hw) / 2, lead_top + 10), LEAD_HEADLINE,
           font=head_font, fill=PAPER)

    lead_body_top = lead_top + band_h + 14
    lead_text_w = 560
    kick_font = SANS_BOLD(15)
    check_width(d, LEAD_KICKER, kick_font, lead_text_w, "lead kicker")
    d.text((MARGIN, lead_body_top), LEAD_KICKER, font=kick_font, fill=RED)
    body_font = SANS(17)
    body_lines = fit_text(d, LEAD_BODY, body_font, lead_text_w, 6,
                          "lead body")
    draw_lines(d, body_lines, MARGIN, lead_body_top + 28, body_font,
               INK, 26)
    # Small fact strip under the lead text, positioned from the real
    # line count (not a hardcoded one).
    fact_y = lead_body_top + 28 + len(body_lines) * 26 + 10
    d.rectangle([MARGIN, fact_y, MARGIN + lead_text_w, fact_y + 1],
                fill=PANEL_LINE)
    fact_font = SANS_BOLD(14)
    fact_text = "196 countries  ·  Longest COP on record"
    check_width(d, fact_text, fact_font, lead_text_w, "lead fact strip")
    d.text((MARGIN, fact_y + 8), fact_text, font=fact_font, fill=GREY)

    # Drawn scene panel on the right (the Q1 lead-photo slot).
    panel_x0 = MARGIN + lead_text_w + 24
    panel_x1 = W - MARGIN
    panel_y0 = lead_body_top - 4
    panel_y1 = lead_body_top + 28 + len(body_lines) * 26 + 34
    d.rectangle([panel_x0, panel_y0, panel_x1, panel_y1],
                outline=INK, width=2)
    # Globe radius is bounded by the panel height (the Q1 lead slot
    # is wide and short): 92 px leaves ~5 px clearance to the panel
    # border top and bottom instead of ~2 px.
    globe_r = min(92, (panel_y1 - panel_y0) // 2 - 16)
    draw_globe(d, (panel_x0 + panel_x1) // 2,
               (panel_y0 + panel_y1) // 2 - 14, globe_r)
    cap_font = SANS_BOLD(13)
    cap = "First COP with no deal since 2009."
    check_width(d, cap, cap_font, panel_x1 - panel_x0 - 16,
                "globe caption")
    cw = d.textlength(cap, font=cap_font)
    d.text(((panel_x0 + panel_x1 - cw) / 2, panel_y1 - 24), cap,
           font=cap_font, fill=INK)

    # ---- Story grid (Q1: four-column story grid, compressed). ----
    grid_top = panel_y1 + 22
    d.rectangle([MARGIN, grid_top, W - MARGIN, grid_top + 1], fill=INK)
    gap = 12
    cols = 3
    rows = 2
    card_w = (W - 2 * MARGIN - (cols - 1) * gap) // cols
    # Integer division drops the remainder; give it to the last
    # column so the grid ends flush at W - MARGIN.
    width_rem = (W - 2 * MARGIN - (cols - 1) * gap) - card_w * cols
    # Card height is derived from the footer rule, not from a nominal
    # grid bottom: the bottom row ends 16 px above the footer rule.
    foot_y = H - MARGIN - 22
    card_h = (foot_y - 16 - grid_top - 12 - gap) // rows
    cells = CARDS + [{"sources": True}]
    for i, cell in enumerate(cells):
        r, c = divmod(i, cols)
        x0 = MARGIN + c * (card_w + gap)
        y0 = grid_top + 12 + r * (card_h + gap)
        x1 = x0 + card_w + (width_rem if c == cols - 1 else 0)
        y1 = y0 + card_h
        if "sources" in cell:
            d.rectangle([x0, y0, x1, y1], outline=INK, width=1)
            src_font = SANS_BOLD(13)
            check_width(d, "SOURCES", src_font, x1 - x0 - 24,
                        "sources label")
            s_font = SANS(13)
            s_lines = fit_text(d, SOURCES_TEXT, s_font, x1 - x0 - 24, 8,
                               "sources box")
            # Centre the text block vertically: top-anchoring left
            # ~115 px of dead white below the text in this cell.
            block_h = 24 + len(s_lines) * 18
            start = y0 + max(10, (card_h - block_h) // 2)
            d.text((x0 + 12, start), "SOURCES", font=src_font,
                   fill=INK)
            draw_lines(d, s_lines, x0 + 12, start + 24, s_font, INK, 18)
            continue
        d.rectangle([x0, y0, x1, y1], outline=INK, width=1)
        d.rectangle([x0, y0, x1, y0 + 4], fill=INK)
        kx = x0 + 12
        ky = y0 + 14
        k_font = SANS_BOLD(12)
        check_width(d, cell["kicker"], k_font, x1 - x0 - 24,
                    "kicker: %s" % cell["kicker"][:20])
        d.text((kx, ky), cell["kicker"], font=k_font, fill=RED)
        h_font = SERIF_BOLD(21)
        h_lines = fit_text(d, cell["headline"], h_font, x1 - x0 - 24, 2,
                           "headline: %s" % cell["headline"][:20])
        hy = draw_lines(d, h_lines, kx, ky + 22, h_font, INK, 26)
        d.rectangle([kx, hy + 6, x1 - 12, hy + 7], fill=LIGHT)
        b_font = SANS(13)
        b_lines = fit_text(d, cell["body"], b_font, x1 - x0 - 24, 5,
                           "body: %s" % cell["headline"][:20])
        draw_lines(d, b_lines, kx, hy + 16, b_font, INK, 18)
        # Key-number strip anchored at the card bottom. It must sit
        # below the body text: fail loudly if they would collide.
        f_font = SANS_BOLD(12)
        fact_lines = fit_text(d, cell["fact"], f_font, x1 - x0 - 24, 1,
                              "fact: %s" % cell["headline"][:20])
        body_end = hy + 16 + len(b_lines) * 18
        fy = y1 - 12 - len(fact_lines) * 17
        if fy - 8 <= body_end + 4:
            raise ValueError(
                "body/fact collision in %s: body ends %d, fact at %d"
                % (cell["headline"][:20], body_end, fy))
        d.rectangle([kx, fy - 8, x1 - 12, fy - 7], fill=LIGHT)
        draw_lines(d, fact_lines, kx, fy, f_font, GREY, 17)

    # ---- Footer strip (Q1: wide bottom banner slot). ----
    d.rectangle([MARGIN, foot_y, W - MARGIN, foot_y + 1], fill=INK)
    foot = "All six stories verified against two or more wire sources  ·  Drawn entirely by program — no photographs"
    foot_font = SANS_BOLD(12)
    check_width(d, foot, foot_font, W - 2 * MARGIN, "footer")
    fw = d.textlength(foot, font=foot_font)
    d.text(((W - fw) / 2, foot_y + 7), foot, font=foot_font,
           fill=(70, 70, 70))

    return img


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or os.path.dirname(
        os.path.abspath(__file__))
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.png")
    img = render()
    if img.size != (W, H):
        raise ValueError("render size is %r, expected 1024x1024"
                         % (img.size,))
    img.save(out_path, format="PNG")
    with open(out_path, "rb") as fh:
        digest = hashlib.sha256(fh.read()).hexdigest()
    size = os.path.getsize(out_path)
    print("wrote %s (%d bytes) sha256=%s" % (out_path, size, digest))
    return out_path


if __name__ == "__main__":
    main()
