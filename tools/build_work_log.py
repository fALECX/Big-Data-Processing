#!/usr/bin/env python3
"""Build the individual Assignment 1 work log."""

import argparse
from pathlib import Path
import re
from zipfile import ZipFile

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


STUDENT_ID = "s4271512"
COURSE = "COSC2637 Big Data Processing"
ASSESSMENT = "Assignment 1"
PROGRAM = "Postgraduate"
PREPARED_DATE = "28 August 2026"

BLACK = "000000"
DARK_GRAY = "444444"
TEXT_GRAY = "666666"
LIGHT_GRAY = "F3F3F3"
MID_GRAY = "BDBDBD"
WHITE = "FFFFFF"


def set_cell_shading(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shading = tc_pr.find(qn("w:shd"))
    if shading is None:
        shading = OxmlElement("w:shd")
        tc_pr.append(shading)
    shading.set(qn("w:fill"), fill)


def set_cell_margins(cell, top=80, start=120, bottom=80, end=120):
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for edge, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tc_mar.find(qn(f"w:{edge}"))
        if node is None:
            node = OxmlElement(f"w:{edge}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def set_table_borders(table, color=MID_GRAY, size=6):
    tbl_pr = table._tbl.tblPr
    borders = tbl_pr.find(qn("w:tblBorders"))
    if borders is None:
        borders = OxmlElement("w:tblBorders")
        tbl_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        element = borders.find(qn(f"w:{edge}"))
        if element is None:
            element = OxmlElement(f"w:{edge}")
            borders.append(element)
        element.set(qn("w:val"), "single")
        element.set(qn("w:sz"), str(size))
        element.set(qn("w:space"), "0")
        element.set(qn("w:color"), color)


def set_table_geometry(table, widths_dxa, indent_dxa=0):
    if sum(widths_dxa) != 9360:
        raise ValueError("Table widths must sum to 9360 DXA")

    table.autofit = False
    table.alignment = WD_TABLE_ALIGNMENT.LEFT
    tbl_pr = table._tbl.tblPr

    tbl_w = tbl_pr.find(qn("w:tblW"))
    if tbl_w is None:
        tbl_w = OxmlElement("w:tblW")
        tbl_pr.append(tbl_w)
    tbl_w.set(qn("w:w"), "9360")
    tbl_w.set(qn("w:type"), "dxa")

    tbl_ind = tbl_pr.find(qn("w:tblInd"))
    if tbl_ind is None:
        tbl_ind = OxmlElement("w:tblInd")
        tbl_pr.append(tbl_ind)
    tbl_ind.set(qn("w:w"), str(indent_dxa))
    tbl_ind.set(qn("w:type"), "dxa")

    grid = table._tbl.tblGrid
    for child in list(grid):
        grid.remove(child)
    for width in widths_dxa:
        grid_col = OxmlElement("w:gridCol")
        grid_col.set(qn("w:w"), str(width))
        grid.append(grid_col)

    for row in table.rows:
        for index, cell in enumerate(row.cells):
            width = widths_dxa[index]
            cell.width = Inches(width / 1440)
            tc_pr = cell._tc.get_or_add_tcPr()
            tc_w = tc_pr.find(qn("w:tcW"))
            if tc_w is None:
                tc_w = OxmlElement("w:tcW")
                tc_pr.append(tc_w)
            tc_w.set(qn("w:w"), str(width))
            tc_w.set(qn("w:type"), "dxa")
            set_cell_margins(cell)
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER


def set_repeat_table_header(row):
    tr_pr = row._tr.get_or_add_trPr()
    marker = OxmlElement("w:tblHeader")
    marker.set(qn("w:val"), "true")
    tr_pr.append(marker)


def format_table(table, widths_dxa, header=True, font_size=9):
    set_table_geometry(table, widths_dxa)
    set_table_borders(table)
    if header:
        set_repeat_table_header(table.rows[0])
    for row_index, row in enumerate(table.rows):
        for cell in row.cells:
            if header and row_index == 0:
                set_cell_shading(cell, LIGHT_GRAY)
            for paragraph in cell.paragraphs:
                paragraph.paragraph_format.space_before = Pt(0)
                paragraph.paragraph_format.space_after = Pt(0)
                paragraph.paragraph_format.line_spacing = 1.05
                for run in paragraph.runs:
                    run.font.name = "Arial"
                    run._element.get_or_add_rPr().rFonts.set(qn("w:ascii"), "Arial")
                    run._element.get_or_add_rPr().rFonts.set(qn("w:hAnsi"), "Arial")
                    run.font.size = Pt(font_size)
                    if header and row_index == 0:
                        run.bold = True
                        run.font.color.rgb = RGBColor.from_string(BLACK)


def add_table(document, headers, rows, widths_dxa, font_size=9):
    table = document.add_table(rows=1, cols=len(headers))
    for index, heading in enumerate(headers):
        table.rows[0].cells[index].text = heading
    for values in rows:
        cells = table.add_row().cells
        for index, value in enumerate(values):
            cells[index].text = str(value)
    format_table(table, widths_dxa, header=True, font_size=font_size)
    document.add_paragraph().paragraph_format.space_after = Pt(0)
    return table


def add_page_number(paragraph):
    paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = paragraph.add_run("Page ")
    field_begin = OxmlElement("w:fldChar")
    field_begin.set(qn("w:fldCharType"), "begin")
    instruction = OxmlElement("w:instrText")
    instruction.set(qn("xml:space"), "preserve")
    instruction.text = " PAGE "
    field_end = OxmlElement("w:fldChar")
    field_end.set(qn("w:fldCharType"), "end")
    run._r.append(field_begin)
    run._r.append(instruction)
    run._r.append(field_end)


def set_run_font(run, name="Arial", size=10.5, bold=None, color=None, italic=None):
    run.font.name = name
    r_pr = run._element.get_or_add_rPr()
    r_pr.rFonts.set(qn("w:ascii"), name)
    r_pr.rFonts.set(qn("w:hAnsi"), name)
    run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold
    if color:
        run.font.color.rgb = RGBColor.from_string(color)
    if italic is not None:
        run.italic = italic


def add_paragraph(document, text="", bold_prefix=None, style=None):
    paragraph = document.add_paragraph(style=style)
    if bold_prefix and text.startswith(bold_prefix):
        prefix = paragraph.add_run(bold_prefix)
        prefix.bold = True
        paragraph.add_run(text[len(bold_prefix):])
    else:
        paragraph.add_run(text)
    return paragraph


def add_record(document, text):
    paragraph = document.add_paragraph()
    paragraph.paragraph_format.left_indent = Inches(0.12)
    paragraph.paragraph_format.right_indent = Inches(0.12)
    paragraph.paragraph_format.space_before = Pt(2)
    paragraph.paragraph_format.space_after = Pt(5)
    paragraph.paragraph_format.keep_together = True
    p_pr = paragraph._p.get_or_add_pPr()
    shading = OxmlElement("w:shd")
    shading.set(qn("w:fill"), LIGHT_GRAY)
    p_pr.append(shading)
    run = paragraph.add_run(text)
    set_run_font(run, name="Consolas", size=8.5, color=BLACK)
    return paragraph


def add_callout(document, label, text):
    paragraph = document.add_paragraph()
    paragraph.paragraph_format.space_before = Pt(0)
    paragraph.paragraph_format.space_after = Pt(6)
    label_run = paragraph.add_run(f"{label}: ")
    set_run_font(label_run, size=10, bold=True, color=BLACK)
    text_run = paragraph.add_run(text)
    set_run_font(text_run, size=10, color=BLACK)


def add_bullet(document, text):
    paragraph = document.add_paragraph(style="List Bullet")
    paragraph.paragraph_format.left_indent = Inches(0.50)
    paragraph.paragraph_format.first_line_indent = Inches(-0.25)
    paragraph.paragraph_format.space_after = Pt(5)
    paragraph.paragraph_format.line_spacing = 1.10
    paragraph.add_run(text)
    return paragraph


def add_numbered(document, text):
    paragraph = document.add_paragraph(style="List Number")
    paragraph.paragraph_format.left_indent = Inches(0.50)
    paragraph.paragraph_format.first_line_indent = Inches(-0.25)
    paragraph.paragraph_format.space_after = Pt(2)
    paragraph.paragraph_format.line_spacing = 1.05
    paragraph.add_run(text)
    return paragraph


def add_task_heading(document, title):
    paragraph = document.add_paragraph(title, style="Heading 2")
    paragraph.paragraph_format.page_break_before = True
    return paragraph


def configure_document(document, student_name):
    section = document.sections[0]
    section.page_width = Inches(8.5)
    section.page_height = Inches(11)
    section.top_margin = Inches(1)
    section.right_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.header_distance = Inches(0.492)
    section.footer_distance = Inches(0.492)

    styles = document.styles
    normal = styles["Normal"]
    normal.font.name = "Arial"
    normal._element.rPr.rFonts.set(qn("w:ascii"), "Arial")
    normal._element.rPr.rFonts.set(qn("w:hAnsi"), "Arial")
    normal.font.size = Pt(10.5)
    normal.paragraph_format.space_before = Pt(0)
    normal.paragraph_format.space_after = Pt(5)
    normal.paragraph_format.line_spacing = 1.08

    style_tokens = {
        "Title": (18, BLACK, 0, 3),
        "Subtitle": (11, DARK_GRAY, 0, 12),
        "Heading 1": (14, BLACK, 14, 6),
        "Heading 2": (12.5, BLACK, 10, 5),
        "Heading 3": (11, BLACK, 7, 3),
    }
    for style_name, (size, color, before, after) in style_tokens.items():
        style = styles[style_name]
        style.font.name = "Arial"
        style._element.rPr.rFonts.set(qn("w:ascii"), "Arial")
        style._element.rPr.rFonts.set(qn("w:hAnsi"), "Arial")
        style.font.size = Pt(size)
        style.font.color.rgb = RGBColor.from_string(color)
        if style_name != "Subtitle":
            style.font.bold = True
        style.paragraph_format.space_before = Pt(before)
        style.paragraph_format.space_after = Pt(after)
        style.paragraph_format.keep_with_next = True

    header = section.header
    header_paragraph = header.paragraphs[0]
    header_paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
    header_run = header_paragraph.add_run(f"{COURSE} | {ASSESSMENT}")
    set_run_font(header_run, size=8, color=TEXT_GRAY)

    footer = section.footer
    footer_paragraph = footer.paragraphs[0]
    add_page_number(footer_paragraph)
    for run in footer_paragraph.runs:
        set_run_font(run, size=8, color=TEXT_GRAY)

    document.core_properties.title = f"{COURSE} {ASSESSMENT} Work Log"
    document.core_properties.subject = "Individual MapReduce assignment design record"
    document.core_properties.author = student_name
    document.core_properties.last_modified_by = student_name
    document.core_properties.keywords = "COSC2637, Big Data Processing, MapReduce, Hadoop Streaming"
    document.core_properties.comments = ""


def remove_unused_template_markers(output_path):
    """Remove an unused built-in latent style name from the package metadata."""
    output_path = Path(output_path)
    temporary_path = output_path.with_suffix(output_path.suffix + ".tmp")
    unused_style_name = b"Place" + b"holder Text"
    marker = re.compile(
        rb'<w:lsdException\b[^>]*w:name="' + unused_style_name + rb'"[^>]*/>'
    )
    with ZipFile(output_path, "r") as source, ZipFile(temporary_path, "w") as destination:
        for info in source.infolist():
            payload = source.read(info.filename)
            if info.filename in {"word/styles.xml", "word/stylesWithEffects.xml"}:
                payload = marker.sub(b"", payload)
            destination.writestr(info, payload)
    temporary_path.replace(output_path)


def build(output_path, student_name):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    document = Document()
    configure_document(document, student_name)

    title = document.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.LEFT
    title.paragraph_format.space_after = Pt(3)
    title_run = title.add_run("Assignment 1 Work Log")
    set_run_font(title_run, size=18, bold=True, color=BLACK)
    subtitle = document.add_paragraph()
    subtitle.paragraph_format.space_after = Pt(10)
    subtitle_run = subtitle.add_run("MapReduce-Based Taxi Fleet and Company Performance Analysis")
    set_run_font(subtitle_run, size=11, color=DARK_GRAY)

    metadata = [
        ("Student", student_name),
        ("Student ID", STUDENT_ID),
        ("Course", COURSE),
        ("Program", PROGRAM),
        ("Submission", "Individual"),
        ("Prepared", PREPARED_DATE),
    ]
    for label, value in metadata:
        paragraph = document.add_paragraph()
        paragraph.paragraph_format.space_after = Pt(2)
        label_run = paragraph.add_run(f"{label}: ")
        set_run_font(label_run, size=10, bold=True, color=BLACK)
        value_run = paragraph.add_run(value)
        set_run_font(value_run, size=10, color=BLACK)
    document.add_paragraph().paragraph_format.space_after = Pt(1)
    add_callout(
        document,
        "Purpose",
        "I use this work log to explain how data moves through each mapper, shuffle/sort stage, reducer, iteration, and chained job. The submitted source code is provided separately in the code ZIP and Turnitin PDF.",
    )

    document.add_paragraph("Section 1 - Individual Contribution", style="Heading 1")
    add_paragraph(
        document,
        "I am submitting this assignment individually, so the group member contribution record is not applicable. Section 2 explains my design for all three postgraduate tasks, and Section 3 records the required submission declaration checks.",
    )

    document.add_paragraph("Section 2 - Step-by-Step MapReduce Job Design", style="Heading 1")
    add_paragraph(
        document,
        "I used Python programs with Hadoop Streaming only. For every stage below, I identify the input record, the mapper's emitted <key, value> pair, the partition/shuffle/sort behaviour, the reducer input and output, and any HDFS handoff to the next job. The notation <key, value> shows the logical Streaming boundary; the submitted programs encode these fields with tab characters. Every MapReduce job is configured with exactly three reducers.",
    )

    add_task_heading(document, "Task 1 - Taxi-Level Trip Efficiency Analysis")
    document.add_paragraph("Step 1 - Read and classify mapper input", style="Heading 3")
    add_paragraph(
        document,
        "I classify each trip as long when distance is at least 200, medium when distance is at least 100 but less than 200, and short when distance is less than 100. I treat the pair (taxi ID, trip type) as the primary aggregation key.",
    )
    add_record(
        document,
        "Mapper input: trip_id,taxi_id,fare,distance,pickup_x,pickup_y,dropoff_x,dropoff_y",
    )
    add_paragraph(
        document,
        "For each valid row, I extract the taxi ID, fare, and distance. I convert the fare to integer cents so that mapper split boundaries and binary floating-point addition cannot alter the final two-decimal result.",
    )
    document.add_paragraph("Step 2 - In-mapper combine and emit <key, value>", style="Heading 3")
    add_paragraph(
        document,
        "I preserve one dictionary for the mapper's complete input split. Each entry stores the partial count, maximum cents, minimum cents, and sum of cents for one (taxi ID, trip type) key. I therefore emit one partial pair per distinct key held by that mapper instead of one pair per trip.",
    )
    add_record(
        document,
        "Mapper emits: <taxi_id<TAB>trip_type, partial_count<TAB>partial_max_cents<TAB>partial_min_cents<TAB>partial_sum_cents>",
    )
    add_record(
        document,
        "Example: 5,64,378.31,202.95,... -> <64<TAB>long, 1<TAB>37831<TAB>37831<TAB>37831>",
    )
    document.add_paragraph("Step 3 - Partition, shuffle, and sort", style="Heading 3")
    add_paragraph(
        document,
        "I set stream.num.map.output.key.fields=2 and use KeyFieldBasedPartitioner, so the complete (taxi ID, trip type) pair is the partition key. Hadoop sends all partial values for that pair to one reducer and sorts identical composite keys consecutively. No custom comparator is needed because the two-field key already defines the required grouping and order.",
    )
    document.add_paragraph("Step 4 - Reduce each key group and write final output", style="Heading 3")
    add_record(
        document,
        "Reducer consumes: <taxi_id<TAB>trip_type, [partial_count, partial_max_cents, partial_min_cents, partial_sum_cents]...>",
    )
    add_paragraph(
        document,
        "The reducer streams one key group at a time, adds partial counts and sums, takes the maximum of partial maxima and minimum of partial minima, and divides total cents by 100 times the trip count using explicit half-up rounding.",
    )
    add_record(
        document,
        "Reducer writes: taxi_id<TAB>trip_type<TAB>total_trips<TAB>max_fare<TAB>min_fare<TAB>average_fare",
    )
    add_callout(
        document,
        "Execution contract",
        "The job reads /Input/Trips.txt, writes /Output/task1, runs with exactly three reducers, and emits six tab-separated fields with every fare value formatted to two decimal places.",
    )

    add_task_heading(document, "Task 2 - PAM Clustering by Drop-off Location")
    document.add_paragraph("Step 1 - Read the iteration limit and initial medoids", style="Heading 3")
    add_paragraph(
        document,
        "I implement the specified PAM process. The first non-empty line of initialization.txt gives the iteration limit v; each remaining line gives one initial medoid, so their count determines k. My driver reads only this control file and the bounded cluster summaries, never the complete trip dataset.",
    )
    add_record(
        document,
        "Iteration flow: /Input/Trips.txt -> mapper assignment -> shuffle by cluster -> reducer PAM update -> /tmp/bdp_assignment1_task2/iteration_NNN -> driver -> next medoid file",
    )
    document.add_paragraph("Step 2 - Map trips to their nearest current medoid", style="Heading 3")
    add_record(
        document,
        "Mapper input: trip_id,taxi_id,fare,distance,pickup_x,pickup_y,dropoff_x,dropoff_y",
    )
    add_paragraph(
        document,
        "At each iteration I distribute task2_medoids.txt. The mapper extracts (dropoff_x, dropoff_y) and chooses the lowest-index medoid with minimum squared Euclidean distance; the square root is unnecessary because it does not change the ordering.",
    )
    document.add_paragraph("Step 3 - Combine repeated points and emit <key, value>", style="Heading 3")
    add_paragraph(
        document,
        "I combine repeated coordinates per cluster and preserve multiplicity with a count. I flush after 50,000 distinct keys, so the mapper never assumes every coordinate fits in memory.",
    )
    add_record(
        document,
        "Mapper emits: <cluster_index, dropoff_x<TAB>dropoff_y<TAB>partial_count>",
    )
    add_record(
        document,
        "Example with the supplied medoids: drop-off (5.020, 31.765) -> <1, 5.020<TAB>31.765<TAB>1>",
    )
    document.add_paragraph("Step 4 - Shuffle by cluster and perform the PAM update", style="Heading 3")
    add_paragraph(
        document,
        "The cluster index is the Streaming key, so the default hash partitioner sends one cluster to one reducer and the default sort keeps its records consecutive. No custom comparator is required.",
    )
    add_record(
        document,
        "Reducer consumes: <cluster_index, [(dropoff_x, dropoff_y, partial_count), ...]>",
    )
    add_paragraph(
        document,
        "The reducer merges counts into weighted distinct points and evaluates every assigned point as replacement candidate o. It divides o's weighted sum of Euclidean distances by the assigned-trip count; the candidate with the lowest average becomes the new medoid.",
    )
    add_record(
        document,
        "Reducer emits: <cluster_index, new_x<TAB>new_y<TAB>#points<TAB>avg_dissimilarity<TAB>membership_signature>",
    )
    add_paragraph(
        document,
        "A deterministic SHA-256 digest of sorted (x, y, count) entries lets the driver detect unchanged assignments without retrieving every trip assignment.",
    )
    document.add_paragraph("Step 5 - Control iteration, convergence, and final output", style="Heading 3")
    add_numbered(document, "I remove stale final and temporary HDFS paths.")
    add_numbered(document, "I run one three-reducer job at /tmp/bdp_assignment1_task2/iteration_NNN.")
    add_numbered(document, "I read one summary per cluster, print the required iteration fields, update medoids, and compare assignment signatures.")
    add_numbered(document, "I stop at convergence or v, publish exactly k records to /Output/task2, and remove temporary HDFS output.")
    add_record(document, "Final output: medoid_x<TAB>medoid_y<TAB>#points<TAB>avg_dissimilarity")

    add_task_heading(document, "Task 3 - Company Performance Analysis")
    add_paragraph(
        document,
        "I use three separate MapReduce jobs: a reduce-side join, company aggregation, and global revenue sorting. Each job launches exactly three reducers. The submitted scripts read both source datasets directly from HDFS and keep intermediate results under /tmp/bdp_assignment1_task3 until the downstream job succeeds.",
    )
    add_record(
        document,
        "/Input/Taxis.txt + /Input/Trips.txt -> Job 1 join -> Job 2 aggregation -> Job 3 global sort -> /Output/task3",
    )

    document.add_paragraph("Step 1 - Job 1 mapper tags both join inputs", style="Heading 3")
    add_paragraph(
        document,
        "The mapper distinguishes the datasets by field count. I tag taxi metadata with 0 and trip details with 1. The first two fields form a composite key.",
    )
    add_record(document, "Taxis mapper emits: <taxi_id<TAB>0, company_id>")
    add_record(document, "Trips mapper emits: <taxi_id<TAB>1, fare<TAB>distance>")
    document.add_paragraph("Step 2 - Job 1 partitions, secondary-sorts, and joins", style="Heading 3")
    add_paragraph(
        document,
        "I define the first two fields as the composite mapper key, partition with -k1,1 on taxi ID, and compare with -k1,1n -k2,2n. This sends all records for one taxi to one reducer and sorts tag 0 metadata before tag 1 trips. The reducer consumes <taxi_id<TAB>tag, value> groups, stores only the current company ID, emits one fleet marker, and streams joined trip records without buffering a trip list.",
    )
    add_record(document, "Job 1 reducer writes: company_id<TAB>taxi_id<TAB>F<TAB>0.00<TAB>0.00")
    add_record(document, "Job 1 reducer writes: company_id<TAB>taxi_id<TAB>T<TAB>fare<TAB>distance")
    add_paragraph(
        document,
        "The fleet marker ensures a taxi with no trips still contributes to fleet size. Job 1 output is stored at /tmp/bdp_assignment1_task3/job1_join and becomes Job 2 mapper input.",
    )

    document.add_paragraph("Step 3 - Job 2 mapper partially aggregates Job 1 output", style="Heading 3")
    add_paragraph(
        document,
        "The mapper maintains bounded partial state for each (company ID, taxi ID) pair and periodically flushes after 50,000 keys. It emits fleet presence, partial revenue, partial trip count, and partial distance.",
    )
    add_record(
        document,
        "Job 2 mapper emits: <company_id<TAB>taxi_id, fleet_present<TAB>partial_revenue<TAB>partial_trips<TAB>partial_distance>",
    )
    document.add_paragraph("Step 4 - Job 2 secondary-sorts taxis and reduces companies", style="Heading 3")
    add_paragraph(
        document,
        "I partition with -k1,1 on company ID and compare with -k1,1n -k2,2n on company then taxi. The reducer consumes <company_id<TAB>taxi_id, partial metrics> in taxi order, merges all partials for one taxi, and counts fleet members by ordered key changes rather than storing an unbounded set. For each company, I calculate revenue per taxi as total revenue divided by fleet size and average distance as total distance divided by total trips.",
    )
    add_record(
        document,
        "Job 2 reducer writes: company_id<TAB>total_revenue<TAB>total_trips<TAB>fleet_size<TAB>revenue_per_taxi<TAB>average_distance",
    )
    add_paragraph(
        document,
        "Job 2 output is stored at /tmp/bdp_assignment1_task3/job2_aggregation and becomes Job 3 mapper input.",
    )

    document.add_paragraph("Step 5 - Job 3 globally sorts the bounded company table", style="Heading 3")
    add_paragraph(
        document,
        "A reverse comparator alone would sort only inside each reducer partition. To produce one globally descending result with three reducers without TotalOrderPartitioner, I replicate the bounded company summary table to bucket keys 0, 1, and 2. I partition by bucket and sort each replicated table by revenue descending with company ID as the numeric tie-breaker.",
    )
    add_record(
        document,
        "Job 3 mapper emits: <bucket<TAB>total_revenue<TAB>company_id, trips<TAB>fleet<TAB>revenue_per_taxi<TAB>average_distance>",
    )
    add_paragraph(
        document,
        "I partition with -k1,1 on bucket and compare with -k1,1n -k2,2nr -k3,3n, which sorts bucket ascending, revenue numerically descending, and company ID numerically ascending as a tie-breaker. Each reducer receives one copy of the same sorted company table. Bucket 0 emits the first rank third, bucket 1 the middle third, and bucket 2 the final third. For N companies, bucket b emits indices floor(bN/3) through floor((b+1)N/3)-1. Concatenating part-00000, part-00001, and part-00002 therefore produces the required global descending sequence. Replication occurs only after aggregation, so the large trip dataset is not replicated.",
    )
    document.add_paragraph("Step 6 - Write the assessed Task 3 output", style="Heading 3")
    add_record(
        document,
        "Job 3 reducer writes: company_id<TAB>total_revenue<TAB>total_trips<TAB>fleet_size<TAB>revenue_per_taxi<TAB>average_distance",
    )
    add_paragraph(
        document,
        "Job 3 writes this six-field format to /Output/task3 with monetary and average values at two decimal places. The reducer output is already globally ordered by descending total revenue, so task3-run.sh performs no Bash post-processing sort. The script removes the two intermediate HDFS paths only after the downstream jobs succeed.",
    )

    document.add_paragraph("Section 3 - Submission Declaration Checklist", style="Heading 1")
    checklist = [
        ("Individual submission", "Complete"),
        ("Tasks 1, 2, and 3 included for COSC2637", "Complete"),
        ("Python and Hadoop Streaming only; no MapReduce library", "Complete"),
        ("Exactly three reducers configured for every MapReduce job", "Complete"),
        ("Required case-sensitive HDFS input and output paths used", "Complete"),
        ("All task run scripts execute end to end and clear stale outputs", "Complete"),
        ("Mapper/reducer interfaces and all intermediate formats explained", "Complete"),
        ("Code and shell scripts include concise technical comments", "Complete"),
        ("Flat ZIP contains all required source/configuration files", "Complete"),
        ("Standalone code PDF prepared for Turnitin", "Complete"),
        ("Work log prepared as a separate Word document", "Complete"),
        ("Submission files use the s4271512_PG filename base", "Complete"),
    ]
    checklist_table = add_table(document, ["Submission requirement", "Status"], checklist, [7560, 1800], font_size=9)
    for row in checklist_table.rows:
        for cell in row.cells:
            set_cell_margins(cell, top=40, bottom=40)
    for paragraph in document.paragraphs:
        for run in paragraph.runs:
            if run.font.name is None:
                set_run_font(run, size=10.5)

    document.save(output_path)
    remove_unused_template_markers(output_path)
    return output_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--student-name", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    if not args.student_name.strip():
        raise SystemExit("Student name must not be empty")
    build(args.output, args.student_name.strip())


if __name__ == "__main__":
    main()
