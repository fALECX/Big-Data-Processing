#!/usr/bin/env python3
"""Create a Word-compatible HTML document from the verified DOCX master."""

from __future__ import annotations

import argparse
from html import escape
from pathlib import Path

from docx import Document
from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph


def iter_blocks(document):
    for child in document.element.body.iterchildren():
        if child.tag == qn("w:p"):
            yield Paragraph(child, document)
        elif child.tag == qn("w:tbl"):
            yield Table(child, document)


def paragraph_class(paragraph):
    style_name = paragraph.style.name if paragraph.style is not None else "Normal"
    mapping = {
        "Title": "title",
        "Subtitle": "subtitle",
        "Heading 1": "heading1",
        "Heading 2": "heading2",
        "Heading 3": "heading3",
        "List Bullet": "bullet",
        "List Number": "number",
    }
    if style_name in mapping:
        return mapping[style_name]
    p_pr = paragraph._p.pPr
    if p_pr is not None and p_pr.find(qn("w:shd")) is not None:
        return "record"
    if any(run.font.name == "Consolas" for run in paragraph.runs):
        return "record"
    return "body"


def paragraph_html(paragraph, number_value=None):
    text = escape(paragraph.text)
    kind = paragraph_class(paragraph)
    if not text.strip():
        return ""
    if kind == "title":
        return f"<h1 class=\"title\">{text}</h1>"
    if kind == "subtitle":
        return f"<p class=\"subtitle\">{text}</p>"
    if kind == "heading1":
        return f"<h2 class=\"heading1\">{text}</h2>"
    if kind == "heading2":
        return f"<h3 class=\"heading2\">{text}</h3>"
    if kind == "heading3":
        return f"<h4 class=\"heading3\">{text}</h4>"
    if kind == "record":
        return f"<div class=\"record\">{text}</div>"
    if kind == "bullet":
        return f"<div class=\"list-item\"><span class=\"marker\">&#8226;</span>{text}</div>"
    if kind == "number":
        return f"<div class=\"list-item\"><span class=\"marker\">{number_value}.</span>{text}</div>"
    return f"<p>{text}</p>"


def table_html(table):
    rows = [[cell.text.strip() for cell in row.cells] for row in table.rows]
    if len(rows) == 1 and len(rows[0]) == 1:
        return f"<div class=\"callout\">{escape(rows[0][0])}</div>"

    parts = ["<table>"]
    for row_index, row in enumerate(rows):
        parts.append("<tr>")
        tag = "th" if row_index == 0 else "td"
        for value in row:
            parts.append(f"<{tag}>{escape(value)}</{tag}>")
        parts.append("</tr>")
    parts.append("</table>")
    return "".join(parts)


def build_html(docx_path, student_name):
    document = Document(docx_path)
    body_parts = []
    number_counter = 0
    previous_kind = None
    for block in iter_blocks(document):
        if isinstance(block, Paragraph):
            kind = paragraph_class(block)
            if kind == "number":
                number_counter = number_counter + 1 if previous_kind == "number" else 1
            else:
                number_counter = 0
            rendered = paragraph_html(block, number_counter or None)
            if rendered:
                body_parts.append(rendered)
            previous_kind = kind
        else:
            body_parts.append(table_html(block))
            previous_kind = "table"

    body = "\n".join(body_parts)
    safe_name = escape(student_name)
    return f"""<!DOCTYPE html>
<html xmlns:o="urn:schemas-microsoft-com:office:office"
      xmlns:w="urn:schemas-microsoft-com:office:word"
      xmlns="http://www.w3.org/TR/REC-html40">
<head>
<meta charset="utf-8">
<meta name="author" content="{safe_name}">
<meta name="title" content="COSC2637 Big Data Processing Assignment 1 Work Log">
<title>COSC2637 Big Data Processing Assignment 1 Work Log</title>
<style>
@page {{ size: Letter; margin: 0.72in 0.78in 0.72in 0.78in; }}
* {{ box-sizing: border-box; }}
body {{ font-family: Calibri, Arial, sans-serif; color: #1f2937; font-size: 10pt; line-height: 1.22; margin: 0; }}
p {{ margin: 0 0 5.5pt 0; }}
.title {{ color: #17365d; font-size: 23pt; line-height: 1.05; margin: 0 0 4pt 0; }}
.subtitle {{ color: #4b5563; font-size: 13pt; margin: 0 0 13pt 0; }}
.heading1 {{ color: #2e5e8c; font-size: 16pt; margin: 16pt 0 7pt 0; page-break-after: avoid; }}
.heading2 {{ color: #2e5e8c; font-size: 13pt; margin: 0 0 7pt 0; page-break-before: always; page-break-after: avoid; }}
.heading3 {{ color: #17365d; font-size: 11.5pt; margin: 9pt 0 4pt 0; page-break-after: avoid; }}
.record {{ font-family: Consolas, 'Courier New', monospace; font-size: 8pt; background: #f2f4f7; padding: 5.5pt 8pt; margin: 2.5pt 0 6pt 0; border-radius: 2pt; white-space: normal; page-break-inside: avoid; }}
.callout {{ background: #e8eef5; border: 1px solid #aab8c6; padding: 7pt 9pt; margin: 7pt 0; page-break-inside: avoid; }}
.list-item {{ margin: 0 0 4pt 0.48in; text-indent: -0.26in; }}
.marker {{ display: inline-block; width: 0.26in; text-indent: 0; }}
table {{ border-collapse: collapse; width: 100%; margin: 4pt 0 7pt 0; font-size: 8.75pt; page-break-inside: avoid; }}
th, td {{ border: 1px solid #c8d0d9; padding: 4.5pt 6.5pt; vertical-align: middle; text-align: left; }}
th {{ color: white; background: #17365d; font-weight: 700; }}
tr:nth-child(odd) td {{ background: #f2f4f7; }}
tr {{ page-break-inside: avoid; }}
</style>
</head>
<body>
{body}
</body>
</html>
"""


def main():
    parser = argparse.ArgumentParser(description="Create a Word-compatible work-log document.")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--html-copy", type=Path)
    parser.add_argument("--student-name", required=True)
    args = parser.parse_args()
    if not args.student_name.strip():
        raise SystemExit("Student name must not be empty")
    html = build_html(args.input.resolve(), args.student_name.strip())
    payload = html.encode("utf-8")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(payload)
    if args.html_copy:
        args.html_copy.parent.mkdir(parents=True, exist_ok=True)
        args.html_copy.write_bytes(payload)


if __name__ == "__main__":
    main()
