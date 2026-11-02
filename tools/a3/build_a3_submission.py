#!/usr/bin/env python3
"""Build the Assignment 3 ZIP and Turnitin code PDF (individual PG submission).

The ZIP is flat and contains exactly a3.jar and a3.scala. The PDF is a plain
monospaced copy of a3.scala, as the specification asks for.
"""

from pathlib import Path
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Preformatted, SimpleDocTemplate, Spacer

WORKSPACE = Path(__file__).resolve().parents[2]
SOURCE = WORKSPACE / "Assignment 3" / "a3-project" / "src" / "main" / "scala" / "streaming" / "a3.scala"
JAR = WORKSPACE / "output" / "A3" / "build" / "a3.jar"
OUTPUT_DIR = WORKSPACE / "output" / "A3" / "submission"
BASE_NAME = "s4271512_PG"
TITLE = "COSC2637 Assignment 3 - a3.scala source code (s4271512)"


def read_source():
    data = SOURCE.read_bytes()
    if b"\r" in data:
        raise ValueError("a3.scala must use LF line endings")
    data.decode("ascii")  # plain text only, so the PDF text matches the source exactly
    return data


def build_zip():
    path = OUTPUT_DIR / f"{BASE_NAME}.zip"
    entries = (("a3.jar", JAR.read_bytes()), ("a3.scala", read_source()))
    with ZipFile(path, "w", ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in entries:
            info = ZipInfo(name, date_time=(2026, 10, 25, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = ZIP_DEFLATED
            archive.writestr(info, data)
    return path


def build_pdf():
    path = OUTPUT_DIR / f"{BASE_NAME}.pdf"
    document = SimpleDocTemplate(
        str(path), pagesize=A4,
        leftMargin=0.6 * inch, rightMargin=0.6 * inch,
        topMargin=0.6 * inch, bottomMargin=0.6 * inch,
        title=TITLE, author="s4271512", subject="Spark Streaming Scala source code",
    )
    heading = ParagraphStyle("Heading", fontName="Courier-Bold", fontSize=9, leading=12, spaceAfter=6)
    code = ParagraphStyle("Code", fontName="Courier", fontSize=8, leading=9.6)
    story = [
        Paragraph(escape(TITLE), heading),
        Spacer(1, 6),
        Paragraph(escape("===== a3.scala ====="), heading),
        Preformatted(read_source().decode("ascii"), code, maxLineLength=110),
    ]
    document.build(story)
    return path


if __name__ == "__main__":
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(build_zip())
    print(build_pdf())
