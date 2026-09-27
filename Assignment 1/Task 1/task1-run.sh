#!/bin/bash
# Task 1 - Taxi-Level Trip Efficiency Analysis
# Runs end-to-end with no manual intervention: clears any previous output
# directory, then runs the streaming MapReduce job with 3 reducers.
# Compound key (taxi_id, trip_type) is grouped/partitioned as a 2-field key,
# matching the pattern taught for multi-field grouping (KeyFieldBasedPartitioner).

set -euo pipefail
cd "$(dirname "$0")"
chmod +x task1_mapper.py task1_reducer.py

hadoop fs -rm -r -f /Output/task1

hadoop jar /usr/lib/hadoop/hadoop-streaming.jar \
  -D stream.num.map.output.key.fields=2 \
  -D mapred.reduce.tasks=3 \
  -file ./task1_mapper.py \
  -mapper ./task1_mapper.py \
  -file ./task1_reducer.py \
  -reducer ./task1_reducer.py \
  -input /Input/Trips.txt \
  -output /Output/task1 \
  -partitioner org.apache.hadoop.mapred.lib.KeyFieldBasedPartitioner
