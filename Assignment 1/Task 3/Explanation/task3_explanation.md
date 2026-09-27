# Task 3 — Company performance analysis design

## Requirements addressed

The solution uses exactly three Hadoop Streaming jobs, with exactly three reducers in every job:

1. reduce-side join of `/Input/Taxis.txt` and `/Input/Trips.txt`;
2. company aggregation; and
3. total-revenue sorting in descending order.

The final assessed path is `/Output/task3`. Intermediate outputs stay under `/tmp/bdp_assignment1_task3` and are removed after success. Raw HDFS inputs are never copied to the EMR master's local filesystem.

## Complete pipeline

```text
/Input/Taxis.txt + /Input/Trips.txt
    ↓ Job 1: tag, partition by taxi, secondary-sort metadata before trips
(company, taxi, F/T, fare, distance)
    ↓ /tmp/bdp_assignment1_task3/job1_join
Job 2: in-mapper partials; partition company; secondary-sort taxi
(company, revenue, trips, fleet, revenue/taxi, average distance)
    ↓ /tmp/bdp_assignment1_task3/job2_aggregation
Job 3: replicate bounded company table to three ordered rank buckets
    ↓ each reducer sees the same revenue-descending company table
part-00000 = top third
part-00001 = middle third
part-00002 = final third
    ↓
/Output/task3 (global descending order after getmerge part*)
```

## Job 1 — reduce-side join

### Mapper input and output

The mapper distinguishes input record types by field count.

`Taxis.txt` input:

```text
taxi_id,company_id,model,year
```

Mapper output:

```text
taxi_id    0    company_id
```

`Trips.txt` input:

```text
trip_id,taxi_id,fare,distance,pickup_x,pickup_y,dropoff_x,dropoff_y
```

Mapper output:

```text
taxi_id    1    fare    distance
```

The first two fields form the composite mapper key. `KeyFieldBasedPartitioner` partitions on field 1 only (`taxi_id`), ensuring all metadata and trips for one taxi reach one reducer. `KeyFieldBasedComparator` sorts by numeric taxi ID and then numeric tag, so tag `0` metadata arrives before tag `1` trips.

### Reducer processing and output

The reducer remembers only the current taxi's `company_id`. Once tag `0` arrives, every following tag `1` trip can be emitted immediately, so it never buffers all trips for a taxi.

It emits one fleet marker per taxi:

```text
company_id    taxi_id    F    0.00    0.00
```

and one joined trip record per trip:

```text
company_id    taxi_id    T    fare    distance
```

The `F` marker ensures a taxi with zero trips still contributes to fleet size.

## Job 2 — company aggregation

### Mapper partial aggregation

The mapper preserves bounded state keyed by `(company_id, taxi_id)`:

```text
fleet_present, partial_revenue, partial_trip_count, partial_distance
```

It periodically flushes after 50,000 keys, so multiple mapper partials remain possible and safe. Mapper output is:

```text
company_id    taxi_id    fleet_present    partial_revenue    partial_trips    partial_distance
```

### Partition, secondary sort, and reducer

The partitioner uses `company_id`, while the comparator sorts by `(company_id, taxi_id)`. Thus all partials for one company reach the same reducer and all partials for one taxi are consecutive.

The reducer merges one taxi at a time. It increments fleet size once for each distinct taxi with an `F` marker and adds partial revenue, trips, and distance. It therefore uses constant streaming state rather than a company-sized set of taxi IDs.

For each company it calculates:

```text
revenue_per_taxi = total_revenue / fleet_size
average_distance = total_distance / total_trips
```

and emits the six final-format fields:

```text
company_id    total_revenue    total_trips    fleet_size    revenue_per_taxi    average_distance
```

## Job 3 — globally descending sort with three reducers

### Why ordinary hash partitioning is insufficient

A reverse numeric comparator sorts records only **inside** each reducer partition. Hashing companies across three reducers and concatenating their part files would not produce a globally sorted result. `TotalOrderPartitioner` is explicitly prohibited.

### Replicated-summary rank slicing

Job 2 produces only one bounded summary per company. The Job 3 mapper emits each summary three times using bucket keys `0`, `1`, and `2`:

```text
bucket    total_revenue    company_id    trips    fleet    revenue_per_taxi    average_distance
```

The job:

- partitions on `bucket`;
- sorts by bucket ascending;
- sorts total revenue numerically in reverse order; and
- uses company ID numerically as a deterministic tie-breaker.

For three reducers, the course's `KeyFieldBasedPartitioner` maps the one-byte digit keys directly to matching reducer numbers: its hash begins at zero and the partition is the non-negative hash modulo the reducer count, so ASCII `0`, `1`, and `2` map to partitions `0`, `1`, and `2`. See the [Apache Hadoop `KeyFieldBasedPartitioner` source](https://hadoop.apache.org/docs/r2.6.0/api/src-html/org/apache/hadoop/mapreduce/lib/partition/KeyFieldBasedPartitioner.html).

Every reducer consequently receives the complete company table in the same revenue-descending order. For `N` companies, bucket `b` outputs indices:

```text
start = floor(b × N / 3)
end   = floor((b + 1) × N / 3)
```

Therefore:

```text
part-00000 = ranks [0, floor(N/3))
part-00001 = ranks [floor(N/3), floor(2N/3))
part-00002 = ranks [floor(2N/3), N)
```

The marker's `getmerge /Output/task3/part*` command concatenates these contiguous rank ranges into one global descending sequence. The trade-off is threefold replication of the **small aggregated company table**, not the large trip dataset. All three reducers perform useful work.

## HDFS execution

The HDFS inputs must already exist with exact case-sensitive names:

```text
/Input/Taxis.txt
/Input/Trips.txt
```

From the Task 3 directory on the EMR master:

```bash
chmod +x task3-run.sh
./task3-run.sh
hadoop fs -ls /Output/task3
hadoop fs -cat '/Output/task3/part*'
```

The run script makes all mapper/reducer files executable, removes stale paths, chains all three jobs, and cleans intermediate outputs after success.

## Local validation result

The actual six Python programs were chained locally using the course pattern `mapper → sort → reducer` and compared with an independent direct calculation:

| Check | Verified value |
|---|---:|
| Valid taxis / total fleet | 500 |
| Companies / final lines | 19 |
| Valid trips / summed output trips | 30,000 |
| Job 1 output records | 30,500 (`500 F` + `30,000 T`) |
| Job 3 part sizes | 6, 6, 7 |
| Final revenue order | Globally descending |

The first three verified final lines are:

```text
0     356194.37    2112    34    10476.30    93.83
18    307067.86    1873    30    10235.60    91.09
5     299524.26    1851    32     9360.13    89.97
```
