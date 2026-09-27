#!/usr/bin/env python3
"""CPython checks for the A2 Task 2 Jython UDF (not part of the submission).

Pig injects the outputSchema decorator into Jython UDF modules; this harness
provides a stand-in, simulates the Pig data flow of task2.pig, and compares the
result with the independent reference in expected_task2.py.
"""

import builtins
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "Assignment 2" / "Data"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from expected_task2 import expected_report, read_rows  # noqa: E402

builtins.outputSchema = lambda schema: (lambda func: func)
spec = importlib.util.spec_from_file_location("task2", ROOT / "Assignment 2" / "Task 2" / "task2.py")
task2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(task2)


def pig_simulation(start, end):
    names = {r[0]: r[1] for r in read_rows(DATA / "countries.csv")}
    cities = {int(r[0]): r[1] for r in read_rows(DATA / "games.csv") if start <= int(r[0]) <= end}
    groups = {}
    for y, code, g, s, b in read_rows(DATA / "medal_table.csv"):
        y = int(y)
        if start <= y <= end and code in names:
            groups.setdefault(y, []).append((code, names[code], int(g), int(g) + int(s) + int(b)))
    out = []
    for y in sorted(set(groups) & set(cities)):
        rows = groups[y]
        # Pig bags are unordered: pass the top-3 bags in reverse order on purpose.
        gold = sorted(rows, key=lambda r: (-r[2], r[0]))[:3]
        total = sorted(rows, key=lambda r: (-r[3], r[0]))[:3]
        out.append(task2.format_games_report(y, cities[y],
                                             [(c, n, g) for c, n, g, _ in reversed(gold)],
                                             [(c, n, t) for c, n, _, t in reversed(total)]) + "\n")
    return "".join(out)


def main():
    for start, end in [(0, 9999), (2010, 2020), (2026, 2026), (2011, 2013), (2006, 2006), (2018, 2022)]:
        assert pig_simulation(start, end) == expected_report(DATA, start, end), (start, end)

    # Spec examples (country names taken from countries.csv).
    assert expected_report(DATA, 2026, 2026) == (
        "2026 Milan-Cortina\nBy Gold Medals:\n"
        "1. Norway (18) | 2. United States (12) | 3. Italy (10)\n"
        "By Total Medals:\n1. Norway (41) | 2. United States (33) | 3. Italy (30)\n\n")
    spec_2010_2020 = (
        "2010 Vancouver\nBy Gold Medals:\n1. Canada (14) | 2. Germany (10) | 3. Norway (9)\n"
        "By Total Medals:\n1. United States (37) | 2. Germany (30) | 3. Canada (26)\n\n"
        "2014 Sochi\nBy Gold Medals:\n1. Russia (13) | 2. Norway (11) | 3. Canada (10)\n"
        "By Total Medals:\n1. Russia (33) | 2. United States (28) | 3. Norway (26)\n\n"
        "2018 PyeongChang\nBy Gold Medals:\n1. Germany (14) | 2. Norway (14) | 3. Canada (11)\n"
        "By Total Medals:\n1. Norway (39) | 2. Germany (31) | 3. Canada (29)\n\n")
    assert expected_report(DATA, 2010, 2020).replace("Russia / ROC / OAR", "Russia") == spec_2010_2020

    # Ties are broken by country code, fewer than three countries are allowed.
    line = task2._ranked_line([("SWE", "Sweden", 5), ("SUI", "Switzerland", 5)])
    assert line == "1. Switzerland (5) | 2. Sweden (5)", line
    assert task2._ranked_line([("NOR", "Norway", 1)]) == "1. Norway (1)"
    print("all UDF checks passed")


if __name__ == "__main__":
    main()
