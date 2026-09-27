#!/usr/bin/env python3
"""Perform the exact PAM medoid-update step for each assigned cluster.

Reducer input (grouped by cluster_index):
    cluster_index    dropoff_x    dropoff_y    partial_count

Internal reducer output consumed by task2_driver.py:
    cluster_index    medoid_x    medoid_y    #points    avg_dissimilarity    membership_signature

The reducer merges mapper partial counts, then tests every distinct assigned
point as the swap candidate. Counts are used as weights, so duplicate points
have exactly the same effect as processing every trip individually.
"""

import hashlib
import math
import sys


def average_dissimilarity(candidate, weighted_points, total_count):
    candidate_x, candidate_y = candidate
    total_distance = 0.0
    for (point_x, point_y), count in weighted_points.items():
        total_distance += math.hypot(candidate_x - point_x, candidate_y - point_y) * count
    return total_distance / total_count


def membership_signature(weighted_points):
    """Create a deterministic signature for assignment-convergence testing."""
    digest = hashlib.sha256()
    for (x, y), count in sorted(weighted_points.items()):
        digest.update(("%.3f,%.3f:%d;" % (x, y, count)).encode("ascii"))
    return digest.hexdigest()


def choose_medoid(weighted_points):
    """Return the assigned data point with minimum weighted average distance."""
    total_count = sum(weighted_points.values())
    candidates = sorted(weighted_points)
    best_candidate = candidates[0]
    best_cost = average_dissimilarity(best_candidate, weighted_points, total_count)

    for candidate in candidates[1:]:
        cost = average_dissimilarity(candidate, weighted_points, total_count)
        if cost < best_cost:
            best_candidate = candidate
            best_cost = cost

    return best_candidate, total_count, best_cost


def emit_cluster(cluster_index, weighted_points):
    if cluster_index is None or not weighted_points:
        return
    medoid, total_count, cost = choose_medoid(weighted_points)
    signature = membership_signature(weighted_points)
    print(
        "%d\t%.3f\t%.3f\t%d\t%.2f\t%s"
        % (cluster_index, medoid[0], medoid[1], total_count, cost, signature)
    )


current_cluster = None
weighted_points = {}

for line in sys.stdin:
    fields = line.strip().split("\t")
    if len(fields) != 4:
        continue

    try:
        cluster_index = int(fields[0])
        point = (float(fields[1]), float(fields[2]))
        partial_count = int(fields[3])
    except ValueError:
        continue

    if partial_count <= 0:
        continue

    if current_cluster is None:
        current_cluster = cluster_index
    elif cluster_index != current_cluster:
        emit_cluster(current_cluster, weighted_points)
        current_cluster = cluster_index
        weighted_points = {}

    weighted_points[point] = weighted_points.get(point, 0) + partial_count

emit_cluster(current_cluster, weighted_points)
