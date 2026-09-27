#!/usr/bin/env python3
"""Job 2 mapper: create per-(company,taxi) partial aggregates.

Input from Job 1:
    company_id, taxi_id, F/T, fare, distance

Output:
    company_id, taxi_id, fleet_present, partial_revenue,
    partial_trip_count, partial_distance

State is preserved across mapper input lines and periodically flushed, so the
mapper reduces shuffle traffic without assuming the complete input fits in
memory.
"""

import sys


MAX_BUFFERED_KEYS = 50000


def emit_partials(partials):
    for (company_id, taxi_id), values in partials.items():
        fleet_present, revenue, trips, distance = values
        print(
            "%s\t%s\t%d\t%.2f\t%d\t%.2f"
            % (company_id, taxi_id, fleet_present, revenue, trips, distance)
        )


partials = {}

for line in sys.stdin:
    fields = line.strip().split("\t")
    if len(fields) != 5:
        continue

    company_id, taxi_id, record_type = fields[0], fields[1], fields[2]
    key = (company_id, taxi_id)
    if key not in partials:
        partials[key] = [0, 0.0, 0, 0.0]

    values = partials[key]
    if record_type == "F":
        values[0] = 1
    elif record_type == "T":
        try:
            fare = float(fields[3])
            distance = float(fields[4])
        except ValueError:
            continue
        values[1] += fare
        values[2] += 1
        values[3] += distance
    else:
        continue

    if len(partials) >= MAX_BUFFERED_KEYS:
        emit_partials(partials)
        partials.clear()

emit_partials(partials)
