# Assignment 2 working set

## Core files

- Canvas assignment overview: `Advanced Winter Olympic Medal Analysis Using Pig Latin.pdf`
- Detailed specification: `2026A2.pdf`
- Four required input datasets: `Data/`
- Group work-log template: `Templates/A2_GroupLeaderStudentID_GroupNumber_UGorPG_worklog.docx`
- Supporting Pig references: `References/`

## Course-week mapping

The assignment is Pig Latin and Jython UDF work on the RMIT EMR/HDFS environment. Week 7's Pig/Hive lecture and tutorial are the relevant course materials. Week 9 Spark Basics and the Week 10 Spark Streaming/socket lab are separate topics and are not A2 prerequisites. The Week 10 handout labels broadcast and accumulator as selective material that is not necessary for the course.

For COSC2637/Postgraduate, `2026A2.pdf` assigns Task 2. It names `task2.pig` and `task2.py`, requires `START_YEAR` and `END_YEAR` parameters, and specifies `/Output/task2`. Follow the detailed PDF for exact field names, ranking logic, paths, and submission packaging.

## Input inventory

| File | Data rows | Fields | Check |
|---|---:|---:|---|
| `countries.csv` | 11 | 3 | Country codes used by the game and population tables are represented. |
| `games.csv` | 6 | 3 | Host-country codes resolve in `countries.csv`. |
| `medal_table.csv` | 65 | 5 | 11 country records for 2006-2022 and 10 for 2026; the specification says RUS is omitted in 2026. |
| `population.csv` | 66 | 3 | 11 country records for each of the six game years. |

The four required input filenames are present. Field counts are consistent, there are no blank records, and the country/year references were checked across files. Week 7's taxi, `visits`, and `urlInfo` samples are tutorial data, not A2 inputs.

## Remaining course-material notes

- The Week 7 tutorial says companion examples `join_task1.pig` and `join_task2.pig` are supplied next to the lab materials. No `.pig` source files are currently in the repository. These are useful practice examples, not required A2 files; the handout itself shows the Pig workflow.
- The Canvas overview links Pig UDF documentation version 0.17.0; `2026A2.pdf` refers to version 0.18.0. The downloaded local UDF guide is 0.17.0. Check the target EMR/Pig version if a version-specific syntax issue comes up.
- The specification cover labels 27 September 2026 as Friday, although that date is Sunday. Verify the authoritative deadline in Canvas.
