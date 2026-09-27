#!/usr/bin/env python3
"""Job 2 reducer: aggregate taxi partials into company performance metrics.

Input is partitioned by company_id and sorted by (company_id, taxi_id), making
all partials for one taxi consecutive. The reducer streams one taxi at a time,
then emits one six-field company summary.
"""

import sys


current_company = None
current_taxi = None

taxi_present = False
taxi_revenue = 0.0
taxi_trips = 0
taxi_distance = 0.0

company_fleet = 0
company_revenue = 0.0
company_trips = 0
company_distance = 0.0


def add_current_taxi():
    global company_fleet, company_revenue, company_trips, company_distance
    if current_taxi is None:
        return
    if taxi_present:
        company_fleet += 1
    company_revenue += taxi_revenue
    company_trips += taxi_trips
    company_distance += taxi_distance


def emit_current_company():
    if current_company is None or company_fleet == 0:
        return
    revenue_per_taxi = company_revenue / company_fleet
    average_distance = company_distance / company_trips if company_trips else 0.0
    print(
        "%s\t%.2f\t%d\t%d\t%.2f\t%.2f"
        % (
            current_company,
            company_revenue,
            company_trips,
            company_fleet,
            revenue_per_taxi,
            average_distance,
        )
    )


for line in sys.stdin:
    fields = line.strip().split("\t")
    if len(fields) != 6:
        continue

    company_id, taxi_id = fields[0], fields[1]
    try:
        fleet_partial = int(fields[2])
        revenue_partial = float(fields[3])
        trips_partial = int(fields[4])
        distance_partial = float(fields[5])
    except ValueError:
        continue

    if current_taxi is None:
        current_company, current_taxi = company_id, taxi_id
    elif company_id != current_company or taxi_id != current_taxi:
        previous_company = current_company
        add_current_taxi()

        if company_id != previous_company:
            emit_current_company()
            company_fleet = 0
            company_revenue = 0.0
            company_trips = 0
            company_distance = 0.0

        current_company, current_taxi = company_id, taxi_id
        taxi_present = False
        taxi_revenue = 0.0
        taxi_trips = 0
        taxi_distance = 0.0

    taxi_present = taxi_present or fleet_partial > 0
    taxi_revenue += revenue_partial
    taxi_trips += trips_partial
    taxi_distance += distance_partial

add_current_taxi()
emit_current_company()
