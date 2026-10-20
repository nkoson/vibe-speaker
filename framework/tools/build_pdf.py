#!/usr/bin/env python3
"""Assemble Markdown documents and their images into one PDF.

  build_pdf.py --out final/design-package.pdf --title "Three-way design" --md final/README.md --md final/01-cabinet-construction.md ...
  build_pdf.py --out final/design-package.pdf --title "..." --folder final/      (every *.md in the folder, sorted by name)

Supported Markdown: # ## ### headings, paragraphs, - or * bullets, 1. numbered
lists, | tables |, ![alt](image.png), fenced code blocks, **bold**, *italic*,
`code`. Image paths resolve relative to the Markdown file. Each document starts
on a new page; page numbers and the title sit in the footer. --preview DIR
renders every page to PNG so the result can be inspected as images.
HTTP(S) Markdown links retain clickable labels. A standalone
<!-- pagebreak --> inserts an explicit page break.
"""
import argparse
import re
import sys
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (Image, KeepTogether, ListFlowable, ListItem, PageBreak, Paragraph, Preformatted, SimpleDocTemplate, Spacer, Table,
                                TableStyle)
from reportlab.lib.utils import ImageReader

PAGE = A4
MARGIN = 18 * mm
BODY_WIDTH = PAGE[0] - 2 * MARGIN


def styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("title", parent=base["Title"], fontSize=24, leading=30, spaceAfter=12),
        "subtitle": ParagraphStyle("subtitle", parent=base["Normal"], fontSize=12, leading=16, textColor=colors.HexColor("#444444")),
        "h1": ParagraphStyle("h1", parent=base["Heading1"], fontSize=18, leading=22, spaceBefore=6, spaceAfter=8, keepWithNext=True),
        "h2": ParagraphStyle("h2", parent=base["Heading2"], fontSize=14, leading=18, spaceBefore=10, spaceAfter=6, keepWithNext=True),
        "h3": ParagraphStyle("h3", parent=base["Heading3"], fontSize=11.5, leading=15, spaceBefore=8, spaceAfter=4, keepWithNext=True),
        "body": ParagraphStyle("body", parent=base["Normal"], fontSize=9.5, leading=13, alignment=TA_LEFT, spaceAfter=5),
        "cell": ParagraphStyle("cell", parent=base["Normal"], fontSize=8, leading=10),
        "cellhead": ParagraphStyle("cellhead", parent=base["Normal"], fontSize=8, leading=10, fontName="Helvetica-Bold"),
        "code": ParagraphStyle("code", parent=base["Code"], fontSize=7.5, leading=9.5, backColor=colors.HexColor("#f4f4f4"), leftIndent=4, spaceAfter=6),
        "caption": ParagraphStyle("caption", parent=base["Normal"], fontSize=8, leading=10, textColor=colors.HexColor("#555555"), spaceAfter=8),
    }


def inline(text):
    """Escape XML and convert bold, italic and code spans to reportlab markup."""
    text = escape(text)
    text = re.sub(r"`([^`]+)`", r'<font face="Courier">\1</font>', text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<i>\1</i>", text)
    def link(match):
        label, target = match.groups()
        if target.startswith(("https://", "http://")):
            # XML text was escaped above; quote attribute delimiters as well.
            target = target.replace('"', "&quot;")
            return f'<link href="{target}" color="#167895">{label}</link>'
        return f'{label} (<font face="Courier">{target}</font>)'
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link, text)
    return text


def image_flowable(path, caption, st):
    reader = ImageReader(str(path))
    width, height = reader.getSize()
    scale = min(BODY_WIDTH / width, (PAGE[1] - 2 * MARGIN - 60) / height, 1.0)
    items = [Image(str(path), width=width * scale, height=height * scale)]
    if caption:
        items.append(Paragraph(inline(caption), st["caption"]))
    return KeepTogether(items)


def table_flowable(rows, st):
    header = [Paragraph(inline(c), st["cellhead"]) for c in rows[0]]
    body = [[Paragraph(inline(c), st["cell"]) for c in row] for row in rows[1:]]
    columns = max(len(r) for r in rows)
    data = [header + [Paragraph("", st["cell"])] * (columns - len(header))] + [r + [Paragraph("", st["cell"])] * (columns - len(r)) for r in body]
    widths = [BODY_WIDTH / columns] * columns
    table = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8e8e8")),
        ("GRID", (0, 0), (-1, -1), .3, colors.HexColor("#999999")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    return table


def split_row(line):
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    return cells


def render_markdown(path, st, warnings):
    """Convert one Markdown file to a list of flowables."""
    text = Path(path).read_text()
    lines = text.splitlines()
    flow = []
    paragraph = []
    bullets = []
    numbered = []
    table = []
    code = None

    def flush_paragraph():
        if paragraph:
            flow.append(Paragraph(inline(" ".join(paragraph)), st["body"]))
            paragraph.clear()

    def flush_lists():
        if bullets:
            flow.append(ListFlowable([ListItem(Paragraph(inline(b), st["body"]), leftIndent=12) for b in bullets], bulletType="bullet", start="•", leftIndent=14))
            bullets.clear()
        if numbered:
            flow.append(ListFlowable([ListItem(Paragraph(inline(b), st["body"]), leftIndent=12) for b in numbered], bulletType="1", leftIndent=16))
            numbered.clear()

    def flush_table():
        if table:
            rows = [split_row(r) for r in table if not re.match(r"^\s*\|?\s*:?-{2,}", r)]
            if rows:
                flow.append(table_flowable(rows, st))
                flow.append(Spacer(1, 6))
            table.clear()

    def flush_all():
        flush_paragraph()
        flush_lists()
        flush_table()

    for raw in lines:
        line = raw.rstrip()
        if code is not None:
            if line.startswith("```"):
                flow.append(Preformatted("\n".join(code), st["code"]))
                code = None
            else:
                code.append(line)
            continue
        if line.startswith("```"):
            flush_all()
            code = []
            continue
        if line.strip() == "<!-- pagebreak -->":
            flush_all()
            flow.append(PageBreak())
            continue
        if not line.strip():
            flush_all()
            continue
        m = re.match(r"^(#{1,3})\s+(.*)$", line)
        if m:
            flush_all()
            level = len(m.group(1))
            flow.append(Paragraph(inline(m.group(2)), st[f"h{level}"]))
            continue
        m = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)\s*$", line)
        if m:
            flush_all()
            image = (Path(path).parent / m.group(2)).resolve()
            if image.exists():
                flow.append(image_flowable(image, m.group(1), st))
            else:
                warnings.append(f"{Path(path).name}: missing image {m.group(2)}")
                flow.append(Paragraph(inline(f"[missing image: {m.group(2)}]"), st["caption"]))
            continue
        if line.lstrip().startswith("|"):
            flush_paragraph()
            flush_lists()
            table.append(line)
            continue
        m = re.match(r"^\s*[-*]\s+(.*)$", line)
        if m:
            flush_paragraph()
            flush_table()
            bullets.append(m.group(1))
            continue
        m = re.match(r"^\s*\d+[.)]\s+(.*)$", line)
        if m:
            flush_paragraph()
            flush_table()
            numbered.append(m.group(1))
            continue
        if bullets and line.startswith("  "):
            bullets[-1] += " " + line.strip()
            continue
        if numbered and line.startswith("  "):
            numbered[-1] += " " + line.strip()
            continue
        flush_lists()
        flush_table()
        paragraph.append(line.strip())
    if code is not None:
        flow.append(Preformatted("\n".join(code), st["code"]))
    flush_all()
    return flow


def build(out, title, subtitle, files):
    st = styles()
    warnings = []
    story = [Spacer(1, 120), Paragraph(inline(title), st["title"])]
    if subtitle:
        story.append(Paragraph(inline(subtitle), st["subtitle"]))
    story.append(Spacer(1, 24))
    story.append(Paragraph(inline("Contents"), st["h2"]))
    for f in files:
        heading = re.search(r"^#\s+(.+)$", Path(f).read_text(), re.MULTILINE)
        label = heading.group(1) if heading else Path(f).stem.replace("-", " ").replace("_", " ")
        story.append(Paragraph(inline(label), st["body"]))
    for f in files:
        story.append(PageBreak())
        story.extend(render_markdown(f, st, warnings))

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#666666"))
        canvas.drawString(MARGIN, 10 * mm, title)
        canvas.drawRightString(PAGE[0] - MARGIN, 10 * mm, f"Page {doc.page}")
        canvas.restoreState()

    doc = SimpleDocTemplate(str(out), pagesize=PAGE, leftMargin=MARGIN, rightMargin=MARGIN, topMargin=MARGIN, bottomMargin=MARGIN, title=title)
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return warnings


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--subtitle", default="")
    parser.add_argument("--md", action="append", default=[], help="Markdown file, in order; repeatable")
    parser.add_argument("--folder", help="take every *.md in this folder, sorted by name")
    parser.add_argument("--preview", help="folder that receives one PNG per page for visual checking")
    args = parser.parse_args()
    files = [Path(f) for f in args.md]
    if args.folder:
        files += sorted(Path(args.folder).glob("*.md"))
    if not files:
        raise SystemExit("give --md files or --folder")
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    warnings = build(args.out, args.title, args.subtitle, files)
    for w in warnings:
        print("warning:", w, file=sys.stderr)
    print(args.out)
    if args.preview:
        for page in preview(args.out, args.preview):
            print(page)


def preview(pdf, folder, scale=1.3):
    """Render every page to <folder>/page-NN.png; returns the written paths."""
    import pypdfium2 as pdfium
    out = Path(folder)
    out.mkdir(parents=True, exist_ok=True)
    document = pdfium.PdfDocument(str(pdf))
    paths = []
    for index in range(len(document)):
        path = out / f"page-{index + 1:02d}.png"
        document[index].render(scale=scale).to_pil().save(path)
        paths.append(path)
    return paths


if __name__ == "__main__":
    main()
