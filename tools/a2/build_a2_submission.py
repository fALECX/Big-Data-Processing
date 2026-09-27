#!/usr/bin/env python3
"""Build the Assignment 2 ZIP and Turnitin code PDF (individual PG submission).

The ZIP is flat and contains exactly task2.pig and task2.py. The PDF is a plain
monospaced copy of both source files, as the specification asks for.
"""

from pathlib import Path
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Preformatted, SimpleDocTemplate, Spacer

WORKSPACE = Path(__file__).resolve().parents[2]
SOURCE_DIR = WORKSPACE / "Assignment 2" / "Task 2"
OUTPUT_DIR = WORKSPACE / "output" / "A2" / "submission"
BASE_NAME = "s4271512_PG"
SOURCE_FILES = ("task2.pig", "task2.py")
TITLE = "COSC2637 Assignment 2 - Task 2 source code (s4271512)"


def read_source(name):
    data = (SOURCE_DIR / name).read_bytes()
    if b"\r" in data:
        raise ValueError(f"{name} must use LF line endings")
    return data


def build_zip():
    path = OUTPUT_DIR / f"{BASE_NAME}.zip"
    with ZipFile(path, "w", ZIP_DEFLATED, compresslevel=9) as archive:
        for name in SOURCE_FILES:
            info = ZipInfo(name, date_time=(2026, 9, 27, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = ZIP_DEFLATED
            archive.writestr(info, read_source(name))
    return path


def build_pdf():
    path = OUTPUT_DIR / f"{BASE_NAME}.pdf"
    document = SimpleDocTemplate(
        str(path), pagesize=A4,
        leftMargin=0.6 * inch, rightMargin=0.6 * inch,
        topMargin=0.6 * inch, bottomMargin=0.6 * inch,
        title=TITLE, author="s4271512", subject="Pig and Jython UDF source code",
    )
    heading = ParagraphStyle("Heading", fontName="Courier-Bold", fontSize=9, leading=12, spaceAfter=6)
    code = ParagraphStyle("Code", fontName="Courier", fontSize=8, leading=9.6)
    story = [Paragraph(escape(TITLE), heading), Spacer(1, 6)]
    for name in SOURCE_FILES:
        story.append(Paragraph(escape(f"===== {name} ====="), heading))
        story.append(Preformatted(read_source(name).decode("utf-8"), code, maxLineLength=104))
        story.append(Spacer(1, 14))
    document.build(story)
    return path


if __name__ == "__main__":
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(build_zip())
    print(build_pdf())
