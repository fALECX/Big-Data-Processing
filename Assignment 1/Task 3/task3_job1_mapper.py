#!/usr/bin/env python3
"""Job 1 mapper: tag Taxis and Trips records for a reduce-side join.

Taxis mapper output: taxi_id, tag 0, company_id
Trips mapper output: taxi_id, tag 1, fare, distance

The composite key (taxi_id, tag) lets Hadoop sort taxi metadata before trip
records while partitioning only by taxi_id.
"""

import sys


for line in sys.stdin:
    fields = line.strip().split(",")

    if len(fields) == 4:  # Taxis.txt: taxi_id,company_id,model,year
        taxi_id, company_id = fields[0], fields[1]
        try:
            int(taxi_id)
            int(company_id)
        except ValueError:
            continue
        print("%s\t0\t%s" % (taxi_id, company_id))

    elif len(fields) == 8:  # Trips.txt
        taxi_id, fare_text, distance_text = fields[1], fields[2], fields[3]
        try:
            int(taxi_id)
            fare = float(fare_text)
            distance = float(distance_text)
        except ValueError:
            continue
        print("%s\t1\t%.2f\t%.2f" % (taxi_id, fare, distance))
