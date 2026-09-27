# Assignment 1 Project Notes

**Student:** Samuel Klefe  
**Student ID:** s4271512  
**Course:** COSC2637 Big Data Processing  
**Program:** Postgraduate  
**Submission type:** Individual  
**Status:** Conditionally ready - one Task 3 rounding decision remains  
**Last reviewed:** 29 August 2026

This file is my concise project reference. It is not part of the three assessed uploads.

## Submission set

| File | Assessed content |
|---|---|
| `s4271512_PG.zip` | Flat folder containing the required Python programs, Bash scripts, and `initialization.txt` |
| `s4271512_PG.pdf` | Python and Bash source from Tasks 1, 2, and 3 for the plagiarism check |
| `s4271512_PG.doc` | Individual work log containing the three required sections |

Section 2 of the DOC is titled **Step-by-Step MapReduce Job Design**. For every submitted task, I identify mapper input, emitted `<key, value>` pairs, partition/shuffle/sort behaviour, reducer input and output, and the exact HDFS path and record format used between chained jobs. The explanation contains no Python code.

Section 3 remains in the submitted work log. The specification tells me to complete all three work-log sections and to use the Submission Declaration Checklist before submitting. This checklist is therefore assessed submission structure, unlike private cluster-status or verification notes, which stay outside the work log.

I preserved the previous PDF and DOC unchanged in `output/design-backup/original-design`. I also prepared a separate restrained, black-and-white alternative in `output/design-candidates/minimalist`. The alternative uses Arial, ordinary heading hierarchy, light-grey code examples, and a plain checklist table; it does not change the assessed content. I rendered and reviewed all 25 pages of the code PDF and all five pages of the work log, then converted the work log back from DOC to PDF to verify the actual legacy Word file. The round-trip content matches the master after page-number normalisation.

I have not mixed either design set into the assessed folder while the choice is pending. `output/submission` therefore remains the current three-file upload set. Once I choose a design, only the selected PDF and DOC should replace their matching files there; the ZIP remains unchanged.

## Task 1 - Taxi-level trip efficiency

I classify trips as short, medium, or long and aggregate by `(taxi_id, trip_type)`. The mapper preserves state across its input split and emits one partial count, maximum, minimum, and sum per key. I store fares as integer cents so the reducer can calculate deterministic two-decimal results without floating-point accumulation changing the final cent.

The reducer merges mapper partials and writes:

```text
taxi_id<TAB>trip_type<TAB>total_trips<TAB>max_fare<TAB>min_fare<TAB>average_fare
```

The job reads `/Input/Trips.txt`, writes `/Output/task1`, and uses exactly three reducers.

## Task 2 - PAM clustering

I read the maximum iteration count and initial medoids from `initialization.txt`. During each iteration, the mapper assigns each drop-off point to its nearest current medoid and combines repeated coordinates with occurrence counts. The reducer performs the specified weighted medoid swap evaluation for each cluster and emits a deterministic membership signature for convergence checking.

The driver repeats the three-reducer job until assignments stop changing or the iteration limit is reached. It publishes the final cluster summaries to `/Output/task2` in this format:

```text
medoid_x<TAB>medoid_y<TAB>#points<TAB>avg_dissimilarity
```

## Task 3 - Company performance

I use three MapReduce jobs, each with exactly three reducers:

1. Job 1 performs a metadata-first secondary-sort join between taxis and trips.
2. Job 2 aggregates revenue, trips, distinct fleet size, revenue per taxi, and average distance by company.
3. Job 3 sorts the bounded company summary by descending revenue and assigns contiguous rank thirds to the three output parts without using `TotalOrderPartitioner` or a Bash post-processing sort.

The final output at `/Output/task3` uses this format:

```text
company_id<TAB>total_revenue<TAB>total_trips<TAB>fleet_size<TAB>revenue_per_taxi<TAB>average_distance
```

An independent exact-decimal recomputation matched all Task 3 rows, ordering, totals, fleet sizes, trip counts, revenues, and average distances except for one rounding tie. For company 0, `356194.37 / 34 = 10476.305`; the verified EMR run emitted `10476.30`, while explicit half-up rounding gives `10476.31`. The specification requires two decimal places but does not define a tie-breaking rule. The current value is therefore defensible under half-even-style formatting, but float accumulation can make this final cent depend on mapper/reducer summation order. Converting Task 3 revenue partials to integer cents and applying one documented `Decimal` rule in the reducer would remove that nondeterminism, but it requires rebuilding and re-verifying all three assessed artifacts.

## Course-based implementation review

I use a custom partitioner only where the grouping requirement depends on selected fields of a composite key. Task 1 partitions on the complete `(taxi_id, trip_type)` key. Task 3 partitions on the primary grouping field and uses Hadoop's key comparator for secondary ordering. Task 2 uses the default hash partitioner because the cluster index is already the complete grouping key; a custom partitioner would not improve its distribution or correctness.

I rely on Hadoop shuffle and sort rather than sorting assessed output in a shell command. The only Python `sorted()` calls are inside the Task 2 reducer to evaluate the distinct weighted points of one cluster in deterministic order. They do not replace distributed sorting. Task 3's final ordering is encoded in the mapper key and comparator configuration.

I keep only purpose-specific state. Task 1 holds split-local in-mapper aggregates. Task 2 mappers flush partial aggregates after 50,000 distinct keys, and the driver reads only the three cluster summaries. The exact PAM reducer must retain the weighted distinct points belonging to its current cluster to evaluate candidate medoid swaps. Task 3 streams the join with one metadata value, flushes mapper aggregates after 50,000 keys, counts distinct taxis from secondary-sort key changes, and buffers only the bounded company summary after the raw trips have already been aggregated.

For Task 2, I pass the changing medoid model as the auxiliary file `task2_medoids.txt` with Hadoop Streaming's `-file` option. Command-line parameters are suitable for a few scalar settings, but the structured medoid list is iteration-dependent data and belongs in a distributed auxiliary file. The driver reads `initialization.txt`, creates the localised medoid file for each iteration, and uses three reducers for every iteration.

I do not add a separate combiner merely to include one. Task 1 uses the required in-mapper combining pattern, while Task 2 and Task 3 Job 2 use bounded, periodically flushed mapper-side partial aggregation. Their reducers merge those partials. This reduces shuffle traffic without relying on Hadoop to invoke an optional combiner.

## Marking-guide audit

I verified the current implementation against the top-band conditions in the specification. Task 1 produced all `1,436` exact groups and represents all `30,000` trips. Task 2 converged on EMR, its three clusters represent all `30,000` trips, and an independent weighted PAM calculation confirmed every final medoid, count, and average dissimilarity. Task 3 ran all three chained jobs successfully on EMR, represents all `500` taxis and `30,000` trips, and produces a globally descending 19-company result. The Python files use only the standard library, all submitted jobs request three reducers, the Bash scripts pass syntax checking, and comments explain the logical flow.

The submission package contains the separately named DOC, PDF, and flat ZIP required for an individual postgraduate submission. The ZIP has no subfolders and every archived source file is byte-identical to the reviewed source. The DOC contains all three work-log sections, including the numbered Section 2 data-flow explanation, and has no comments or tracked changes. The Turnitin PDF contains the complete Python and Bash source for all three tasks.

## Submission boundary

Only the ZIP, PDF, and DOC in `output/submission` are submitted. The assignment data, explanation files, this project note, and the editable DOCX master are not included.

## Final upload-folder audit

I completed the final read-only audit of `output/submission` on 29 August 2026. It contains exactly three files with the required individual postgraduate names: `s4271512_PG.zip`, `s4271512_PG.pdf`, and `s4271512_PG.doc`. The DOC and PDF are genuine files of their stated formats, not renamed alternatives.

The ZIP contains 15 top-level entries and no directories, raw datasets, caches, or explanation files. Every archived file is byte-identical to the reviewed task source. All Python files compile, all three Bash scripts pass `bash -n`, use Linux LF line endings, and begin with `#!/bin/bash`.

The submitted code PDF has 25 readable pages. Its file index matches the current source line counts, and all 770 non-empty source lines from the 14 Python/Bash files are present. The submitted DOC renders as five complete pages, contains Sections 1, 2, and 3 and all three task designs, and has no comments, tracked revisions, or populated author/company/comment fields. The visible text contains no placeholders or internal operational notes.

The PDF and DOC currently in `output/submission` are the preserved original blue design. The separately verified minimalist design remains in `output/design-candidates/minimalist`; it has not replaced the upload files. Both designs contain the same assessed explanation, apart from layout-level line wrapping and the simplified identity block.

The package is ready in the required hand-in form. The only known assessment-level uncertainty remains the previously documented Task 3 half-cent rounding tie; the specification and available FAQ do not define the tie-breaking rule, and I have not changed the verified implementation.
