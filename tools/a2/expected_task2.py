#!/usr/bin/env python3
"""Independent CPython reference for A2 Task 2 (not part of the submission).

Recomputes the expected /Output/task2 text directly from the CSV inputs so the
EMR output can be compared byte for byte. It deliberately does not import the
submitted UDF.

Usage: python expected_task2.py DATA_DIR [START_YEAR END_YEAR] > expected.txt
"""

import csv
import sys
from pathlib import Path


def read_rows(path):
    with open(path, newline="", encoding="utf-8") as handle:
        return [[field.strip() for field in row] for row in csv.reader(handle) if row]


def as_int(text):
    try:
        return int(text)
    except ValueError:
        return None


def ranking(rows, measure):
    ordered = sorted(rows, key=lambda row: (-row[measure], row["code"]))[:3]
    return " | ".join(
        f"{rank}. {row['name']} ({row[measure]})" for rank, row in enumerate(ordered, 1)
    )


def expected_report(data_dir, start_year=0, end_year=9999):
    data_dir = Path(data_dir)
    names = {row[0]: row[1] for row in read_rows(data_dir / "countries.csv")}
    cities = {}
    for year, city, _host in read_rows(data_dir / "games.csv"):
        year = as_int(year)
        if year is not None and start_year <= year <= end_year:
            cities[year] = city

    by_year = {}
    for year, code, gold, silver, bronze in read_rows(data_dir / "medal_table.csv"):
        year = as_int(year)
        if year is None or not start_year <= year <= end_year or code not in names:
            continue
        gold, silver, bronze = int(gold), int(silver), int(bronze)
        by_year.setdefault(year, []).append(
            {"code": code, "name": names[code], "gold": gold, "total": gold + silver + bronze}
        )

    blocks = []
    for year in sorted(set(by_year) & set(cities)):
        rows = by_year[year]
        blocks.append(
            f"{year} {cities[year]}\n"
            f"By Gold Medals:\n{ranking(rows, 'gold')}\n"
            f"By Total Medals:\n{ranking(rows, 'total')}\n\n"
        )
    return "".join(blocks)


if __name__ == "__main__":
    args = sys.argv[1:]
    bounds = (int(args[1]), int(args[2])) if len(args) == 3 else (0, 9999)
    sys.stdout.buffer.write(expected_report(args[0], *bounds).encode("utf-8"))
