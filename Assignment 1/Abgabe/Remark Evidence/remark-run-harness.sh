#!/bin/bash

# Reproducibility harness for the A1 Task 2 remark evidence.
# This file is not part of the submitted ZIP. It runs the extracted submission
# unchanged and records source hashes, released-input hashes, convergence, and
# the final HDFS output.

BASE="$HOME/a1-remark-20260918"
SUBMISSION="$BASE/submission"
INPUTS="$BASE/grading-inputs"
FULL_LOG="$BASE/task2-full-run.log"
EVIDENCE="$BASE/task2-remark-evidence.txt"
FINAL_SORTED="$BASE/task2-output-sorted.txt"

cd "$SUBMISSION" || exit 1

sha256sum ./*.py ./*.sh | sort > "$BASE/source-hashes-before.txt"
cp "$INPUTS/initialization.txt" ./initialization.txt

hadoop fs -mkdir -p /Input
hadoop fs -put -f "$INPUTS/Trips_task2.txt" /Input/Trips.txt

rm -f "$FULL_LOG" "$FINAL_SORTED"
bash ./task2-run.sh 2>&1 | tee "$FULL_LOG"
run_status=${PIPESTATUS[0]}

sha256sum ./*.py ./*.sh | sort > "$BASE/source-hashes-after.txt"

if [ "$run_status" -eq 0 ]; then
    hadoop fs -cat '/Output/task2/part*' | sort > "$FINAL_SORTED"
fi

{
    echo "A1 TASK 2 REMARK EVIDENCE — UNCHANGED CANVAS SUBMISSION ON AWS EMR"
    echo "Captured UTC: $(date -u '+%Y-%m-%d %H:%M:%S')"
    echo "EMR host: $(hostname)"
    hadoop version 2>/dev/null | head -n 1
    echo
    echo '$ sha256sum s4271512_PG-1.zip'
    sha256sum "$BASE/s4271512_PG-1.zip"
    echo
    echo '$ sha256sum released grading inputs'
    sha256sum "$INPUTS/initialization.txt" "$INPUTS/Trips_task2.txt"
    echo "Trips_task2.txt HDFS record count: $(hadoop fs -cat /Input/Trips.txt | wc -l)"
    echo
    echo '$ bash ./task2-run.sh'
    grep -E '^Iteration [0-9]+$|^Assignments unchanged; converged|^Final output written' "$FULL_LOG" || true
    echo "task2-run.sh exit status: $run_status"
    echo
    echo "$ hadoop fs -cat '/Output/task2/part*' | sort"
    if [ -f "$FINAL_SORTED" ]; then
        cat "$FINAL_SORTED"
    else
        echo '[no final output because the submitted program exited unsuccessfully]'
    fi
    echo
    echo '$ diff -u source-hashes-before.txt source-hashes-after.txt'
    if diff -u "$BASE/source-hashes-before.txt" "$BASE/source-hashes-after.txt"; then
        echo '[no differences — all submitted .py and .sh files remained unchanged]'
    fi
} | tee "$EVIDENCE"

exit "$run_status"
