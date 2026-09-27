#!/usr/bin/env python3
"""Job 3 reducer: output one contiguous third of the global revenue ranking.

Input per reducer is the complete company table, already sorted by revenue
descending and company ID ascending for ties. Bucket 0 outputs the first rank
third, bucket 1 the middle third, and bucket 2 the final third. With bucket
digits partitioned across three reducers, concatenating part files in reducer
number order is therefore globally sorted.
"""

import sys


def emit_rank_slice(bucket, records):
    if bucket is None or not records:
        return

    record_count = len(records)
    start = bucket * record_count // 3
    end = (bucket + 1) * record_count // 3

    for fields in records[start:end]:
        # Remove the internal bucket field and restore the required six fields:
        # company, revenue, trips, fleet, revenue/taxi, average distance.
        print("%s\t%s\t%s\t%s\t%s\t%s" % (fields[2], fields[1], fields[3], fields[4], fields[5], fields[6]))


current_bucket = None
records = []

for line in sys.stdin:
    fields = line.strip().split("\t")
    if len(fields) != 7:
        continue

    try:
        bucket = int(fields[0])
    except ValueError:
        continue

    if current_bucket is None:
        current_bucket = bucket
    elif bucket != current_bucket:
        emit_rank_slice(current_bucket, records)
        current_bucket = bucket
        records = []

    records.append(fields)

emit_rank_slice(current_bucket, records)
