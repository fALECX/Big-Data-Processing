#!/usr/bin/env python3
import sys
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

# Task 1 - Taxi-Level Trip Efficiency Analysis
# Input line (Trips.txt): trip_id,taxi_id,fare,distance,pickup_x,pickup_y,dropoff_x,dropoff_y
# Trip type by distance: long >= 200, medium 100-200, short < 100
#
# In-mapper combining: state (a dict keyed by taxi_id+trip_type) is preserved
# across all input lines seen by this mapper task, and partial aggregates are
# only emitted once per key after the whole input split has been read. This
# cuts the number of <key,value> pairs shipped to the reducers compared to
# emitting one pair per trip.
#
# Emitted key/value (tab separated):
#   taxi_id  trip_type  partial_count  partial_max_cents  partial_min_cents  partial_sum_cents

stats = {}  # (taxi_id, trip_type) -> [count, max_cents, min_cents, sum_cents]

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    fields = line.split(",")
    if len(fields) != 8:
        continue  # skip malformed lines

    taxi_id, fare_text, distance_text = fields[1], fields[2], fields[3]
    try:
        # Store money as integer cents so mapper split boundaries and floating-
        # point addition cannot change the final two-decimal-place result.
        fare_cents = int(
            (Decimal(fare_text) * 100).quantize(
                Decimal("1"), rounding=ROUND_HALF_UP
            )
        )
        distance = float(distance_text)
    except (InvalidOperation, ValueError):
        continue

    if distance >= 200:
        trip_type = "long"
    elif distance >= 100:
        trip_type = "medium"
    else:
        trip_type = "short"

    key = (taxi_id, trip_type)
    if key in stats:
        s = stats[key]
        s[0] += 1
        if fare_cents > s[1]:
            s[1] = fare_cents
        if fare_cents < s[2]:
            s[2] = fare_cents
        s[3] += fare_cents
    else:
        stats[key] = [1, fare_cents, fare_cents, fare_cents]

for (taxi_id, trip_type), (count, max_cents, min_cents, sum_cents) in stats.items():
    print(
        "%s\t%s\t%d\t%d\t%d\t%d"
        % (taxi_id, trip_type, count, max_cents, min_cents, sum_cents)
    )
