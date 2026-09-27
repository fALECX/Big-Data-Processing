#!/bin/bash
# Task 3 - Company Performance Analysis: join, aggregate, then globally sort.

set -euo pipefail
cd "$(dirname "$0")"

STREAMING_JAR=/usr/lib/hadoop/hadoop-streaming.jar
TEMP_BASE=/tmp/bdp_assignment1_task3
JOB1_OUTPUT=$TEMP_BASE/job1_join
JOB2_OUTPUT=$TEMP_BASE/job2_aggregation
FINAL_OUTPUT=/Output/task3

chmod +x task3_job1_mapper.py task3_job1_reducer.py \
  task3_job2_mapper.py task3_job2_reducer.py \
  task3_job3_mapper.py task3_job3_reducer.py

# Remove stale intermediate/final directories so the script is end-to-end.
hadoop fs -rm -r -f "$TEMP_BASE"
hadoop fs -rm -r -f "$FINAL_OUTPUT"

# Job 1: reduce-side join on taxi_id. Partition by taxi_id; secondary-sort
# tag 0 metadata before tag 1 trip records so the reducer can stream the join.
hadoop jar "$STREAMING_JAR" \
  -D mapred.reduce.tasks=3 \
  -D stream.num.map.output.key.fields=2 \
  -D mapred.text.key.partitioner.options='-k1,1' \
  -D mapred.output.key.comparator.class=org.apache.hadoop.mapred.lib.KeyFieldBasedComparator \
  -D mapred.text.key.comparator.options='-k1,1n -k2,2n' \
  -file ./task3_job1_mapper.py \
  -mapper ./task3_job1_mapper.py \
  -file ./task3_job1_reducer.py \
  -reducer ./task3_job1_reducer.py \
  -input /Input/Taxis.txt \
  -input /Input/Trips.txt \
  -output "$JOB1_OUTPUT" \
  -partitioner org.apache.hadoop.mapred.lib.KeyFieldBasedPartitioner

# Job 2: aggregate by company while secondary-sorting by taxi_id. This lets
# reducers count distinct fleet members without holding a company-sized set.
hadoop jar "$STREAMING_JAR" \
  -D mapred.reduce.tasks=3 \
  -D stream.num.map.output.key.fields=2 \
  -D mapred.text.key.partitioner.options='-k1,1' \
  -D mapred.output.key.comparator.class=org.apache.hadoop.mapred.lib.KeyFieldBasedComparator \
  -D mapred.text.key.comparator.options='-k1,1n -k2,2n' \
  -file ./task3_job2_mapper.py \
  -mapper ./task3_job2_mapper.py \
  -file ./task3_job2_reducer.py \
  -reducer ./task3_job2_reducer.py \
  -input "$JOB1_OUTPUT" \
  -output "$JOB2_OUTPUT" \
  -partitioner org.apache.hadoop.mapred.lib.KeyFieldBasedPartitioner

# Job 3: replicate the small company-summary table to buckets 0,1,2. Each
# reducer receives a full revenue-descending order and emits its contiguous
# rank third. part-00000 + part-00001 + part-00002 is globally descending.
hadoop jar "$STREAMING_JAR" \
  -D mapred.reduce.tasks=3 \
  -D stream.num.map.output.key.fields=3 \
  -D mapred.text.key.partitioner.options='-k1,1' \
  -D mapred.output.key.comparator.class=org.apache.hadoop.mapred.lib.KeyFieldBasedComparator \
  -D mapred.text.key.comparator.options='-k1,1n -k2,2nr -k3,3n' \
  -file ./task3_job3_mapper.py \
  -mapper ./task3_job3_mapper.py \
  -file ./task3_job3_reducer.py \
  -reducer ./task3_job3_reducer.py \
  -input "$JOB2_OUTPUT" \
  -output "$FINAL_OUTPUT" \
  -partitioner org.apache.hadoop.mapred.lib.KeyFieldBasedPartitioner

# Only the assessed final directory remains.
hadoop fs -rm -r -f "$TEMP_BASE"

echo "Task 3 complete: $FINAL_OUTPUT"
