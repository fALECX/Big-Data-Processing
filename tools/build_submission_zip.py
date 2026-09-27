#!/usr/bin/env python3
"""Build the flat Assignment 1 source archive with stable file permissions."""

from __future__ import annotations

import argparse
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


SUBMISSION_FILES = (
    ("Task 1/task1_mapper.py", "task1_mapper.py"),
    ("Task 1/task1_reducer.py", "task1_reducer.py"),
    ("Task 1/task1-run.sh", "task1-run.sh"),
    ("Task 2/task2_mapper.py", "task2_mapper.py"),
    ("Task 2/task2_reducer.py", "task2_reducer.py"),
    ("Task 2/task2_driver.py", "task2_driver.py"),
    ("Task 2/task2-run.sh", "task2-run.sh"),
    ("Task 2/initialization.txt", "initialization.txt"),
    ("Task 3/task3_job1_mapper.py", "task3_job1_mapper.py"),
    ("Task 3/task3_job1_reducer.py", "task3_job1_reducer.py"),
    ("Task 3/task3_job2_mapper.py", "task3_job2_mapper.py"),
    ("Task 3/task3_job2_reducer.py", "task3_job2_reducer.py"),
    ("Task 3/task3_job3_mapper.py", "task3_job3_mapper.py"),
    ("Task 3/task3_job3_reducer.py", "task3_job3_reducer.py"),
    ("Task 3/task3-run.sh", "task3-run.sh"),
)


def build_archive(assignment_dir: Path, output_path: Path) -> None:
    missing = [source for source, _ in SUBMISSION_FILES if not (assignment_dir / source).is_file()]
    if missing:
        raise FileNotFoundError("Missing submission files: " + ", ".join(missing))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output_path, "w", ZIP_DEFLATED, compresslevel=9) as archive:
        for source_name, archive_name in SUBMISSION_FILES:
            source_path = assignment_dir / source_name
            data = source_path.read_bytes()
            info = ZipInfo(archive_name, date_time=(2026, 8, 23, 0, 0, 0))
            info.create_system = 3
            mode = 0o100755 if source_path.suffix in {".py", ".sh"} else 0o100644
            info.external_attr = mode << 16
            info.compress_type = ZIP_DEFLATED
            archive.writestr(info, data)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the Assignment 1 submission ZIP.")
    parser.add_argument("--assignment-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    build_archive(args.assignment_dir.resolve(), args.output.resolve())


if __name__ == "__main__":
    main()
