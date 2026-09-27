#!/usr/bin/env python3
"""Job 1 reducer: stream the secondary-sorted taxi/company join.

Input is partitioned by taxi_id and sorted by (taxi_id, tag), so tag 0 taxi
metadata arrives before tag 1 trips. No trip list is buffered.

Output:
    company_id, taxi_id, record_type(F or T), fare, distance

An F marker is emitted once per taxi so Job 2 can count the complete company
fleet even when a taxi has no trips.
"""

import sys


current_taxi = None
company_id = None
fleet_marker_emitted = False

for line in sys.stdin:
    fields = line.strip().split("\t")
    if len(fields) < 3:
        continue

    taxi_id, tag = fields[0], fields[1]
    if taxi_id != current_taxi:
        current_taxi = taxi_id
        company_id = None
        fleet_marker_emitted = False

    if tag == "0" and len(fields) == 3:
        company_id = fields[2]
        if not fleet_marker_emitted:
            print("%s\t%s\tF\t0.00\t0.00" % (company_id, taxi_id))
            fleet_marker_emitted = True

    elif tag == "1" and len(fields) == 4 and company_id is not None:
        try:
            fare = float(fields[2])
            distance = float(fields[3])
        except ValueError:
            continue
        print("%s\t%s\tT\t%.2f\t%.2f" % (company_id, taxi_id, fare, distance))
