# Repository map

## Project guidance

- `AGENTS.md` is the authoritative workspace guidance, including the learning-paper maintenance rules.
- `CLAUDE.md` points agents to that guidance.
- `.agent-harness/state.json` stores the latest verified handoff observations and harness routing preferences.

## Coursework

- `Assignment 1/` contains the earlier assignment brief, source data, tasks, explanations, and submission evidence.
- `Assignment 2/` contains the Canvas brief, detailed `2026A2.pdf` specification, `Data/`, `References/`, `Templates/`, and a working-set README.
- `Assignment 3/` contains the Spark Streaming brief `2026A3.pdf` (6 Oct 2026 revision with updated Appendix A), the two sample query logs in `Data/`, the work-log template, and `a3-project/` (the single source `src/main/scala/streaming/a3.scala` plus a `pom.xml`); due 25 Oct 2026 23:59.
- `output/A3/` holds the A3 upload set in `submission/` (`s4271512_PG.zip`, `.pdf`, `.doc`), the built `build/a3.jar`, and EMR test evidence in `verification/`. Rebuild with `tools/a3/build_a3_submission.py` and `tools/a3/build_a3_work_log.py` (then convert the DOCX to Word 97 `.doc` with the portable LibreOffice in `tmp/`).
- `Week 1/` through `Week 6/` contain earlier lecture and lab materials.
- `Week 7/` contains Pig/Hive lecture and tutorial material with the tutorial's sample datasets.
- `Week 8/` contains Mahout, Solr, and Storm lecture material plus the Mahout Java example, input data, and job JAR.
- `Week 9/` contains Spark Basics, the first Spark/IntelliJ lab, Scala exercises, and the Three Little Pigs sample.
- `Week 10/` contains the Spark Streaming/socket lab, its code examples, and the accumulator sample input.
- `Summary and Learning Sheet/Big Data Processing - Learning Summary and Cheat Sheet.md` is the canonical course learning paper.
- `Summary and Learning Sheet/Lernplan - A3 und A4.md` is the user-requested study plan for A3 (due 25 Oct) and the A4 timed assessment (2 Nov 2026).
- `Reference/` contains general reference books.
- `Environment Setup/` contains the existing environment setup material.

## Working files

- `tools/`, `output/`, and `tmp/` contain the existing assignment build tools, generated outputs, and working artifacts.
