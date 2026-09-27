# Task 2 — PAM clustering design

## Objective and parameters

Cluster every trip in `/Input/Trips.txt` by its drop-off coordinates using exact PAM/k-medoids. The first non-empty line of `initialization.txt` is the maximum iteration count `v`; every remaining line is one initial `(medoid_x, medoid_y)` pair, so their number defines `k`.

The program runs one Hadoop Streaming job per PAM iteration with exactly three reducers. The Python driver performs only iteration control and reads `k` reducer summaries; it never loads the complete trip dataset.

## Files

| File | Responsibility |
|---|---|
| `initialization.txt` | Supplies `v` and the `k` initial medoids. |
| `task2_mapper.py` | Assigns drop-off points to the nearest medoid and combines duplicate assigned coordinates. |
| `task2_reducer.py` | Performs the exact PAM swap/update calculation for each cluster. |
| `task2_driver.py` | Runs repeated Streaming jobs, reports each iteration, detects assignment convergence, and publishes final output. |
| `task2-run.sh` | End-to-end entry point executed on the EMR master. |

## One iteration: complete data flow

```text
/Input/Trips.txt in HDFS
    ↓ Streaming InputFormat / mapper stdin
mapper: assign each drop-off point to nearest current medoid
    ↓ in-mapper combine duplicate coordinates
(cluster_index, dropoff_x, dropoff_y, partial_count)
    ↓ default hash partition by cluster_index; shuffle and sort
reducer: merge partial counts and evaluate every assigned point as medoid
    ↓
(cluster_index, new_x, new_y, #points, avg_dissimilarity, membership_signature)
    ↓ HDFS /tmp/bdp_assignment1_task2/iteration_NNN/part-*
driver: print report, update medoids, compare assignment signatures
    ↓ repeat unless assignments are unchanged or iteration v finishes
/Output/task2/part-00000
```

### Mapper input and processing

Each mapper reads `Trips.txt` line by line:

```text
trip_id,taxi_id,fare,distance,pickup_x,pickup_y,dropoff_x,dropoff_y
```

It loads the current medoids from `task2_medoids.txt`, which the driver distributes with Hadoop Streaming's `-file` option. For each drop-off point `p=(x,y)`, it selects the lowest-index medoid minimizing Euclidean distance. Comparing squared distances gives the same nearest-medoid ordering while avoiding unnecessary square roots.

The mapper preserves a dictionary across input lines:

```text
(cluster_index, x, y) → occurrence_count
```

It flushes the dictionary after 50,000 distinct keys to bound memory. Multiple partial records remain correct because the reducer adds their counts.

Mapper output has four tab-separated fields:

```text
cluster_index    dropoff_x    dropoff_y    partial_count
```

For example, three identical points assigned to cluster `1` can become:

```text
1    20.805    35.172    3
```

instead of three separate records. This reduces mapper output and shuffle traffic without approximating the dataset.

### Partition, shuffle, and reducer input

The first tab-separated field is the Streaming key. The default hash partitioner therefore sends every record for one `cluster_index` to the same reducer. The job requests three reducers; depending on `k` and hash placement, one reducer may process more than one cluster or none.

Within a cluster, the reducer merges mapper partials into:

```text
(dropoff_x, dropoff_y) → global_count_within_cluster
```

The reducer holds only the distinct weighted points for its current cluster, not all trips or all clusters.

### Exact weighted PAM update

Every distinct assigned point `o` is evaluated as the replacement medoid. If point `p` occurs `w_p` times and the cluster contains `N` trips, the candidate cost is:

```text
avg_dissimilarity(o) = Σ_p [w_p × EuclideanDistance(o,p)] / N
```

The candidate with the smallest average dissimilarity becomes the new medoid. Weighting duplicates is mathematically identical to repeating the same distance once per trip, so mapper-side compression does not change the PAM result.

The reducer emits six internal fields:

```text
cluster_index    new_medoid_x    new_medoid_y    #points    avg_dissimilarity    membership_signature
```

The SHA-256 membership signature is calculated from sorted `(x,y,count)` entries. The driver compares signatures for consecutive iterations; identical signatures mean no point assignments changed, satisfying the required convergence test without returning every assignment to the driver.

## Iteration control and HDFS paths

The driver writes current medoids to a small local `task2_medoids.txt`, then submits a three-reducer job. Intermediate outputs are kept outside the assessed directory:

```text
/tmp/bdp_assignment1_task2/iteration_001
/tmp/bdp_assignment1_task2/iteration_002
...
```

At every iteration the terminal displays:

```text
iteration number
cluster index, medoid coordinates, #points, avg_dissimilarity
```

The loop stops when assignment signatures are unchanged or after `v` iterations. Temporary HDFS iteration directories are then removed.

## Final output

The driver writes exactly one line per cluster, ordered by cluster index but without printing that index:

```text
medoid_x    medoid_y    #points    avg_dissimilarity
```

It publishes these lines as `/Output/task2/part-00000`, so the required command works directly:

```bash
hadoop fs -getmerge /Output/task2/part* task2_output.txt
```

For the supplied 30,000-trip dataset and initialization file, local validation converged after five iterations and produced:

```text
51.323    78.236    14576    24.68
13.409    25.872     9181    20.85
70.175    17.378     6243    17.82
```

The cluster counts sum to 30,000. The supplied data has 100 distinct drop-off coordinates, so weighted duplicate aggregation reduces the exact candidate calculation substantially. In general, exact PAM update cost remains quadratic in the number of distinct assigned points per cluster because every assigned point must be evaluated as a candidate.

## Execution on the EMR master

The required HDFS input must already exist as `/Input/Trips.txt`. From the directory containing all Task 2 files:

```bash
chmod +x task2-run.sh
./task2-run.sh
hadoop fs -ls /Output/task2
hadoop fs -cat '/Output/task2/part*'
```

`task2-run.sh` makes the mapper and reducer executable before the driver submits them to Hadoop Streaming.
