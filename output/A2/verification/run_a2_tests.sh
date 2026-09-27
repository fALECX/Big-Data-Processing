#!/bin/bash
# Private A2 Task 2 verification harness for the EMR master (not submitted).
# Layout in ~/a2: s4271512_PG.zip, data/*.csv (Canvas copies, CRLF), expected/*.txt
# Runs the unchanged submitted task2.pig from the extracted ZIP and compares
# every HDFS result byte for byte with the independent CPython reference.

BASE="$HOME/a2"
SUB="$BASE/submission"
EXP="$BASE/expected"
LOG="$BASE/logs"
RESULTS="$BASE/results.txt"

rm -rf "$SUB" "$LOG" && mkdir -p "$SUB" "$LOG"
cd "$SUB" || exit 1
unzip -q "$BASE/s4271512_PG.zip" || exit 1
sha256sum "$BASE/s4271512_PG.zip" task2.pig task2.py > "$BASE/hashes-before.txt"

put_inputs() {  # $1 = local directory holding the four CSV files
    for f in countries games medal_table population; do
        hadoop fs -put -f "$1/$f.csv" "/$f.csv" || exit 1
    done
}

check() {  # $1 = test name, $2 = expected file, remaining = pig -param arguments
    name=$1; expected=$2; shift 2
    pig -x mapreduce "$@" task2.pig > "$LOG/$name.log" 2>&1
    status=$?
    hadoop fs -cat '/Output/task2/part*' > "$LOG/$name.out" 2>/dev/null
    if [ $status -eq 0 ] && cmp -s "$LOG/$name.out" "$expected"; then
        verdict=PASS
    else
        verdict=FAIL
    fi
    parts=$(hadoop fs -ls /Output/task2 2>/dev/null | grep -c 'part-')
    echo "$verdict  $name  exit=$status  parts=$parts  lines=$(wc -l < "$LOG/$name.out")" | tee -a "$RESULTS"
}

: > "$RESULTS"
{
    echo "Captured UTC: $(date -u '+%Y-%m-%d %H:%M:%S')  host: $(hostname)"
    hadoop version 2>/dev/null | head -n 1
    pig -version 2>/dev/null | head -n 1
    ls /usr/lib/pig/lib 2>/dev/null | grep -i jython
} | tee -a "$RESULTS"

# 1. Canvas CSVs exactly as downloaded (CRLF line endings).
put_inputs "$BASE/data"
check range_2010_2020 "$EXP/expected_2010_2020.txt" -param START_YEAR=2010 -param END_YEAR=2020
check rerun_2010_2020 "$EXP/expected_2010_2020.txt" -param START_YEAR=2010 -param END_YEAR=2020
check single_2026     "$EXP/expected_2026_2026.txt" -param START_YEAR=2026 -param END_YEAR=2026
check no_params_all   "$EXP/expected_all.txt"
check full_2006_2026  "$EXP/expected_all.txt"       -param START_YEAR=2006 -param END_YEAR=2026
check no_games_2011   "$EXP/expected_2011_2013.txt" -param START_YEAR=2011 -param END_YEAR=2013
check single_2006     "$EXP/expected_2006_2006.txt" -param START_YEAR=2006 -param END_YEAR=2006
check range_2018_2022 "$EXP/expected_2018_2022.txt" -param START_YEAR=2018 -param END_YEAR=2022

# 2. Same data with LF line endings and with a header row in every file.
mkdir -p "$BASE/data_lf" "$BASE/data_header"
for f in countries games medal_table population; do
    tr -d '\r' < "$BASE/data/$f.csv" > "$BASE/data_lf/$f.csv"
    { echo "header,row,for,robustness,test"; cat "$BASE/data/$f.csv"; } > "$BASE/data_header/$f.csv"
done
put_inputs "$BASE/data_lf"
check lf_all          "$EXP/expected_all.txt"
put_inputs "$BASE/data_header"
check header_all      "$EXP/expected_all.txt"

# 3. Global year order across several reducer outputs (test copy only).
put_inputs "$BASE/data"
sed 's/^%default END_YEAR 9999$/%default END_YEAR 9999\nSET default_parallel 3;/' task2.pig > task2_parallel.pig
mv task2.pig task2.pig.orig && cp task2_parallel.pig task2.pig
check parallel3_all   "$EXP/expected_all.txt"
mv task2.pig.orig task2.pig && rm -f task2_parallel.pig

# 4. Leave the specification example as the final HDFS result.
check final_2010_2020 "$EXP/expected_2010_2020.txt" -param START_YEAR=2010 -param END_YEAR=2020

sha256sum "$BASE/s4271512_PG.zip" task2.pig task2.py > "$BASE/hashes-after.txt"
if diff -q "$BASE/hashes-before.txt" "$BASE/hashes-after.txt" > /dev/null; then
    echo "Submitted files unchanged during the run." | tee -a "$RESULTS"
fi
echo "FAIL count: $(grep -c '^FAIL' "$RESULTS")" | tee -a "$RESULTS"
