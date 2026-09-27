#!/usr/bin/env python3
"""Build the standalone Assignment 1 code PDF for Turnitin submission."""

from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    KeepTogether,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


STUDENT_ID = "s4271512"
COURSE = "COSC2637 Big Data Processing"
TITLE = "Assignment 1 - Code Submission"

SOURCE_FILES = [
    ("Task 1", "Task 1/task1_mapper.py"),
    ("Task 1", "Task 1/task1_reducer.py"),
    ("Task 1", "Task 1/task1-run.sh"),
    ("Task 2", "Task 2/task2_mapper.py"),
    ("Task 2", "Task 2/task2_reducer.py"),
    ("Task 2", "Task 2/task2_driver.py"),
    ("Task 2", "Task 2/task2-run.sh"),
    ("Task 3", "Task 3/task3_job1_mapper.py"),
    ("Task 3", "Task 3/task3_job1_reducer.py"),
    ("Task 3", "Task 3/task3_job2_mapper.py"),
    ("Task 3", "Task 3/task3_job2_reducer.py"),
    ("Task 3", "Task 3/task3_job3_mapper.py"),
    ("Task 3", "Task 3/task3_job3_reducer.py"),
    ("Task 3", "Task 3/task3-run.sh"),
]


def numbered_source(text):
    lines = text.splitlines()
    width = len(str(max(1, len(lines))))
    return "\n".join(
        f"{number:>{width}}  {line}" for number, line in enumerate(lines, start=1)
    )


def page_furniture(canvas, document):
    canvas.saveState()
    canvas.setTitle(f"{COURSE} {TITLE}")
    canvas.setAuthor(STUDENT_ID)
    canvas.setSubject("Python and Bash source code submitted for Assignment 1")
    width, height = landscape(letter)
    if document.page > 1:
        canvas.setFillColor(colors.HexColor("#555555"))
        canvas.setFont("Helvetica", 8)
        canvas.drawString(0.55 * inch, height - 0.31 * inch, COURSE)
        canvas.drawRightString(width - 0.55 * inch, height - 0.31 * inch, STUDENT_ID)
    canvas.setFillColor(colors.HexColor("#666666"))
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(width - 0.55 * inch, 0.30 * inch, f"Page {document.page}")
    canvas.restoreState()


def build(assignment_dir, output_pdf):
    assignment_dir = Path(assignment_dir)
    output_pdf = Path(output_pdf)
    output_pdf.parent.mkdir(parents=True, exist_ok=True)

    page_width, _page_height = landscape(letter)
    document = SimpleDocTemplate(
        str(output_pdf),
        pagesize=landscape(letter),
        leftMargin=0.55 * inch,
        rightMargin=0.55 * inch,
        topMargin=0.55 * inch,
        bottomMargin=0.48 * inch,
        title=f"{COURSE} {TITLE}",
        author=STUDENT_ID,
        subject="Python and Bash source code submitted for Assignment 1",
    )

    styles = getSampleStyleSheet()
    cover_title = ParagraphStyle(
        "CoverTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=19,
        leading=23,
        textColor=colors.black,
        alignment=TA_LEFT,
        spaceAfter=8,
    )
    cover_subtitle = ParagraphStyle(
        "CoverSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#555555"),
        alignment=TA_LEFT,
        spaceAfter=4,
    )
    file_heading = ParagraphStyle(
        "FileHeading",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=15,
        textColor=colors.black,
        alignment=TA_LEFT,
        spaceAfter=8,
    )
    file_meta = ParagraphStyle(
        "FileMeta",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#666666"),
        spaceAfter=8,
    )
    code_style = ParagraphStyle(
        "Code",
        fontName="Courier",
        fontSize=7.25,
        leading=8.7,
        textColor=colors.HexColor("#111111"),
        leftIndent=0,
        rightIndent=0,
        spaceBefore=0,
        spaceAfter=0,
    )
    index_style = ParagraphStyle(
        "Index",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#222222"),
    )

    story = [Spacer(1, 0.18 * inch)]
    story.append(Paragraph(escape(TITLE), cover_title))
    story.append(Paragraph(escape(COURSE), cover_subtitle))
    story.append(Paragraph("Postgraduate individual submission", cover_subtitle))
    story.append(Spacer(1, 0.18 * inch))
    details = [
        ["Student ID", STUDENT_ID],
        ["Assessment", "Assignment 1"],
        ["Contents", "Python source and Bash run scripts from Tasks 1, 2, and 3"],
    ]
    detail_table = Table(details, colWidths=[1.55 * inch, 5.75 * inch], hAlign="CENTER")
    detail_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("TEXTCOLOR", (0, 0), (0, -1), colors.black),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("LINEBELOW", (0, -1), (-1, -1), 0.4, colors.HexColor("#BDBDBD")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    story.append(detail_table)
    story.append(Spacer(1, 0.12 * inch))

    index_rows = [["Task", "File", "Lines"]]
    for task, relative in SOURCE_FILES:
        path = assignment_dir / relative
        line_count = len(path.read_text(encoding="utf-8").splitlines())
        index_rows.append([task, Path(relative).name, str(line_count)])
    index_table = Table(
        index_rows,
        colWidths=[1.0 * inch, 4.9 * inch, 0.75 * inch],
        hAlign="CENTER",
        repeatRows=1,
    )
    index_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EEEEEE")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#BDBDBD")),
                ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                ("ALIGN", (2, 1), (2, -1), "RIGHT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    story.append(index_table)

    for task, relative in SOURCE_FILES:
        path = assignment_dir / relative
        source = path.read_text(encoding="utf-8")
        story.append(PageBreak())
        story.append(
            KeepTogether(
                [
                    Paragraph(escape(path.name), file_heading),
                    Paragraph(
                        escape(f"{task} | {relative} | {len(source.splitlines())} lines"),
                        file_meta,
                    ),
                ]
            )
        )
        story.append(Preformatted(numbered_source(source), code_style, maxLineLength=150))

    document.build(story, onFirstPage=page_furniture, onLaterPages=page_furniture)
    return output_pdf


if __name__ == "__main__":
    workspace = Path(__file__).resolve().parents[1]
    build(
        workspace / "Assignment 1",
        workspace / "output" / "pdf" / "s4271512_PG.pdf",
    )
