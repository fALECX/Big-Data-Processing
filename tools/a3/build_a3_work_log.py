#!/usr/bin/env python3
"""Fill the A3 work-log template for the individual PG submission.

Section 1 (member contribution) is marked not applicable, as the specification
allows for individual submissions. Section 2 ticks only the checklist items
that apply to an individual submission; the two group-membership items are
marked not applicable. The DOCX is converted to Word 97 .doc separately.
"""

import copy
from pathlib import Path

from docx import Document
from docx.oxml.ns import qn

WORKSPACE = Path(__file__).resolve().parents[2]
TEMPLATE = WORKSPACE / "Assignment 3" / "Templates" / "A3_GroupLeaderStudentID_GroupNumber_UGorPG_worklog.docx"
OUTPUT = WORKSPACE / "output" / "A3" / "docx" / "s4271512_PG.docx"

STUDENT = "Samuel Klefe (s4271512)"
NOT_APPLICABLE = "Not applicable - individual submission."
GROUP_ITEMS = ("All members have joined", "The correct group members are listed")


def set_paragraph_text(paragraph, text):
    """Replace a paragraph's text while keeping the formatting of its first run."""
    runs = paragraph.runs
    runs[0].text = text
    for run in runs[1:]:
        run._r.getparent().remove(run._r)


def set_cell_text(cell, text):
    first = cell.paragraphs[0]
    if first.runs:
        set_paragraph_text(first, text)
    else:
        first.add_run(text)
    for extra in cell.paragraphs[1:]:
        extra._p.getparent().remove(extra._p)


def fill_log_table(table, first_row):
    for cell, text in zip(table.rows[1].cells, first_row):
        set_cell_text(cell, text)
    for row in list(table.rows)[2:]:
        row._tr.getparent().remove(row._tr)


def tick(paragraph):
    for box in paragraph._p.iter(qn("w:checkBox")):
        box.find(qn("w:default")).set(qn("w:val"), "1")
        checked = box.find(qn("w:checked"))
        if checked is None:
            checked = copy.deepcopy(box.find(qn("w:default")))
            checked.tag = qn("w:checked")
            box.append(checked)
        checked.set(qn("w:val"), "1")


def build():
    document = Document(TEMPLATE)
    paragraphs = document.paragraphs
    tables = document.tables

    # Section 1: member contribution (not applicable for an individual submission).
    group_number = next(p for p in paragraphs if p.text.startswith("Group Number:"))
    set_paragraph_text(group_number, "Group Number: " + NOT_APPLICABLE)
    members, screenshot = tables[0].rows[0].cells
    set_cell_text(members, "Group Members: " + NOT_APPLICABLE + " Student: " + STUDENT
                  + ", Postgraduate (COSC2637).")
    set_cell_text(screenshot, "Canvas A3 group screenshot: " + NOT_APPLICABLE
                  + " No Canvas A3 group was joined.")
    fill_log_table(tables[1], ["-", NOT_APPLICABLE, STUDENT, "-", "-"])
    fill_log_table(tables[2], ["Tasks 1-3 (a3.scala, a3.jar)", STUDENT, "25/10/2026",
                               "Individual submission."])

    # Section 2: submission declaration checklist.
    for paragraph in paragraphs:
        if not any(box is not None for box in paragraph._p.iter(qn("w:checkBox"))):
            continue
        if paragraph.text.strip().startswith(GROUP_ITEMS):
            paragraph.runs[-1].text = paragraph.runs[-1].text.rstrip() + " (" + NOT_APPLICABLE.rstrip(".") + ")"
        else:
            tick(paragraph)

    properties = document.core_properties
    properties.author = "Samuel Klefe"
    properties.last_modified_by = "Samuel Klefe"
    properties.title = "Assignment 3 work log - s4271512_PG"
    properties.comments = ""
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    document.save(OUTPUT)
    return OUTPUT


if __name__ == "__main__":
    print(build())
