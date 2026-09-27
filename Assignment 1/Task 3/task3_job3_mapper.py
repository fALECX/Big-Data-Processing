#!/usr/bin/env python3
"""Job 3 mapper: replicate the small company table to three sort buckets.

Each company summary is emitted once for bucket 0, 1, and 2. Hadoop partitions
by bucket and sorts by revenue descending, so all three reducers receive the
same ordered company table. Each reducer later outputs only its rank slice.
"""

import sys


for line in sys.stdin:
    fields = line.strip().split("\t")
    if len(fields) != 6:
        continue

    company_id, revenue = fields[0], fields[1]
    try:
        int(company_id)
        float(revenue)
        int(fields[2])
        int(fields[3])
        float(fields[4])
        float(fields[5])
    except ValueError:
        continue

    for bucket in range(3):
        print("%d\t%s\t%s\t%s\t%s\t%s\t%s" % (bucket, revenue, company_id, fields[2], fields[3], fields[4], fields[5]))
