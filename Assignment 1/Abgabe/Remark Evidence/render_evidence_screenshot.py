from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "task2-remark-evidence.txt"
OUTPUT = HERE / "Task2_EMR_Remark_Evidence.png"

text = SOURCE.read_text(encoding="utf-8").replace("\t", "    ")
lines = text.rstrip().splitlines()

font_path = Path("C:/Windows/Fonts/consola.ttf")
bold_path = Path("C:/Windows/Fonts/consolab.ttf")
body_font = ImageFont.truetype(str(font_path), 25)
title_font = ImageFont.truetype(str(bold_path), 27)
small_font = ImageFont.truetype(str(font_path), 19)

probe = Image.new("RGB", (10, 10))
probe_draw = ImageDraw.Draw(probe)
line_height = 36
text_width = max(probe_draw.textlength(line, font=body_font) for line in lines)

padding_x = 48
title_height = 76
footer_height = 56
width = int(max(1500, text_width + padding_x * 2))
height = title_height + 32 + len(lines) * line_height + footer_height

image = Image.new("RGB", (width, height), "#0d1117")
draw = ImageDraw.Draw(image)

draw.rectangle((0, 0, width, title_height), fill="#161b22")
for index, colour in enumerate(("#ff5f57", "#febc2e", "#28c840")):
    x = 32 + index * 32
    draw.ellipse((x, 25, x + 16, 41), fill=colour)
draw.text(
    (width // 2, 21),
    "Captured EMR terminal transcript",
    font=title_font,
    fill="#f0f6fc",
    anchor="ma",
)

y = title_height + 24
for line in lines:
    colour = "#c9d1d9"
    if line.startswith("A1 TASK 2"):
        colour = "#58a6ff"
    elif line.startswith("Assignments unchanged") or line.startswith("task2-run.sh exit status: 0"):
        colour = "#3fb950"
    elif line.startswith("$ "):
        colour = "#d2a8ff"
    elif line.startswith("[no differences"):
        colour = "#3fb950"
    draw.text((padding_x, y), line, font=body_font, fill=colour)
    y += line_height

draw.line((padding_x, height - footer_height, width - padding_x, height - footer_height), fill="#30363d", width=1)
draw.text(
    (padding_x, height - 40),
    "Rendered directly from task2-remark-evidence.txt; full raw YARN log retained separately.",
    font=small_font,
    fill="#8b949e",
)

image.save(OUTPUT, format="PNG", optimize=True)
print(OUTPUT)
