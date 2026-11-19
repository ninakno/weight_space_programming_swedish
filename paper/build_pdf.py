"""Build research_note.pdf (repo root) from RESEARCH_NOTE.md.

Supports the Markdown subset used in the note: '#'/'##' headings, paragraphs,
'-' bullet lists, '1.' numbered lists, pipe tables, **bold**, *italic*,
`code`, \\* (literal asterisk) and bare URLs.

Usage: .venv/bin/python paper/build_pdf.py
Edit AUTHOR / SUBTITLE below to change the title block.
"""
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (KeepTogether, ListFlowable, ListItem, Paragraph,
                                SimpleDocTemplate, Spacer, Table, TableStyle)

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "RESEARCH_NOTE.md"
OUT = ROOT / "research_note.pdf"

AUTHOR = ""                       # e.g. "Firstname Lastname, SE.LLMA"
SUBTITLE = "Research note · November 2026"

# ---------- fonts (DejaVu covers å/ä/ö, −, →, ≈, ≥, ×, ✓, ✗) ----------
FD = "/usr/share/fonts/truetype/dejavu/"
pdfmetrics.registerFont(TTFont("Serif", FD + "DejaVuSerif.ttf"))
pdfmetrics.registerFont(TTFont("Serif-Bold", FD + "DejaVuSerif-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Serif-Italic", FD + "DejaVuSerif-Italic.ttf"))
pdfmetrics.registerFont(TTFont("Serif-BoldItalic", FD + "DejaVuSerif-BoldItalic.ttf"))
pdfmetrics.registerFont(TTFont("Sans", FD + "DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("Sans-Bold", FD + "DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Mono", FD + "DejaVuSansMono.ttf"))
pdfmetrics.registerFontFamily("Serif", normal="Serif", bold="Serif-Bold",
                              italic="Serif-Italic", boldItalic="Serif-BoldItalic")

ACCENT = colors.HexColor("#1f3a5f")
RULE = colors.HexColor("#b8c2cc")

body = ParagraphStyle("body", fontName="Serif", fontSize=10, leading=14.2, spaceAfter=6)
small = ParagraphStyle("small", parent=body, fontSize=8.8, leading=11.5, spaceAfter=0)
title = ParagraphStyle("title", fontName="Sans-Bold", fontSize=17, leading=21,
                       alignment=TA_CENTER, textColor=ACCENT, spaceAfter=6)
subtitle = ParagraphStyle("subtitle", fontName="Sans", fontSize=10, leading=13,
                          alignment=TA_CENTER, textColor=colors.HexColor("#555555"), spaceAfter=2)
h2 = ParagraphStyle("h2", fontName="Sans-Bold", fontSize=12.5, leading=16,
                    textColor=ACCENT, spaceBefore=12, spaceAfter=5)
ref = ParagraphStyle("ref", parent=body, fontSize=9.2, leading=12.5, leftIndent=14,
                     firstLineIndent=-14, spaceAfter=4)


def inline(text: str) -> str:
    """Markdown inline -> ReportLab mini-HTML."""
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = text.replace("\\*", "\x00")                     # literal asterisk
    codes = []

    def keep_code(m):
        codes.append(m.group(1))
        return f"\x01{len(codes) - 1}\x01"

    text = re.sub(r"`([^`]+)`", keep_code, text)
    text = re.sub(r"(https?://[^\s)]+[^\s).,])",
                  lambda m: f'<link href="{m.group(1)}" color="#1f3a5f">{m.group(1)}</link>', text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<i>\1</i>", text)
    text = text.replace("✅", '<font name="Sans" color="#2e7d32">✓</font>')
    text = text.replace("❌", '<font name="Sans" color="#c62828">✗</font>')
    text = re.sub(r"\x01(\d+)\x01",
                  lambda m: f'<font name="Mono" size="8.6">{codes[int(m.group(1))]}</font>', text)
    return text.replace("\x00", "*")


def blocks(md: str):
    """Split into (kind, lines) blocks."""
    out, cur, kind = [], [], None

    def flush():
        nonlocal cur, kind
        if cur:
            out.append((kind, cur))
        cur, kind = [], None

    for line in md.splitlines():
        s = line.rstrip()
        if not s:
            flush()
            continue
        if s.startswith("# ") or s.startswith("## "):
            flush()
            out.append(("h1" if s.startswith("# ") else "h2", [s.lstrip("#").strip()]))
            continue
        k = ("table" if s.startswith("|") else "ul" if s.startswith("- ")
             else "ol" if re.match(r"\d+\. ", s) else None)
        if kind is None:
            kind = k or "p"
        elif k and kind == "p":
            flush()
            kind = k
        cur.append(s)
    flush()
    return out


def list_items(lines, ordered):
    items, cur = [], []
    for s in lines:
        if (ordered and re.match(r"\d+\. ", s)) or (not ordered and s.startswith("- ")):
            if cur:
                items.append(" ".join(cur))
            cur = [re.sub(r"^(\d+\.|-)\s+", "", s)]
        else:
            cur.append(s.strip())
    items.append(" ".join(cur))
    return items


def make_table(lines, width):
    rows = [[c.strip() for c in l.strip("|").split("|")] for l in lines]
    rows = [r for r in rows if not all(re.fullmatch(r":?-+:?", c) for c in r if c)]
    ncol = len(rows[0])
    lens = [max(len(re.sub(r"[*`]", "", r[i])) for r in rows) for i in range(ncol)]
    lens = [max(l, 6) for l in lens]
    colw = [width * l / sum(lens) for l in lens]
    cells = [[Paragraph(("<b>%s</b>" if i == 0 else "%s") % inline(c), small) for c in r]
             for i, r in enumerate(rows)]
    t = Table(cells, colWidths=colw, repeatRows=1, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("LINEABOVE", (0, 0), (-1, 0), 0.8, ACCENT),
        ("LINEBELOW", (0, 0), (-1, 0), 0.5, ACCENT),
        ("LINEBELOW", (0, -1), (-1, -1), 0.8, ACCENT),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f3f6f9")]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return t


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Sans", 8)
    canvas.setFillColor(colors.HexColor("#777777"))
    canvas.drawCentredString(A4[0] / 2, 12 * mm, str(doc.page))
    canvas.restoreState()


def build():
    md = SRC.read_text()
    doc = SimpleDocTemplate(str(OUT), pagesize=A4, leftMargin=22 * mm, rightMargin=22 * mm,
                            topMargin=20 * mm, bottomMargin=20 * mm,
                            title="Training-free weight editing for Swedish subordinate-clause word order",
                            author=AUTHOR or "")
    width = A4[0] - 44 * mm
    story, in_refs = [], False
    for kind, lines in blocks(md):
        if kind == "h1":
            t = re.sub(r"^Research note:\s*", "", lines[0])
            story += [Paragraph(inline(t), title)]
            if AUTHOR:
                story.append(Paragraph(inline(AUTHOR), subtitle))
            story += [Paragraph(inline(SUBTITLE), subtitle), Spacer(1, 4)]
            story.append(Table([[""]], colWidths=[width], rowHeights=[2],
                               style=[("LINEBELOW", (0, 0), (-1, -1), 0.6, RULE)]))
            story.append(Spacer(1, 6))
        elif kind == "h2":
            in_refs = lines[0].lower().startswith("references")
            story.append(Paragraph(inline(lines[0]), h2))
        elif kind == "table":
            story += [make_table(lines, width), Spacer(1, 8)]
        elif kind in ("ul", "ol"):
            items = list_items(lines, kind == "ol")
            lf = ListFlowable([ListItem(Paragraph(inline(i), body), leftIndent=14) for i in items],
                              bulletType="1" if kind == "ol" else "bullet", start="1" if kind == "ol" else "•",
                              leftIndent=14, bulletFontName="Serif", bulletFontSize=9)
            story += [lf, Spacer(1, 2)]
        else:
            story.append(Paragraph(inline(" ".join(lines)), ref if in_refs else body))
    # keep each heading with the block that follows it
    merged = []
    for f in story:
        if merged and isinstance(merged[-1], Paragraph) and merged[-1].style is h2:
            merged[-1] = KeepTogether([merged[-1], f])
        else:
            merged.append(f)
    doc.build(merged, onFirstPage=footer, onLaterPages=footer)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    build()
