#!/usr/bin/env python3
"""Assign trip drop-off points to their nearest current medoid.

Input (Trips.txt):
    trip_id,taxi_id,fare,distance,pickup_x,pickup_y,dropoff_x,dropoff_y

Mapper output (tab separated):
    cluster_index    dropoff_x    dropoff_y    partial_count

The dictionary is an in-mapper combiner. Repeated coordinates assigned to the
same cluster are emitted once per mapper flush, reducing shuffle traffic while
preserving the exact multiplicity needed by the PAM update.
"""

import sys


MEDOIDS_FILE = "task2_medoids.txt"
MAX_BUFFERED_KEYS = 50000


def load_medoids(path):
    medoids = []
    with open(path, encoding="utf-8") as source:
        for line_number, line in enumerate(source, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                x_text, y_text = line.split()
                medoids.append((float(x_text), float(y_text)))
            except ValueError:
                raise ValueError(
                    "Invalid medoid on line %d of %s" % (line_number, path)
                )
    if not medoids:
        raise ValueError("No medoids were supplied in %s" % path)
    return medoids


def nearest_medoid(x, y, medoids):
    """Return the lowest-index medoid at minimum Euclidean distance.

    Squared distance is sufficient for comparison and avoids an unnecessary
    square root for every medoid examined by the mapper.
    """
    best_index = 0
    best_distance_squared = None
    for index, (medoid_x, medoid_y) in enumerate(medoids):
        distance_squared = (x - medoid_x) ** 2 + (y - medoid_y) ** 2
        if best_distance_squared is None or distance_squared < best_distance_squared:
            best_index = index
            best_distance_squared = distance_squared
    return best_index


def emit_counts(point_counts):
    for (cluster_index, x, y), count in point_counts.items():
        print("%d\t%.3f\t%.3f\t%d" % (cluster_index, x, y, count))


medoids = load_medoids(MEDOIDS_FILE)
point_counts = {}

for line in sys.stdin:
    fields = line.strip().split(",")
    if len(fields) != 8:
        continue

    try:
        dropoff_x = float(fields[6])
        dropoff_y = float(fields[7])
    except ValueError:
        continue

    cluster_index = nearest_medoid(dropoff_x, dropoff_y, medoids)
    key = (cluster_index, dropoff_x, dropoff_y)
    point_counts[key] = point_counts.get(key, 0) + 1

    # Bound memory for data with many distinct coordinates. Multiple partial
    # records for a point are safely merged by the reducer.
    if len(point_counts) >= MAX_BUFFERED_KEYS:
        emit_counts(point_counts)
        point_counts.clear()

emit_counts(point_counts)
