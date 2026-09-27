#!/usr/bin/env python3
import sys
from decimal import Decimal, ROUND_HALF_UP

# Task 1 - Reducer
# Receives partial aggregates from each mapper's in-mapper combining step,
# grouped/sorted by the compound key (taxi_id, trip_type) thanks to
# stream.num.map.output.key.fields=2 + KeyFieldBasedPartitioner in task1-run.sh.
# Final aggregation only: merge partial counts/sums/max/min and compute the average.

current_taxi = None
current_type = None
count = 0
max_cents = None
min_cents = None
sum_cents = 0


def cents_to_text(value):
    return format(Decimal(value) / Decimal(100), ".2f")


def emit(taxi_id, trip_type, count, max_cents, min_cents, sum_cents):
    avg_fare = (Decimal(sum_cents) / Decimal(100 * count)).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    print(
        "%s\t%s\t%d\t%s\t%s\t%s"
        % (
            taxi_id,
            trip_type,
            count,
            cents_to_text(max_cents),
            cents_to_text(min_cents),
            format(avg_fare, ".2f"),
        )
    )


for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    taxi_id, trip_type, c, mx, mn, sm = line.split("\t")
    c = int(c)
    mx = int(mx)
    mn = int(mn)
    sm = int(sm)

    if taxi_id == current_taxi and trip_type == current_type:
        count += c
        sum_cents += sm
        if mx > max_cents:
            max_cents = mx
        if mn < min_cents:
            min_cents = mn
    else:
        if current_taxi is not None:
            emit(current_taxi, current_type, count, max_cents, min_cents, sum_cents)
        current_taxi, current_type = taxi_id, trip_type
        count, max_cents, min_cents, sum_cents = c, mx, mn, sm

if current_taxi is not None:
    emit(current_taxi, current_type, count, max_cents, min_cents, sum_cents)
