# Big Data Processing — Learning Summary and Lab Cheat Sheet

**Last updated:** 2 November 2026

**Current coverage:** Weeks 1-10 (Week 10 lecture and Week 11 material not local); AWS/EMR and HDFS/YARN foundations; MapReduce execution, including graph shortest paths; Python Streaming; local/weighted aggregation, including per-key averages with a true combiner; iterative jobs; pairs and stripes; composite-key partitioning, secondary sort, joins, multi-job pipelines; co-occurrence matrices and relative frequencies; clustering, HAC, K-means and iterative MapReduce programming; rubric-based Assignment 1 verification and post-marking design lessons; deterministic decimal aggregation; submission-artifact version control and visual QA; Pig/Hive, including efficient Pig dataflow design, parameters and Jython UDFs; Mahout/Solr/Storm, Spark RDDs and Spark Streaming, including DStreams, HDFS file streams, `foreachRDD` output, `updateStateByKey` and checkpointing; Assignment 2 Pig runbook, EMR verification and submission set; Assignment 3 Spark Streaming runbook and submission set.

This is a living revision paper. Part I develops understanding in lecture order and finishes each covered week with active-recall questions. Part II is the shortest practical and exam-ready reference.

---

# Part I — Chronological learning summary

## Week 1 — Why big data needs distributed processing

### What makes data “big”?

Big data is commonly described by the **3Vs**:

- **Volume:** more data than one machine can conveniently store or process.
- **Velocity:** data arrives or must be processed quickly.
- **Variety:** data appears in different structures and formats.

The important point is not a fixed number of gigabytes. Data becomes “big” when ordinary single-machine methods are no longer adequate for the required storage, speed, or analysis.

### The three central design ideas

1. **Scale out, not only up.** Add more commodity machines instead of continually buying one larger machine.
2. **Expect failures.** With many machines, hardware or processes will regularly fail. The framework must detect failures and redo work.
3. **Move processing to the data.** Sending a small program to machines that already hold the data is usually cheaper than transferring a huge dataset to one processor.

These ideas lead naturally to Hadoop: distribute the storage with HDFS, distribute computation with MapReduce, and coordinate resources with YARN.

### Active recall — Week 1

1. What are the 3Vs of big data?
2. What is the difference between scaling **up** and scaling **out**?
3. Why must a large distributed system assume that failures will occur?
4. Why is moving processing to the data often preferable to moving the data?

<details>
<summary>Show answers</summary>

1. **Volume, velocity and variety.**
2. Scaling **up** makes one machine more powerful; scaling **out** adds more machines that cooperate.
3. A cluster contains many components, so even individually reliable machines produce regular failures at scale. The framework must detect failures and repeat incomplete work.
4. Moving a small program usually consumes less network bandwidth than transferring a very large dataset to a central processor.

</details>

---

## Week 2 — Cloud, Hadoop, HDFS, YARN and the AWS environment

### Cloud and virtualisation

**Utility computing** provides computing resources as a metered, pay-as-you-go service. **Virtualisation** lets a physical server host multiple isolated virtual machines. An AWS **EC2 instance** is one such virtual computer.

Common cloud service layers:

- **IaaS:** virtual infrastructure such as machines, networks and disks.
- **PaaS:** a managed platform for building or running applications; AWS EMR provides a managed platform for Hadoop workloads.
- **SaaS:** complete software delivered to users as a service.

### Hadoop’s three core responsibilities

```text
Hadoop environment
├── HDFS       → distributed storage
├── YARN       → resource management and job scheduling
└── MapReduce  → distributed data-processing model
```

- **HDFS** divides large files into blocks and distributes those blocks across machines. Replication provides fault tolerance.
- The **NameNode** maintains filesystem metadata: filenames, permissions and the locations of blocks.
- **DataNodes** store the actual HDFS blocks and report their health and block lists.
- **YARN ResourceManager** allocates cluster resources among applications.
- A **NodeManager** manages resources and containers on an individual node.
- A **container** is an allocated bundle of resources—such as memory and CPU—in which a task runs. It is not another physical computer.

[![Official Apache HDFS architecture diagram showing a NameNode, DataNodes, clients, file blocks and replication](https://hadoop.apache.org/docs/r3.4.0/hadoop-project-dist/hadoop-hdfs/images/hdfsarchitecture.png)](https://hadoop.apache.org/docs/r3.4.0/hadoop-project-dist/hadoop-hdfs/HdfsDesign.html)

*Figure: Clients ask the NameNode for metadata and block locations, but file data flows directly between clients and DataNodes. Source: [Apache Hadoop HDFS Architecture](https://hadoop.apache.org/docs/r3.4.0/hadoop-project-dist/hadoop-hdfs/HdfsDesign.html).*

> [!IMPORTANT]
> The NameNode coordinates metadata; it is not the route through which all file contents flow. DataNodes store and serve the actual blocks.

### Cluster, instance and node

```text
One EMR cluster
│
├── EC2 instance → master node → coordinates the cluster
├── EC2 instance → core node   → stores HDFS blocks and runs tasks
├── EC2 instance → core node   → stores HDFS blocks and runs tasks
└── EC2 instance → task node   → runs tasks only; optional
```

- An **instance** is AWS terminology for one virtual machine.
- A **node** is that machine participating in a distributed system, usually described by its role.
- A **cluster** is the complete group of connected nodes working together.

In an EMR Hadoop cluster, one EC2 instance normally corresponds to one node. The course calls the coordinating machine the **master node**. Core nodes both process work and store HDFS data; optional task nodes provide computation without storing HDFS data.

### The course AWS path

```text
Local Windows machine / VS Code
              │ SSH
              ▼
bdp-jump: jumphost (user ec2-user)
  • stable front door into the RMIT AWS network
  • creates and terminates the EMR cluster
  • is not a Hadoop cluster node
              │ SSH / VS Code ProxyJump
              ▼
bdp-emr: EMR master node (user hadoop)
  • exists only while the cluster is running
  • runs Hadoop, HDFS, YARN and MapReduce commands
```

The two VS Code SSH entries are aliases in `~/.ssh/config`:

- `bdp-jump` connects to the jumphost using the course PEM key.
- `bdp-emr` connects to the EMR master through `bdp-jump`. `ProxyJump` performs the intermediate hop automatically.

On this Windows machine, the configuration file is `C:\Users\samue\.ssh\config`. One `Host` entry can declare multiple aliases, so changing `Host bdp-jump` to `Host bdp-jump jumphost` makes both names work without breaking the existing `ProxyJump bdp-jump` setting. If the old alias is removed instead, every reference to it—including `ProxyJump`—must also be updated.

**EMR** means **Amazon Elastic MapReduce**, AWS’s managed service for creating Hadoop-style clusters. “EBR” is not the service used here.

### Cluster lifecycle

1. Connect to `bdp-jump`.
2. Run `./create_cluster.sh`; provisioning may take about 15 minutes.
3. Wait until the EMR state is `WAITING`, meaning it is ready for jobs.
4. Connect to `bdp-emr` and do the Hadoop work.
5. Copy out anything that must be retained.
6. Return to `bdp-jump` and run `./terminate_cluster.sh`.

Creating a cluster provisions additional, billable EC2 instances. Terminating it releases them. The jumphost remains available, but the EMR master and worker nodes disappear.

[![Official AWS diagram of an Amazon EMR cluster lifecycle from starting and bootstrapping through running, waiting and termination](https://docs.aws.amazon.com/images/emr/latest/ManagementGuide/images/emr-cluster-lifecycle.png)](https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-overview.html#emr-overview-cluster-lifecycle)

*Figure: The EMR lifecycle explains why SSH may not work while the cluster is still starting and why a finished job can leave a billable cluster in `WAITING`. Source: [AWS — Understanding the EMR cluster lifecycle](https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-overview.html#emr-overview-cluster-lifecycle).*

> [!WARNING]
> `WAITING` means ready and idle—not terminated. The course cluster must still be shut down with `./terminate_cluster.sh` when the session is finished.

### Active recall — Week 2

1. How do an EC2 instance, a Hadoop node and a cluster differ?
2. What are the roles of EMR master, core and task nodes?
3. Why do you connect through `bdp-jump` before reaching `bdp-emr`?
4. What responsibilities do HDFS and YARN have?
5. Where do you create and terminate the cluster, and where do you run Hadoop jobs?

<details>
<summary>Show answers</summary>

1. An **instance** is one AWS virtual machine; a **node** is a machine participating in Hadoop with a particular role; a **cluster** is the complete cooperating group of nodes.
2. The **master** coordinates the cluster; **core** nodes store HDFS data and run tasks; optional **task** nodes run tasks without storing HDFS data.
3. The jumphost is the stable, secured gateway into RMIT's AWS network. `ProxyJump` lets the local SSH client perform this hop automatically.
4. **HDFS** distributes and replicates stored data; **YARN** allocates resources and schedules application tasks.
5. Run `create_cluster.sh` and `terminate_cluster.sh` on `bdp-jump`; run Hadoop, HDFS and MapReduce commands on `bdp-emr`.

</details>

---

## Week 3 — MapReduce basics and Python WordCount

### The MapReduce abstraction

The programmer expresses a distributed algorithm primarily through:

```text
map(k1, v1)                 → list of (k2, v2)
reduce(k2, list of v2)      → list of (k3, v3)
```

Optional stages include:

```text
combine(k2, list of v2)     → locally aggregated (k2, v2)
partition(k2, reducers)     → reducer number for that key
```

The framework handles where tasks run, scheduling, transferring intermediate data, sorting and grouping keys, and retrying failed work.

### The complete record-processing pipeline

The lab presents eight logical stages:

```text
HDFS input
   ↓ InputFormat chooses files and defines logical records
input splits
   ↓ one map task is normally created per split
RecordReader converts split bytes into input (k1, v1) records
   ↓
mapper emits intermediate (k2, v2) pairs
   ↓ partition chooses reducer; shuffle transfers pairs
sort groups equal keys within each reducer partition
   ↓
reducer emits final (k3, v3) pairs
   ↓ OutputFormat writes HDFS part files
HDFS output directory
```

- **InputFormat** validates/selects the input and determines logical splits and how records are represented.
- An **input split** describes a mapper's logical portion of the input. It is not itself a copy of the data and should not be confused with an HDFS storage block, although Hadoop uses block locations to schedule data-local work.
- **RecordReader** turns bytes from a split into mapper input records. With ordinary text input, the key is typically the byte offset of the line and the value is the line's text; the Python Streaming mapper receives the text through standard input.
- **OutputFormat** writes reducer records into the job's HDFS output directory. Each reducer writes its own `part-*` file.

### What the execution framework does

MapReduce separates **what** to compute from **how** it runs. The programmer supplies map/reduce logic and may supply a combiner or partitioner; the runtime handles:

| Runtime responsibility | What it means |
|---|---|
| Scheduling | Break a job into map/reduce tasks and allocate YARN containers as resources become available. The YARN ResourceManager's scheduler shares resources among tasks and jobs. |
| Data distribution/locality | Prefer to run a mapper on the node containing its HDFS block—move code to data. If unavailable, use another node and transfer the data, preferably within the same rack. |
| Synchronisation | Ensure intermediate pairs are partitioned, shuffled, sorted, and grouped before a reducer consumes a key's values. |
| Fault handling | Detect failed task attempts and rerun work rather than expecting every commodity machine and every input record to be flawless. |

A **straggler** is an unusually slow task that delays the whole job. If a machine is abnormally slow, speculative execution can run a duplicate attempt elsewhere and retain the first successful result. If the real cause is **key skew**—for example, one extremely frequent word sends far more values to one reducer—duplicating the same heavy work does not remove the imbalance; partitioning or algorithm design must address it.

The framework deliberately hides exact placement and timing. Application code should not assume which machine runs a task, when it starts, which split a particular mapper receives, or which reducer number receives a key.

### Complete WordCount data flow

For this input:

```text
pig wolf pig
```

the stages are:

```text
Input record
    │
    ▼ map: tokenise and emit one pair per occurrence
(pig, 1) (wolf, 1) (pig, 1)
    │
    ▼ partition + shuffle + sort
(pig, [1, 1])   (wolf, [1])
    │
    ▼ reduce: sum each key's values
(pig, 2)        (wolf, 1)
```

Important guarantees:

- Every value for the same key is sent to the same reducer.
- The default partitioner hashes the intermediate key to select a reducer. A custom partitioner can change placement, but equal keys must still be routed consistently.
- Mapper output is sorted and grouped **by key** before reduction.
- The values belonging to a key should not be assumed to be sorted.
- With multiple reducers, each reducer writes a separate `part-*` output file.
- Keys are sorted within a reducer partition; simply concatenating several `part-*` files does not guarantee one globally sorted file.

### What the Week 3 mapper does

The mapper is used first in the MapReduce data-processing pipeline. After Hadoop divides the HDFS input into **input splits**, mapper tasks read the records in those splits—here, one text line at a time. Multiple mappers can run in parallel on different splits, preferably on or near the nodes storing the corresponding HDFS blocks. Each mapper transforms raw input into intermediate key-value pairs; it does not calculate the final total.

```text
HDFS file → input splits → parallel mapper tasks → intermediate (word, 1) pairs
                                                    ↓
                                      partition + shuffle + sort
                                                    ↓
                                                 reducers
```

WordCount uses the mapper once per input record because it must convert unstructured text into keyed records that Hadoop can group. A map-only job can deliberately omit reducers, but this WordCount job needs reducers to add the counts for equal words.

The essential mapper pattern is:

```python
for line in sys.stdin:
    words = line.strip().split()
    for word in words:
        print(f"{word}\t1")
```

It processes input line by line and emits `(word, 1)` **for every occurrence**, not once per distinct word and not `(word, count)`. If `pig` occurs three times, the mapper initially emits three `(pig, 1)` pairs.

Therefore, for the sample multiple-choice question, the correct answer is:

> Given a document, it emits a key-value pair `(word, 1)` for every word in the document.

The actual Week 3 `mapper.py` additionally removes non-alphanumeric characters and ignores empty tokens.

Line by line, its inner logic is:

```python
words = line.split(" ")

for word in words:
    word = "".join(c for c in word if c.isalnum())
    if word.strip():
        print("%s\t%s" % (word, "1"))
```

1. `split(" ")` splits specifically at space characters. Consecutive spaces can therefore create empty strings in `words` (unlike `split()` with no argument, which treats runs of whitespace as one separator).
2. The generator `c for c in word if c.isalnum()` visits every character and keeps only letters and digits. `"".join(...)` joins the kept characters into one cleaned word. For example, `"pig!"` becomes `"pig"`, and `"don't"` becomes `"dont"`.
3. `if word.strip():` checks that something remains after cleaning. A token such as `"!!!"` becomes empty and is not emitted.
4. `print("%s\t%s" % (word, "1"))` writes the word, a tab, and `1` to standard output. In Streaming, Hadoop interprets this as the intermediate key-value pair `(word, 1)`.

For example:

```text
Input line:     Pig!  pig, !!! R2-D2
After split:    ["Pig!", "", "pig,", "!!!", "R2-D2"]
After cleaning: ["Pig", "", "pig", "", "R2D2"]
Mapper output:  Pig\t1
                pig\t1
                R2D2\t1
```

The mapper is case-sensitive, so `Pig` and `pig` remain different keys. Removing punctuation from inside a token also concatenates its pieces: `R2-D2` becomes `R2D2`. These are design choices, not requirements of MapReduce.

### What the reducer does

The reducer reads the sorted mapper output one line at a time. It keeps:

- `current_word`: the key currently being accumulated.
- `current_count`: the running total for that key.

When the key changes, the previous word and total are printed, and accumulation starts for the new word. A final print after the loop is essential because the last key is never followed by a different key that would otherwise trigger output.

The reducer can use only small running state because Hadoop has already placed equal keys together.

The actual Week 3 `reducer.py` follows this streaming pattern:

```python
current_word = None
current_count = 0
word = None

for line in sys.stdin:
    line = line.strip()
    word, count = line.split("\t")
    try:
        count = int(count)
    except ValueError:
        continue

    if current_word == word:
        current_count += count
    else:
        if current_word:
            print("%s\t%s" % (current_word, current_count))
        current_count = count
        current_word = word

if current_word == word:
    print("%s\t%s" % (current_word, current_count))
```

Line by line:

1. `current_word` and `current_count` store the key currently being processed and its running total. They are state carried from one input line to the next.
2. `word, count = line.split("\t")` separates a Streaming record such as `pig\t1` into key `pig` and textual value `1`.
3. `count = int(count)` converts the value to an integer so addition is numeric. A non-integer value is skipped by `except ValueError`.
4. If `word` still equals `current_word`, its count is added to the running total.
5. If the word changes, all records for the previous key have finished because Hadoop sorted the input. The reducer prints that previous key and total, then starts a new accumulation.
6. The post-loop print emits the final key, which never encounters a later key change inside the loop.

Worked state trace for sorted reducer input:

| Input record | State/action | Output now |
|---|---|---|
| `pig\t1` | Start `pig`; total = 1 | — |
| `pig\t1` | Same key; total = 2 | — |
| `pig\t1` | Same key; total = 3 | — |
| `wolf\t1` | Key changed; emit `pig`, then start `wolf` at 1 | `pig\t3` |
| End of input | Emit the final accumulated key | `wolf\t1` |

> [!IMPORTANT]
> This reducer is correct for Hadoop's sorted, non-empty WordCount input, but its final condition `if current_word == word` is fragile: with completely empty input, both variables remain `None`, so it prints `None\t0`. The safer condition is `if current_word is not None`. Also, `split("\t", 1)` is safer than `split("\t")` when a value might contain another tab.

### Hadoop Streaming

Hadoop is Java-based, but **Hadoop Streaming** allows any executable that communicates through standard input and output to act as a mapper or reducer:

```text
HDFS input → Hadoop → mapper stdin
mapper stdout → shuffle/sort → reducer stdin
reducer stdout → HDFS output
```

The tab character (`\t`) separates the textual key and value. Debug messages should go to standard error, not standard output, because standard output is treated as MapReduce data.

### Bash run script

The Week 3 shell script packages one repeatable Hadoop command. It identifies the Streaming JAR, supplies the Python mapper and reducer to worker nodes, selects HDFS input and output paths, and can set the reducer count.

Conceptual form:

```bash
hadoop jar <streaming-jar> \
  -D mapreduce.job.reduces=3 \
  -files mapper.py,reducer.py \
  -mapper mapper.py \
  -reducer reducer.py \
  -input /3littlepigs.txt \
  -output /output
```

The exact Streaming JAR path is cluster-version dependent. Use the path in the course-provided script. Hadoop refuses to overwrite an existing HDFS output directory, so remove or rename `/output` before rerunning.

Before launching the supplied script on the EMR master:

```bash
chmod +x run-5.sh
./run-5.sh
```

- `chmod` changes filesystem permissions; `+x` adds executable permission to `run-5.sh`. It changes the file once but does not run it.
- `./run-5.sh` executes the file named `run-5.sh` in the current directory. The `./` is required because the current directory is normally not searched automatically for commands.

The actual course script expands to this job configuration:

| Script argument | Meaning |
|---|---|
| `hadoop jar /usr/lib/hadoop/hadoop-streaming.jar` | Launch the Hadoop Streaming job runner. |
| `-D mapred.reduce.tasks=3` | Request three reducer tasks, normally producing three reducer `part-*` files. |
| `-file ./mapper.py` / `-file ./reducer.py` | Distribute the Python programs to the task machines. |
| `-mapper ./mapper.py` | Use `mapper.py` as the mapper command. |
| `-reducer ./reducer.py` | Use `reducer.py` as the reducer command. |
| `-input /3littlepigs.txt` | Read the input file from HDFS, not from the master's local directory. |
| `-output /output` | Write the job result into the HDFS `/output` directory. |

The trailing `\` on each script line means the shell command continues on the next line. Run both commands from the EMR master's directory containing all three scripts, normally `~/w3`. The HDFS input must already exist, and `/output` must not already exist.

### Combiner and in-mapper combining

A **combiner** performs optional local aggregation after mapping, reducing network traffic. It is an optimisation: Hadoop may execute it zero, one, or multiple times, so correctness must not depend on it running exactly once.

Safe combining requires an operation that can be repeatedly regrouped, such as sum, minimum or maximum. A direct average is unsafe because “average of averages” is generally wrong. Carry `(sum, count)` instead and calculate `total_sum / total_count` at the end.

There is also a type/shape invariant: because the combiner may run zero times, mapper output must already be valid reducer input. For a mean, emit `(value, 1)` from the mapper; the combiner and reducer can both merge pairs as `(sum₁ + sum₂, count₁ + count₂)`, and only the final reducer divides total sum by total count.

> **Exam pattern: "is this mapper correct?"** A mapper that emits `<taxi_id, charge>` is fine for a reducer-only average, but **wrong once a combiner is required**. If the combiner averages raw charges, the reducer averages averages: taxi `132` with charges `15, 33` on mapper A and `30` on mapper B gives `(24 + 30) / 2 = 27`, but the true mean is `78 / 3 = 26`. If the combiner instead emits `(sum, count)`, the reducer receives a mix of bare charges (where the combiner did not run) and pairs. Fix: the mapper emits `<taxi_id, (charge, 1)>`; the combiner sums both fields and emits the same shape; only the reducer divides. Also mention robustness: skip blank or malformed lines and parse the charge as a number, otherwise one bad line in 10 TB crashes the task.

| Stage | Consumes | Emits |
|---|---|---|
| Mapper | `<offset, "taxi_id\tcharge">` | `<taxi_id, (charge, 1)>` |
| Combiner (0..n times) | `<taxi_id, [(s, c), ...]>` | `<taxi_id, (Σs, Σc)>` |
| Reducer | `<taxi_id, [(s, c), ...]>` | `<taxi_id, Σs / Σc>` |

**In-mapper combining** aggregates within the mapper itself before emitting. It provides more control and can reduce output further, but its state consumes memory. State preserved across the entire input split is more efficient than rebuilding it for every line, but it must remain bounded enough to fit in memory.

### Iterative MapReduce and exact weighted aggregation

Some algorithms repeatedly alternate a parallel data-processing step with a small control decision. Hadoop MapReduce does not automatically feed a job's output back into itself, so a lightweight **driver** can run one job per iteration:

```text
small iteration state (for example, k medoids)
    ↓ distributed to mappers
map: assign each record and emit a keyed partial
    ↓ partition + shuffle + sort
reduce: aggregate each group and emit a small summary
    ↓ HDFS intermediate output
driver: read only the summaries, update state, test convergence
    ↺ next job, or publish final HDFS output
```

The full dataset stays in HDFS and is processed line by line by distributed tasks. The driver should read only bounded control data—such as `k` cluster summaries—not collect all records into local memory. Each iteration needs a distinct HDFS output path because Hadoop will not overwrite an existing directory; intermediate paths should stay outside the assessed/final output and be cleaned deliberately.

Repeated identical records can sometimes be compressed **exactly**, not approximately. Suppose a point `p` occurs `wₚ` times in one cluster. A mapper can emit `(cluster, p, partial_count)` rather than one record per occurrence. The reducer merges counts and calculates a candidate point `o`'s average Euclidean dissimilarity as:

```text
Σₚ [wₚ × distance(o,p)] / Σₚ wₚ
```

This produces the same result as expanding every duplicate, while reducing shuffle records and repeated distance calculations. If the number of distinct mapper keys may be large, periodically flush and clear the in-mapper dictionary; reducers can safely add multiple partial counts.

An iterative clustering pattern can use:

```text
Mapper input:     one raw data record
Mapper output:    (cluster_id, point, partial_count)
Shuffle:          all weighted points for one cluster reach one reducer
Reducer input:    cluster_id with its point/count records
Reducer output:   (cluster_id, new_representative, count, cost, assignment_signature)
Final output:     one bounded summary per cluster
```

A deterministic signature of each cluster's sorted `(point, count)` membership lets the driver test whether assignments changed without retrieving every assignment. Exact PAM/k-medoids still requires evaluating every distinct assigned point as a candidate medoid, so its update is quadratic in the number of **distinct** points per cluster; weighted duplicate aggregation reduces that number when coordinates repeat but does not change the algorithm.

### Week 3 practical flow

The lab crossed three distinct storage boundaries and then submitted distributed work:

```text
Windows local disk
  Week 3/w3/{mapper.py,reducer.py,run-5.sh,3littlepigs.txt}
          │ scp -r (SSH file transfer)
          ▼
jumphost local disk (/home/ec2-user/w3)
          │ scp -r, or bypassed by local ProxyJump transfer
          ▼
EMR master local disk (/home/hadoop/w3)
          │ hadoop fs -put 3littlepigs.txt /
          ▼
HDFS (/3littlepigs.txt distributed as blocks on cluster storage)
          │ ./run-5.sh submits a Hadoop Streaming job to YARN
          ▼
HDFS (/output/part-00000 ... part-00002 and _SUCCESS)
          │ hadoop fs -getmerge
          ▼
EMR master local disk (merged_output.txt)
```

1. **Provision:** from the jumphost, `./create_cluster.sh` provisioned the EMR cluster. `aws emr list-clusters --active --region us-east-1` identified the cluster and its state; `WAITING` meant it was ready and still running.
2. **Stage locally:** the four lab files were grouped in the local `w3` directory. The Python files define computation, `run-5.sh` defines job configuration, and the text file is data.
3. **Transfer:** `scp -r` copied ordinary files over SSH. In the guide this is Windows → jumphost → EMR master; the configured `bdp-emr` `ProxyJump` also permits Windows → EMR through the jumphost in one command. This stage does **not** place anything in HDFS.
4. **Ingest:** on the EMR master, `hadoop fs -put 3littlepigs.txt /` copied the input from the master's local disk into HDFS as `/3littlepigs.txt`. `hadoop fs -ls /` verified the HDFS path.
5. **Submit:** `chmod +x run-5.sh` granted Unix execute permission. `./run-5.sh` invoked the cluster's Streaming JAR, distributed the mapper/reducer executables to task containers, requested three reducers, selected HDFS input `/3littlepigs.txt`, and reserved HDFS output `/output`.
6. **Execute:** InputFormat/splits/RecordReaders fed lines to parallel mapper tasks. Mapper stdout became intermediate `word\t1` records. Hadoop partitioned by key, shuffled records to reducers, and sorted/grouped equal words. Each reducer summed a stream of one key at a time.
7. **Materialise and inspect:** OutputFormat wrote one HDFS `part-*` file per reducer plus `_SUCCESS`. `hadoop fs -ls /output` inspected directory metadata; `hadoop fs -cat '/output/part-*'` streamed all result records to the terminal.
8. **Export if needed:** `hadoop fs -getmerge '/output/part-*' merged_output.txt` concatenated HDFS parts into one ordinary file on the EMR master's local disk. It did not create another HDFS file.
9. **Rerun/cleanup:** Hadoop never overwrites an existing output directory, so a deliberate rerun requires a new output path or `hadoop fs -rm -r /output`. Once useful files are saved, return to the jumphost and run `./terminate_cluster.sh` to stop the billable cluster.

> [!IMPORTANT]
> The same-looking `/` has different meanings depending on the command. `ls /` addresses the Linux filesystem of the current machine; `hadoop fs -ls /` addresses the HDFS root. `scp` transfers ordinary host files, whereas `hadoop fs -put/-get` crosses between the EMR master's local filesystem and HDFS.

#### Cluster readiness and inspection

On the local Windows machine, open PowerShell and connect using the configured alias:

```powershell
ssh bdp-jump
```

The prompt should change to the jumphost's `ec2-user` account. Then start provisioning from the jumphost:

```bash
./create_cluster.sh
```

Starting the script does not mean the cluster is immediately ready. If the script does not itself wait and report readiness, check the state from the jumphost:

```bash
aws emr list-clusters --active --region us-east-1
```

Find the cluster ID in that output, then inspect one cluster in detail:

```bash
aws emr describe-cluster --cluster-id j-XXXXXXXXXXXXX --region us-east-1
```

Wait for `State: WAITING` before connecting to the EMR master or submitting work. `WAITING` means ready for steps, not stopped.

> [!IMPORTANT]
> Keep the jumphost session open if convenient. A cluster in `WAITING` is ready but still billable, so terminate it from the jumphost with `./terminate_cluster.sh` when the practical is finished.

Current workspace note: the local `Week 3/w3` folder contains all four required files: `mapper.py`, `reducer.py`, `run-5.sh`, and `3littlepigs.txt`.

### Active recall — Week 3

1. What do InputFormat, an input split, and RecordReader contribute before the mapper runs?
2. For `pig wolf pig`, what does WordCount emit and what happens before the reducer receives it?
3. How do data locality, speculative execution, and key skew affect execution?
4. How can weighted duplicate aggregation and a small driver make iterative clustering exact and scalable?
5. In the lab, how did data move from Windows to HDFS input and finally to reducer output?
6. Why is a mapper that emits `<taxi_id, charge>` wrong for a per-taxi average that must use a combiner?

<details>
<summary>Show answers</summary>

1. InputFormat selects/defines input records and logical splits; a split describes one mapper's logical work; RecordReader converts its bytes into mapper `(k1, v1)` records.
2. The mapper emits `(pig, 1)`, `(wolf, 1)`, `(pig, 1)`. Hadoop partitions, shuffles, sorts, and groups by key, giving reducer groups equivalent to `(pig, [1,1])` and `(wolf, [1])`.
3. Data locality places map work near HDFS blocks to avoid network transfer. Speculative execution can duplicate an abnormally slow attempt, but key skew gives one reducer genuinely more work and requires a partitioning/algorithm fix.
4. Emit `(group, item, partial_count)` so duplicates are represented by weights; compute weighted sums/costs in the reducer. A driver reads only bounded group summaries, updates the small iteration state, and launches another job. Periodic mapper flushing bounds memory, and assignment signatures allow convergence testing without collecting all assignments.
5. `scp` moved ordinary files Windows → jumphost/EMR master; `hadoop fs -put` ingested the text into HDFS; Streaming processed it; OutputFormat wrote three HDFS `part-*` files; `-getmerge` optionally exported them to one master-local file.
6. The combiner may run zero or many times, so its output must match mapper output and reducer input. Averaging bare charges gives an average of averages; emit `(charge, 1)`, sum `(sum, count)` in the combiner, and divide only in the reducer.

</details>

---

## Week 4 — Design patterns, composite keys, joins, and multi-job pipelines

### Pairs and stripes

The Week 4 co-occurrence example shows two recurring ways to represent relationships:

| Pattern | Mapper output | Strength | Main cost/risk |
|---|---|---|---|
| **Pairs** | `((item, neighbour), count)` | Simple records; easy to combine and distribute. | Many intermediate records and more shuffle overhead. |
| **Stripes** | `(item, {neighbour: count, ...})` | Locally aggregates a whole neighbourhood and reduces emitted records. | Associative arrays can grow large and serialization is more complex. |

Both require merge operations that are associative and commutative if a combiner may run. Pairs usually scale better when individual neighbourhoods are huge; stripes can be much faster when each stripe remains safely bounded.

### Composite keys: separate partitioning from sorting

A mapper can emit a key with several tab-separated fields. These settings control different responsibilities:

```text
composite key = (primary_group, secondary_order, optional_tie_breaker)
```

| Setting | Responsibility |
|---|---|
| `stream.num.map.output.key.fields=N` | Treat the first `N` fields as the Streaming key. |
| `KeyFieldBasedPartitioner` with `-k1,1` | Route records using only field 1, keeping one primary group on one reducer. |
| `KeyFieldBasedComparator` | Sort composite keys inside each reducer partition. |
| Comparator options such as `-k2,2nr` | Select field 2, numeric (`n`), reverse/descending (`r`). |

Example configuration:

```bash
-D stream.num.map.output.key.fields=2 \
-D mapred.text.key.partitioner.options='-k1,1' \
-D mapred.output.key.comparator.class=org.apache.hadoop.mapred.lib.KeyFieldBasedComparator \
-D mapred.text.key.comparator.options='-k1,1n -k2,2n' \
-partitioner org.apache.hadoop.mapred.lib.KeyFieldBasedPartitioner
```

Partitioning on the primary field and sorting on the complete composite key is the basis of **secondary sort**: all records for one group reach one reducer in a deliberate internal order.

Keep three different operations separate:

- **Partitioning** selects which reducer receives a mapper record. A custom partitioner is useful only when the default hash of the complete key does not match the required grouping.
- **Hadoop shuffle/sort** orders mapper keys before the reducer reads them. Encoding an assessed ordering in the key and comparator is distributed design; manually sorting final output in Bash is not a substitute.
- **Bounded local ordering** such as Python `sorted()` may still be appropriate for a small reducer-local candidate set or deterministic tie-breaking. It must not collect or globally sort the full Big Data input in one process.

### Order inversion and streaming reduce-side joins

**Order inversion** converts a sequencing dependency into a sorting problem. Emit a special summary/metadata record whose secondary key sorts before ordinary detail records. The reducer consumes the small prerequisite first, saves it, and streams the later details without buffering the entire group.

For a reduce-side join:

```text
Dataset A mapper: (join_id, 0) → metadata
Dataset B mapper: (join_id, 1) → detail
                       ↓ partition by join_id; sort by (join_id, tag)
Reducer input: metadata first, then all details for that join_id
Reducer state: one metadata record
Reducer output: joined records emitted as details stream past
```

Input: two HDFS datasets with a shared join ID. Mapper output: tagged composite-key records. Shuffle: all equal IDs reach one reducer and tags impose metadata-first order. Reducer input: one sorted ID group. Final output: one joined record per matching detail, plus any explicit marker required for entities with no details.

### Chaining jobs through HDFS

A multi-job design must specify exact interfaces, not merely say that one job feeds another:

```text
Job 1 reducer output format
    ↓ HDFS intermediate directory A
Job 2 mapper input format and transformation
    ↓ HDFS intermediate directory B
Job 3 mapper input and final transformation
    ↓ required HDFS final directory
```

Each output directory must be new, every job must ship its own mapper/reducer executables and reducer-count settings, and intermediate paths should remain outside the assessed final directory. Cleanup happens only after downstream success.

A common three-job analytical pipeline is:

1. **Join:** attach dimension/metadata fields to fact records using a shared ID.
2. **Aggregate:** use in-mapper partials and a reducer keyed by the required entity to calculate counts, sums, distinct ordered entities, and derived averages.
3. **Sort:** encode the sort criterion into the mapper key and use a numeric/reverse comparator rather than a shell post-processing sort.

### Why multiple sorted parts are not automatically globally sorted

A comparator sorts only **within each reducer partition**. If records are hash-partitioned across three reducers, concatenating their individually sorted parts is not necessarily a global order.

The 2026 Assignment 1 marking feedback explicitly rejected **replicated-summary rank slicing**:

```text
one company summary
    ↓ mapper emits it once with a range/bucket key
Hadoop partitioner selects exactly one reducer
    ↓ comparator sorts that reducer's assigned range
reducer streams its already sorted records and emits them directly
```

Sending every summary to all three reducers is the opposite of dividing the data: each reducer receives 100% of the company table, buffers it, calculates its own rank slice, and discards the other two thirds. The aggregated table is smaller than the raw trip data, but the assignment gives no bound on the number of companies. Therefore neither full replication nor `records = []` is a scalable Big Data design for this task.

For a globally ordered three-part result, the partition keys or ranges must also preserve cross-part order: reducer 0 receives the highest range, reducer 1 the middle range, and reducer 2 the lowest range. The exact range scheme must be one permitted by the course and documented in the work log. A reducer should not reconstruct the global ranking and decide after the shuffle which subsection it wishes to keep; Hadoop's partitioning decision must already have assigned it a disjoint portion.

The course `KeyFieldBasedPartitioner` hashes only the selected key fields. Its implementation starts the selected-field hash at zero and uses non-negative hash modulo the reducer count, which is useful when deliberately designing bucket keys. See the [Apache Hadoop source](https://hadoop.apache.org/docs/r2.6.0/api/src-html/org/apache/hadoop/mapreduce/lib/partition/KeyFieldBasedPartitioner.html).

### Assignment readiness is a multi-layer gate

An implementation is not submission-ready merely because all mapper and reducer files exist. Verify four separate layers:

| Gate | Evidence required | Typical hidden failure |
|---|---|---|
| Algorithm and format | Independent calculation agrees with every final field, row count, ordering rule, and decimal format. | Correct totals but wrong field order, trip boundary, distinct count, or global ordering. |
| Distributed execution | The end-to-end shell entry point succeeds on the specified EMR cluster with the required reducer count on every job. | Local `mapper → sort → reducer` succeeds, but Streaming options, execute permissions, JAR paths, or HDFS cleanup fail. |
| Design explanation | Section 2 visibly traces each task in numbered stages: mapper input, emitted `<key, value>` pair, partition/shuffle/sort rule, reducer input/output, and exact inter-job path/format. | Good code exists only in a separate walkthrough; the required work-log section is absent, uses unlabelled record strings, or merely says one job feeds another. |
| Submission package | The flat ZIP, standalone Turnitin code PDF, and work-log DOC exist with the required individual/group names. | Task folders and explanations exist, but the three assessed upload artifacts do not. |

The verified postgraduate Assignment 1 run illustrates these gates:

- **Task 1:** the mapper converts each fare to integer cents with explicit half-up rounding, performs in-mapper partial aggregation, and emits count/max/min/sum in cents. The reducer merges only integers and applies `Decimal` half-up rounding once to the final average, so mapper split boundaries cannot alter the last displayed cent. The EMR result contained all `1,436` expected `(taxi, trip_type)` groups, totalled `30,000` trips, used six fields per row, and matched an independent calculation.
- **Task 2:** the real EMR driver converged after five iterations. The final cluster counts were `14,576`, `9,181`, and `6,243`, summing to all `30,000` valid trips; the final average dissimilarities were `24.68`, `20.85`, and `17.82`. The driver removed temporary HDFS iterations after publishing `/Output/task2`.
- **Task 3:** the real three-job EMR pipeline emitted `19` company rows across reducer parts of `6/6/7` rows. Fleet sizes summed to all `500` taxis, trip totals summed to `30,000`, and concatenating `part-00000` through `part-00002` was globally descending by revenue. An exact-decimal audit exposed one important edge case: company 0 has `356194.37 / 34 = 10476.305`, so the current float aggregation emitted `10476.30` while explicit half-up rounding gives `10476.31`. The specification requires two decimals but gives no tie rule; integer cents plus one documented decimal-rounding rule eliminates split/order-dependent last-cent behaviour.
- **Submission packaging:** the individual upload set is format-complete. The flat source archive contains the required source/configuration files at its top level; the standalone code PDF contains only the Python and Bash source requested for plagiarism checking; and the separate work log contains the three required sections, with Section 2 focused on mapper/reducer data flow and design reasoning. Internal QA logs, checksums, output dumps, and cluster-lifecycle notes are retained privately rather than added to assessed documents. All three assessed files use the `s4271512_PG` filename base and remain separate uploads. Packaging completeness does not remove the Task 3 half-cent design decision identified above.
- **Work-log Section 3:** keep the Submission Declaration Checklist in the submitted DOC. The specification explicitly says to double-check all three work-log sections and use this checklist to verify the submission. It is required submission structure, not an internal project-status report. For an individual submission, only the Section 1 member-contribution content is not applicable; the work log itself and its other required sections remain compulsory.
- **Artifact version control:** preserve the previous PDF and DOC outside the assessed folder before testing a redesign. Keep each candidate set in its own clearly named directory, render every page of the PDF and the actual submitted Word format, and copy only the chosen pair into the three-file submission folder. This prevents a visual revision from silently changing content or adding extra upload files.

> [!IMPORTANT]
> A local replay is strong algorithmic evidence, not proof that a Hadoop submission will run. Final acceptance requires the actual `./taskN-run.sh` command on the RMIT EMR environment, inspection of the exact HDFS output path, preservation of verification evidence, and termination of the cluster when finished.

The marking guide's highest bands require more than plausible output:

| Rubric area | Top-band evidence |
|---|---|
| Task 1 (`5/5`) | Correct output, no code/script error, clear comments, required state-preserving in-mapper combining, exact six-field format, and working three-reducer script. |
| Task 2 (`9-10/10`) | Correct PAM mapper/reducer, dynamic `k` and `v`, three reducers per iteration, correct parameter/model distribution, convergence/iteration-limit control, required stdout, clean HDFS intermediates, and clear comments. |
| Task 3 (`9-10/10`) | Correct three-job join/aggregation/sort pipeline, exactly three reducers per job, no shell final sort or `TotalOrderPartitioner`, exact six-field global revenue order, and clear comments. |
| Functional/format penalties | Avoid poor style/comments; submit separately named DOC, PDF, and flat ZIP; use exact script names and case-sensitive HDFS paths. |

### Assignment FAQ clarifications

- Local mapper/reducer success does not prove distributed execution. For debugging, first run a map-only job with `-D mapred.reduce.tasks=0`, inspect mapper output, then restore the reducer and test its logic in small blocks.
- Streaming exit code `127` can be caused by Windows CRLF line endings. On the EMR master, `dos2unix` converts files to Linux LF; the FAQ states that markers perform their own `chmod +x *.sh` and `dos2unix *`, so these setup commands do not belong in the submitted solution.
- Task 1 may use a list or dictionary for in-mapper combining, provided state is preserved across input lines and the aggregated `<key, value>` pairs are emitted after the mapper finishes reading its split.
- A stale hidden `.crc` file created by `copyToLocal` can cause a local `ChecksumException` after that file is modified. Confirm the exact matching hidden CRC file before removing it, then retry the copy.
- No README or raw `Taxis.txt`/`Trips.txt` belongs in the submission. Each `taskN-run.sh` must be self-contained, the HDFS inputs are assumed to exist at the specified paths, and all required source/configuration files must sit at the ZIP root with no subfolders.

### Active recall — Week 4

1. How do the pairs and stripes approaches trade shuffle volume against mapper memory?
2. What is the difference between composite-key partitioning and comparison?
3. How does order inversion let a reducer stream a reduce-side join?
4. What four evidence gates distinguish code-complete from submission-ready work?
5. Why do three revenue-sorted reducer parts not imply global sorting, and why was full-table replication rejected in Assignment 1?

<details>
<summary>Show answers</summary>

1. Pairs emit many small records and use little per-record state; stripes locally combine a neighbourhood into an associative array, reducing records but risking large in-memory structures.
2. The partitioner selects the reducer, often from the primary field; the comparator orders records inside that partition, potentially using secondary numeric/reverse fields.
3. Tag metadata with a secondary key that sorts before detail records while partitioning both by the join ID. The reducer stores one metadata value, then immediately emits joined details as they arrive.
4. Verify algorithm/output, real distributed execution, complete data-flow explanation, and the required final upload package. For chained jobs, the explanation must state every mapper/reducer interface, shuffle rule, intermediate path, and next-stage parser.
5. Comparators sort only within partitions, while hash partitions have no cross-partition range order. Assignment 1 required Hadoop to distribute disjoint portions among the reducers; replicating the complete company table made every reducer buffer all summaries and manually discard two thirds, so it did not demonstrate scalable partitioning.

</details>

---

## Week 5 — Clustering, K-means, and programming iterative MapReduce jobs

### What changed from Week 4

Week 4 was mainly about designing one MapReduce job: choose an intermediate key, control partitioning and ordering, and aggregate related records. Week 5 adds a second kind of problem:

- **Clustering:** group similar points/items when no class labels are supplied.
- **Iteration:** one MapReduce job updates a small model/state, then the next job uses that updated state.
- **Programming on a cluster:** separate the driver/control logic from the mapper and reducer that process the large dataset.

The Week 5 lab also applies Week 4's pairs/stripes patterns to a concrete text problem and then adds a denominator calculation for relative frequencies.

### Clustering and similarity

Clustering arranges items into groups so that items within a group are more similar than items in different groups. It is subjective until a representation and a similarity/distance measure are chosen. Typical applications include document/topic grouping, customer segmentation, image grouping, and anomaly detection.

For numeric vectors, common measures are:

| Measure | Core idea | Important property |
|---|---|---|
| Euclidean distance / L2 norm | Straight-line distance between vectors | Sensitive to scale; smaller means closer |
| Manhattan distance / L1 norm | Sum of absolute coordinate differences | Often more robust to individual large deviations |
| Cosine similarity | Angle between vectors, `x·y / (||x|| ||y||)` | Focuses on direction rather than magnitude; identical direction gives 1 |
| Jaccard similarity | `|A ∩ B| / |A ∪ B|` for sets | Ranges from 0 (no overlap) to 1 (same set) |

Always state whether a larger value means “more similar” or “more distant.” A clustering algorithm that chooses a minimum distance cannot directly use a similarity score without converting the rule.

### Hierarchical agglomerative clustering (HAC)

HAC starts with one cluster per item. Repeatedly, it merges the two closest clusters until one cluster remains or the requested stopping level is reached. The result can be visualised as a dendrogram and cut to obtain a chosen number of clusters.

The answer depends on how cluster-to-cluster similarity is defined:

- **Single-link:** similarity is based on the closest pair across the two clusters. It can create long, “straggly” chains.
- **Complete-link:** similarity is based on the furthest pair. It tends to produce tighter, more spherical clusters.
- Other linkage choices are possible; the linkage rule is part of the algorithm, not a cosmetic detail.

HAC is useful conceptually, but repeatedly comparing and merging clusters is expensive for very large data. Week 5 therefore focuses on K-means as the MapReduce-friendly iterative algorithm.

### K-means and Lloyd’s algorithm

K-means takes:

1. A dataset of points/vectors `x`.
2. A chosen number of clusters `k`.
3. An initial location for each of the `k` centroids.
4. A distance measure, normally Euclidean distance in the lecture example.

Its objective is to minimise the total squared distance from each point to its assigned centroid:

```text
Φ(X, C) = Σ over points x of [distance(x, nearest centroid)^2]
```

Lloyd’s algorithm repeats two alternating steps:

```text
assign:  each point → nearest current centroid
update:  each centroid → mean of the points assigned to it
```

It stops when the centroid locations no longer change (or when an implementation's tolerance/iteration limit says to stop). The result is not guaranteed to be the globally best clustering: different initial seeds can lead to different local optima. Empty clusters also need an explicit policy, such as retaining/reinitialising the centroid; the supplied case-study material does not specify a universal policy, so verify the implementation requirement if assessed.

### Choosing `k`

The correct number of clusters is generally an unsolved problem. The lecture demonstrates the **elbow/knee method**:

1. Run K-means for several values of `k`.
2. Compute the objective value for each `k`.
3. Plot objective against `k`.
4. Look for a sharp improvement followed by diminishing returns.

The elbow is evidence for a useful `k`, not a proof that it is the only correct answer.

### K-means as MapReduce

The dataset is large, but the current centroid list is small (`k` vectors). Keep the large point file in HDFS and distribute the small centroid state to every mapper for each iteration.

```text
driver loads current k centroids
        │ broadcast through job configuration/local file
        ▼
mapper reads one point at a time
        │ finds nearest centroid
        │ emits (cluster_id, point[, weight])
        ▼
shuffle groups all assigned points by cluster_id
        ▼
reducer sums coordinates and counts points
        │ computes mean for each cluster
        ▼
driver reads only k new centroids
        │ compares old/new centroids
        └── repeat until convergence
```

Representative data flow:

| Stage | Input | Emitted/received data | Purpose |
|---|---|---|---|
| Driver | Current centroid file | Small state for all mappers | Make the model available for this iteration |
| Mapper | One point `p` | `(nearest_cluster, p)` | Assign the point to its closest centroid |
| Shuffle/sort | Mapper pairs | All points for a cluster together | Make each reducer responsible for complete cluster totals |
| Reducer | `cluster_id, [p1, p2, ...]` | `(cluster_id, new_mean)` | Sum each dimension and divide by the number of points |
| Driver | One result per cluster | Next centroid state/convergence decision | Launch another iteration or publish final output |

The lecture extends each point with a final coordinate containing `1`:

```text
(x, y) → (x, y, 1)
```

The reducer can then sum vectors component-wise. The first two sums are coordinate totals and the last sum is the point count; divide the coordinate totals by the count to obtain the new centroid. This is a convenient aggregation trick, not an extra geometric dimension.

**In-mapper combining** reduces shuffle traffic by maintaining a local partial sum/count for each cluster and emitting one partial record per cluster (or flushing periodically). The reducer must still merge partials from every mapper. If duplicate points are compressed, carry their occurrence count as a weight; otherwise the mean and cluster size will be wrong.

### Parameters versus auxiliary model files

Use job parameters for a few small scalar controls, such as a reducer count or a fixed threshold. Use Hadoop Streaming's `-file` mechanism when every mapper needs a structured, changing model such as a centroid or medoid list:

```text
initialization file -> driver reads iteration limit and initial model
driver writes current model file -> Streaming -file localises it on mapper nodes
mapper opens local model file -> assigns each input point
reducer summaries -> driver creates the next model file
```

This does not pass the raw dataset through the driver. The large dataset remains in HDFS; only the small model is distributed with each job. For the assignment's PAM task, the auxiliary medoid file is therefore the correct pattern, while replacing it with many command-line arguments would make structured, iteration-dependent state harder to validate and maintain.

### Why the driver must stay small

“No memory” is not a literal MapReduce rule. Split-local aggregates, a small broadcast model, one metadata record, or one reducer group's required state are legitimate. The real warning is against state that can grow with the complete raw dataset without a justified bound or partition.

The driver controls iterations but must not read the entire dataset into memory. It should read only bounded summaries—normally one centroid and count per cluster—while HDFS and the workers retain the full point data. Each iteration needs a unique intermediate output directory because Hadoop refuses to overwrite an existing output path.

The reducer count does not have to be one. Multiple reducers are normally desirable: the cluster ID is the key, so all points assigned to the same cluster go to one reducer, while different clusters can be processed in parallel. Set the required reducer count for every iteration job, not just the first one.

### Assignment 1 marking lessons for iterative control and final output

A lightweight Python driver that reads only `k` summaries can be a valid general iterative-system pattern. The 2026 Assignment 1 marker nevertheless expected the iteration loop, Hadoop Streaming commands, stopping condition, HDFS paths, and explicit failure handling to remain visible in `task2-run.sh`. The published brief required `task2-run.sh` to run the task end to end but did not explicitly say that a Python subprocess driver was forbidden. This distinction matters for a remark, but for future assessed work the safest course-specific implementation is to keep the control loop directly in Bash unless written guidance permits another driver layer.

The marker also expected the last converged MapReduce iteration to write the exact four-field result directly to `/Output/task2`. Creating a local text file afterwards and uploading it as `/Output/task2/part-00000` was rejected because the assessed final file was then produced by client-side post-processing rather than by the final MapReduce job. Design the intermediate output so any convergence-only metadata remains separate from the exact assessed output fields.

PAM medoids are real input points. Preserve their original coordinate representation where practical; do not force `%.3f` padding unless the specification requires three decimal places. The brief required two decimals for average dissimilarity but did not state a fixed number of decimal places for medoid coordinates.

`set -euo pipefail` is a common defensive Bash mode, not automatically a program error. In this assessment the marker preferred explicit handling of important exit codes because strict mode can terminate on an expected non-zero command, an unset variable, or a failing pipeline component. If strict mode is used in assessed work, every possibly expected non-zero status must be handled deliberately; otherwise follow the course's explicit-check pattern.

The final 2026 Assignment 1 marking applied a separate **one-point functional penalty** solely for this strict-mode line. In the submitted `task1-run.sh`, `task2-run.sh`, and `task3-run.sh`, however, there is no shell pipeline, no reference to an intentionally unset variable, and no command whose non-zero result is documented as an expected control condition. `pipefail` therefore has no practical effect in these scripts, `-u` protects only already-defined variables, and `-e` stops after a real setup or job failure instead of allowing later commands to create misleading output. Because the published functional requirements require good style and clear comments but do not prohibit strict mode, a deduction based only on hypothetical fragility is contestable unless the marker can identify a concrete submitted command that should have been allowed to fail.

### Week 5 lab — co-occurrence matrix with pairs

The lab input is `trip.txt`, where each line is a context such as a sentence. For every ordered pair of different words in the same context, the mapper emits one occurrence:

```text
Input:  I am a student
Emits:  (I, am, 1), (I, a, 1), ..., (student, I, 1), ...
```

The supplied pair mapper uses nested loops over `word1` and `word2` and skips `word1 == word2`. Thus pairs are **ordered**: `(I, am)` and `(am, I)` are separate cells. Unless the assignment says otherwise, repeated words can create repeated pair emissions and should not be silently deduplicated.

The mapper prints three tab-separated fields: `left_word`, `right_word`, `1`. With `stream.num.map.output.key.fields=2`, the first two fields form the composite key. The reducer receives one key pair and all its counts, sums them, and emits:

```text
(left_word, right_word, total_cooccurrences)
```

### Week 5 lab — co-occurrence matrix with stripes

The stripes mapper emits one record per left word and stores its neighbours in the value:

```text
Input:  I am a student
Output: I      am:1, a:1, student:1
```

The key is only the left word, so the default partitioner already sends all stripes for that word to the same reducer. The reducer performs an element-wise merge: counts for the same neighbour are added across incoming stripes. It outputs one row per left word containing a neighbour-to-count map/list.

| Pairs | Stripes |
|---|---|
| Key is `(left, right)` | Key is `left` |
| One emission per pair occurrence | One neighbourhood map per input context/left word |
| Simple reducer: sum values for exact pair | Reducer merges maps element by element |
| More intermediate records and shuffle overhead | Fewer records, but larger mapper/reducer memory and serialization cost |
| Composite-key configuration needed in the lab | Default first-field key is sufficient |

The conceptual matrix is sparse: only observed pairs need to be stored, not an enormous dense `N × N` array full of zeroes.

### Week 5 lab — relative frequencies

The co-occurrence count `N(a,b)` tells how often `a` and `b` appear together. Relative frequency asks how strongly `b` is associated with `a`:

```text
f(b | a) = N(a,b) / N(a,*)
N(a,*) = Σ over neighbours b of N(a,b)
```

For the pairs approach, the mapper emits a special total marker as well as each ordinary pair:

```text
(a, *, 1)      # contributes to N(a,*)
(a, b, 1)      # contributes to N(a,b)
```

The custom partitioner must use only `a` (the left word), otherwise `(a,b1)` and `(a,b2)` might reach different reducers and no reducer can calculate the common denominator. The reducer arranges the `*` record before ordinary neighbours through sorting, stores/uses the denominator, then emits each pair count and its relative frequency (the supplied lab output also displays the denominator).

For stripes, all neighbours for `a` already arrive under one key. The reducer merges the neighbour counts, sums them to obtain `N(a,*)`, then divides every neighbour count by that total. This is why stripes make the denominator calculation especially natural.

### Active recall — Week 5

1. What are the assign and update steps in Lloyd’s K-means algorithm?
2. When should an iterative Streaming job use a parameter or auxiliary file, and where did the Assignment 1 marker expect the iteration control and final output to live?
3. What does the final `1` in an extended point `(x, y, 1)` represent?
4. Why must the relative-frequency pairs job partition on the left word only?
5. When would pairs be safer than stripes, and when are stripes likely to be faster?

<details>
<summary>Show answers</summary>

1. Assign each point to its nearest current centroid; then replace each centroid with the mean of its assigned points. Repeat until convergence.
2. Use parameters for a few scalar controls and `-file` for a structured changing model such as a medoid list. For Assignment 1, the marker expected the loop and stopping logic directly in `task2-run.sh` and the last MapReduce iteration to produce the exact `/Output/task2` result, without a local final-file re-upload.
3. It is a count contribution of one point. Summing it gives the cluster size, which is used to divide coordinate sums and calculate the mean.
4. All `(a,b)` counts need the same denominator `N(a,*)`, so every record with the same left word must reach one reducer.
5. Pairs avoid one potentially huge neighbourhood object; stripes reduce shuffle records and can be faster when each neighbourhood map is safely bounded.

</details>

## Week 6 — MapReduce on large graphs

A graph is a set of vertices and edges. Adjacency matrices make incoming and outgoing links easy to inspect but waste space on sparse graphs; adjacency lists store only each vertex's neighbours and are usually more compact. The lecture applies iterative MapReduce to single-source shortest paths.

For one iteration, each node record carries its current distance and adjacency list. A mapper sends candidate distances `distance(u) + weight(u,v)` to each outgoing neighbour and also preserves the node's adjacency information. Shuffle groups candidates by destination node; the reducer keeps the smallest known distance and the adjacency list, then writes the next graph state. Repeating this relaxation propagates shorter paths until distances stop changing. The Week 6 lab also reinforces the Week 5 K-means loop: assign points to centroids, aggregate coordinate sums and counts, then update centroids.

### Active recall — Week 6

1. When is an adjacency list more compact than an adjacency matrix?
2. What does the mapper emit for a shortest-path iteration?
3. Why must the node's adjacency list survive the reducer?
4. What signals that iterative shortest-path updates have converged?

<details>
<summary>Show answers</summary>

1. For a sparse graph, because the list stores existing edges instead of many zero entries.
2. Candidate distances for its neighbours, plus its own node structure so the graph can be processed again.
3. Later iterations need the outgoing edges to propagate new distance estimates.
4. No node distance changes in another iteration.

</details>

## Week 7 — Pig and Hive on Hadoop

Pig and Hive raise the abstraction above hand-written MapReduce. Hive offers SQL-like HiveQL for warehouse-style tables on HDFS; Pig Latin describes a procedural dataflow. Pig's nested data model includes fields, tuples, bags and maps. A relation is a bag of tuples, so row order is not guaranteed unless a later operation explicitly orders the data.

A typical Pig flow loads a relation with a schema, filters or projects records, groups or joins relations by keys, then stores a result. `GROUP` collects one relation's tuples per key; `COGROUP` groups multiple relations and retains a bag from each; `JOIN` combines matching records. After a join, qualify repeated field names with the input alias (for example, `A::country`) to remove ambiguity. The tutorial uses the Grunt shell for interactive work and Pig scripts for repeatable execution. It refers to `join_task1.pig` and `join_task2.pig`, but those companion source files are not present in this workspace.

### Efficient Pig dataflow: shrink data before expensive steps

Pig compiles each script into MapReduce jobs, so the Big Data question is the same as in Weeks 3-5: how many records and bytes reach each shuffle. The Assignment 2 marking criteria name these design rules explicitly.

| Principle | Pig form | Assignment 2 Task 2 example |
|---|---|---|
| Filter as early as possible | `FILTER` directly after `LOAD`, on every relation that will be joined | Medal and games rows are restricted to `START_YEAR..END_YEAR` before any join |
| Project early; compute once | `FOREACH ... GENERATE` only needed fields | Keep `year, code, gold, total`; silver and bronze are summed, then dropped |
| Load only required datasets | Omit unused `LOAD`s | `population.csv` is not needed for the PG ranking report |
| Small lookup table | `JOIN big BY k, small BY k USING 'replicated'` | Country names: the **last** relation is held in memory; map-side join, no shuffle |
| Join after aggregation when possible | Join a per-group relation after `GROUP` | Host city joins one row per Games instead of one row per medal record |
| Bound each group before a UDF | Nested `FOREACH { ORDER ...; LIMIT n; }` | At most three candidates per ranking reach the Jython UDF |

`TOP(n, column, bag)` compares one column only. When ties need a second key (gold desc, then country code asc), use nested `ORDER ... BY gold DESC, country_code ASC` followed by `LIMIT`. Avoid `GROUP ... ALL` on large data: it sends everything to one reducer, which is the Pig equivalent of the replicated-summary design rejected in Assignment 1.

```text
medal_table.csv → FILTER years → FOREACH (year, code, gold, total) ─┐
countries.csv   → FOREACH (code, name) ── replicated JOIN ──────────┘
    → GROUP BY year → nested ORDER + LIMIT 3 (gold) and (total)
games.csv → FILTER years → FOREACH (year, city) → replicated JOIN (one row per Games)
    → Jython UDF formats one block per Games → ORDER BY year → STORE /Output/task2
```

### Parameters, UDFs and data traps

- **Parameter substitution:** `$START_YEAR` in the script is replaced by `-param START_YEAR=2010`; `%default START_YEAR 0` supplies a value when none is passed. Open bounds such as `0` and `9999` keep the script runnable without restricting the analysed years.
- **Jython UDF:** `REGISTER 'task2.py' USING jython AS task2_udf;` is the first statement; the path is relative to where `pig` is invoked. Pig injects `@outputSchema('report:chararray')`, runs the file as **Jython 2.7** (no f-strings), and passes a bag as a Python list of tuples. EMR ships `/usr/lib/pig/lib/jython-standalone-2.7.0.jar` with Pig 0.17.0.
- **Bags are unordered:** a UDF that depends on order should sort its input itself; `ORDER` guarantees order only for the relation that is stored or dumped.
- **Multi-line report records:** a returned string containing `\n` is written by `PigStorage` as several output lines, so the MapReduce job itself produces the exact pretty-printed file.
- **Windows CSVs:** the Canvas files end each line with `\r\n`, so the last field carries `\r`. `TRIM` it before a numeric cast. A header row casts to `null` and is removed by the numeric year filter.
- **Re-runs:** `STORE` fails if the output directory exists; `rmf /Output/task2` at the start of the script makes repeated runs safe.

### Active recall — Week 7

1. How does Pig Latin differ from HiveQL in the way a job is expressed?
2. When is a replicated join appropriate, and which input is replicated?
3. Why join the host city after grouping instead of before?
4. How do you produce deterministic ranked output when Pig bags are unordered?
5. What goes wrong when the last numeric field of a CRLF CSV is cast directly, and how is it avoided?

<details>
<summary>Show answers</summary>

1. Pig describes a procedural sequence of dataflow steps; HiveQL expresses SQL-like queries over warehouse tables.
2. When one input is small enough to fit in memory, such as a country lookup table. The last relation in the `JOIN` is replicated to every map task, so no shuffle is needed.
3. After grouping there is one row per Games, so the join processes and carries far fewer records than one row per medal record.
4. Order by the full ranking key, including the tie-breaker (for example `gold DESC, country_code ASC`), and let the UDF sort its input bag again before assigning rank numbers.
5. The field ends with `\r`, so the cast can fail or depend on converter behaviour. `TRIM` the field before casting.

</details>

## Week 8 — Mahout, Solr and Storm

Mahout provides scalable machine-learning tools. The lecture's user-based recommender finds users with similar ratings on overlapping products, then uses those similarities to estimate preferences for products a target user has not rated. Recommendations should be checked against known ratings rather than assumed to be accurate.

Solr is a search server that indexes documents for fast queries. Its schema describes searchable fields; queries operate on the index rather than scanning every document directly. Storm handles continuous event streams with a topology: spouts provide input streams, bolts filter or transform records, and bolts can send output to later bolts. The topology is a directed graph of processing steps.

### Active recall — Week 8

1. What evidence makes two users similar in the recommender example?
2. What role does a Solr schema play?
3. What does a Storm spout do, and what does a bolt do?
4. How are Storm processing steps connected?

<details>
<summary>Show answers</summary>

1. They gave similar ratings to some of the same products.
2. It declares the document fields and how they are represented for indexing and querying.
3. A spout supplies stream data; a bolt processes or filters a stream and may emit another stream.
4. As a directed topology whose edges carry streams between processing components.

</details>

## Week 9 — Spark and RDDs

A Spark application has a driver that creates the Spark context and executors that run tasks on worker nodes. Spark can run standalone or use a cluster manager such as YARN. An RDD is an immutable, partitioned collection that can be created from an in-memory collection or external storage such as HDFS; lineage lets Spark recompute lost partitions.

RDD transformations such as `map`, `flatMap` and `filter` are lazy and build a computation graph. Narrow transformations use data from their own parent partition; wide transformations need data from multiple partitions and may trigger a shuffle. An action such as `count`, `collect` or saving output starts the pending work and returns a value to the driver or writes to external storage. This is a different toolchain from Assignment 2's Pig/Jython task.

### Active recall — Week 9

1. What work does the driver do, and what work do executors do?
2. Why are RDD transformations called lazy?
3. What makes a transformation wide?
4. What starts execution of a pending RDD computation?

<details>
<summary>Show answers</summary>

1. The driver coordinates the application and builds the Spark context; executors run tasks and hold partition data.
2. They describe new RDDs without immediately running the computation.
3. A result partition needs data from multiple parent partitions, usually requiring a shuffle.
4. An action such as `count`, `collect` or saving the result.

</details>

## Week 10 — Spark Streaming: DStreams, file streams and state

The lab builds a Scala/Maven executable JAR, uploads it to an EMR master, then connects a Spark Streaming word counter to a text server such as Netcat. The supplied example uses one-second batches: each newline-delimited input line is split into words, each word emits `(word, 1)`, and `reduceByKey` groups equal words across the batch and sums their counts. This key grouping may shuffle data; `print()` writes the batch counts to the driver console, with no promised output order. The Week 10 broadcast and accumulator examples are marked selective material.

### A DStream is one RDD per batch

A `StreamingContext(conf, Seconds(n))` cuts the input into batch intervals. A **DStream** is the sequence of RDDs, one per interval. A DStream transformation such as `map` or `reduceByKey` is applied to every batch RDD, so per-batch logic is ordinary RDD logic.

`foreachRDD` is the general **output operation**. Its body runs on the **driver** once per batch and receives that batch's RDD. Driver-side decisions belong there: skip an empty RDD with `rdd.isEmpty()`, or choose the next output folder. RDD actions called inside it, such as `saveAsTextFile`, still run on the executors.

### Reading new files from HDFS

`ssc.textFileStream(dir)`, or `ssc.fileStream[LongWritable, Text, TextInputFormat](dir, filter, newFilesOnly = true)`, lists the directory every batch. It reads only files whose modification time is newer than the start of the stream. Files present before `ssc.start()` are ignored, so a test must add files while the job runs.

`hadoop fs -put` first writes `name._COPYING_` and then renames it. A `fileStream` path filter that rejects `._COPYING_` names ensures each file is read once, complete.

### Stateful processing with `updateStateByKey`

| | Per-batch (`reduceByKey`) | Stateful (`updateStateByKey`) |
|---|---|---|
| Memory | only the current batch | one state value per key since the start |
| Function | `(V, V) => V` | `(Seq[V], Option[S]) => Option[S]` |
| Called for | keys in this batch | every key in the state **or** in this batch |
| Needs | nothing | `ssc.checkpoint(dir)` |

For a key that did not occur in the batch, the function receives an empty `Seq`. Returning `None` removes the key. The state RDD's lineage grows every batch, so Spark checkpoints it to HDFS periodically. The recommended interval is 5–10 × the batch interval, set with `stateStream.checkpoint(Seconds(15))`.

When checkpointing is on, Spark serializes the whole DStream graph. Functions passed to DStreams must therefore be serializable. Do not reference the `StreamingContext` inside `foreachRDD`; use `rdd.sparkContext`.

> **Material gap:** the Week 10 lecture slides (Spark Streaming 1) and all Week 11 material (Spark Streaming 2, the `spark-submit`/HDFS monitoring practical) are not stored locally. This section is based on the Week 10 lab, the A3 brief and the Spark Streaming API.

### Active recall — Week 10

1. What is a DStream, and how does a DStream `map` relate to RDDs?
2. Where does the body of `foreachRDD` run, and why does that matter?
3. Why does a file stream ignore a file that was already in the directory when the job started?
4. When is the `updateStateByKey` function called with an empty `Seq`, and what must be configured before using it?
5. Why should a state stream be checkpointed only every few batches?

<details>
<summary>Show answers</summary>

1. A sequence of RDDs, one per batch interval; the `map` is applied to each batch RDD.
2. On the driver, once per batch. Driver-side state such as output counters can be kept there, and the empty-batch check happens before any output is written.
3. It reads only files whose modification time is newer than the stream's start, so it processes newly arriving files only.
4. For a key that is in the state but did not occur in this batch. `ssc.checkpoint(dir)` must be set.
5. Checkpointing writes the state to HDFS. Doing it every batch is costly, but never doing it lets the lineage grow without bound; 5–10 batch intervals is the usual balance.

</details>

---

# Part II — Condensed lab and exam cheat sheet

## 1. Know where a command runs

| Location | Prompt/user | Purpose |
|---|---|---|
| Local Windows machine | PowerShell | Store/edit files; start SSH/SCP |
| Jumphost | `ec2-user` / `bdp-jump` | Create or terminate EMR |
| EMR master | `hadoop` / `bdp-emr` | Run Hadoop, HDFS and MapReduce |
| HDFS | Accessed using `hadoop fs` | Distributed cluster filesystem, not a terminal machine |

## 2. SSH and EMR lifecycle commands

| Command | Run from | Meaning |
|---|---|---|
| `ssh bdp-jump` | Local | Connect to the RMIT jumphost. |
| `./create_cluster.sh` | Jumphost | Provision the EMR cluster; allow roughly 15 minutes. |
| `aws emr list-clusters --active --region us-east-1` | Jumphost | Show active clusters and their states. |
| `aws emr describe-cluster --cluster-id j-… --region us-east-1` | Jumphost | Show configuration, node groups, timeline, and detailed state for one cluster. |
| `ssh bdp-emr` | Local | Connect through the jumphost to the EMR master. |
| `exit` | Any SSH host | Close that SSH session and return to the previous machine. |
| `./terminate_cluster.sh` | Jumphost | Shut down the billable EMR cluster. Always do this when finished. |

Week 3 startup stopping point:

```text
Windows PowerShell --ssh bdp-jump--> jumphost
jumphost --./create_cluster.sh--> EMR provisioning
EMR state WAITING --> ready; pause before connecting to bdp-emr
```

Configured course identities:

```text
Key:       s4271512-cosc2637.pem
Jumphost:  ec2-user@s4271512.jump.cosc2637.route53.aws.rmit.edu.au
EMR:       hadoop@s4271512.emr.cosc2637.route53.aws.rmit.edu.au
Aliases:   bdp-jump, bdp-emr
```

Optional guide-compatible alias in `C:\Users\samue\.ssh\config`:

```sshconfig
Host bdp-jump jumphost
    HostName s4271512.jump.cosc2637.route53.aws.rmit.edu.au
    User ec2-user
    # Keep the remaining existing jumphost settings unchanged.
```

This permits both `ssh bdp-jump` and `ssh jumphost`; `ProxyJump bdp-jump` can remain unchanged.

New clusters can present a different SSH host key. On the local machine, remove the obsolete entry and reconnect:

```powershell
ssh-keygen -R s4271512.emr.cosc2637.route53.aws.rmit.edu.au
ssh bdp-emr
```

## 3. Secure file copying

Run `scp` from a **local PowerShell terminal**, even if separate terminals are already connected to the jumphost and EMR master. An SSH session does not automatically make the local Windows files visible on the remote machine.

For the current Week 3 folder, the simplest route is directly to the EMR master:

```powershell
cd "C:\Users\samue\Downloads\Big Data Processing\Week 3"
Get-ChildItem .\w3
scp -r ".\w3" bdp-emr:~/
```

The `bdp-emr` SSH configuration uses `ProxyJump bdp-jump`, so this transfer passes through the jumphost automatically. Verify it in the EMR terminal with:

```bash
ls -l ~/w3
```

To follow the course's two-stage route instead, first copy to the jumphost:

```powershell
cd "C:\Users\samue\Downloads\Big Data Processing\Week 3"
scp -r ".\w3" bdp-jump:~/
```

This is the Windows equivalent of the guide's local `scp -r ~/Downloads/w3 jumphost:~/` command. Run it from the parent `Week 3` directory. If the prompt already ends in `\Week 3\w3>`, run `cd ..` first; otherwise `.\w3` incorrectly looks for a nested `w3\w3` directory. Then verify with `ls -l ~/w3` on the jumphost before copying onward to EMR. The configured aliases in this workspace are `bdp-jump` and `bdp-emr`; `jumphost` is only the generic alias shown in the macOS-oriented guide.

> [!TIP]
> A PowerShell `>>` prompt means the command is incomplete, commonly because a quote was opened but not closed. Press `Ctrl+C`, then re-enter the command with the whole space-containing path inside matching quotes. `scp` uses ordinary `-r`; avoid the typographic long dash `–r` found in some formatted notes.

```powershell
scp file.txt bdp-jump:~/
```

Copy a local file to the jumphost home directory.

```powershell
scp -r folder bdp-jump:~/
```

Copy a directory recursively (`-r`).

```powershell
scp ".\Week 3\mapper.py" bdp-emr:~/w3/
```

Copy directly to the EMR master; the SSH configuration automatically jumps through `bdp-jump`.

Traditional two-stage course method, run the second command on the jumphost:

```bash
scp -i s4271512-cosc2637.pem -r w3 \
  hadoop@s4271512.emr.cosc2637.route53.aws.rmit.edu.au:~/
```

`scp` copies between ordinary machine filesystems. It does **not** copy directly into HDFS.

## 4. Essential Unix commands

| Command | Meaning |
|---|---|
| `pwd` | Print the current directory. |
| `ls` / `ls -l` | List files / list with details and permissions. |
| `cd ~/w3` | Change to the `w3` directory under the current user’s home. |
| `mkdir -p ~/w3` | Create the directory; do not fail if it already exists. |
| `cp source destination` | Copy a local file. |
| `mv source destination` | Move or rename a local file. |
| `chmod +x run-5.sh` | Make a shell script executable. |
| `./run-5.sh` | Execute a script from the current directory. |
| `cat file` | Print a local file. |
| `man scp` | Open the manual for a command; press `q` to exit. |

Here, “local file” means local to the machine whose terminal you are using. A file local to the EMR master is still separate from HDFS.

## 5. Essential HDFS commands

| Command | Meaning |
|---|---|
| `hadoop fs -ls /` | List the HDFS root directory. |
| `hadoop fs -mkdir -p /Input` | Create an HDFS directory. |
| `hadoop fs -put file.txt /` | Copy from the EMR master’s local disk into HDFS. |
| `hadoop fs -copyFromLocal file.txt /` | Same basic direction as `-put`. |
| `hadoop fs -get /file.txt ./` | Copy from HDFS to the master node’s local disk. |
| `hadoop fs -copyToLocal /file.txt ./` | Same basic direction as `-get`. |
| `hadoop fs -cat /output/part*` | Print all reducer output parts. |
| `hadoop fs -getmerge /output/part* merged.txt` | Merge HDFS parts into one local file. |
| `hadoop fs -rm /file.txt` | Delete an HDFS file. |
| `hadoop fs -rm -r /output` | Recursively delete an HDFS output directory. |
| `hadoop fs -du -h /` | Show human-readable HDFS space usage. |
| `hadoop fs -count /output` | Count directories, files, and bytes below an HDFS path. |
| `hadoop fs -head /output/part-00000` | Print the first portion of an HDFS file. |
| `hadoop fs -tail /output/part-00000` | Print the last kilobyte of an HDFS file. |
| `hadoop fs -stat '%r' /3littlepigs.txt` | Print the HDFS replication factor (`%r`) for the file. |
| `hadoop fs -setrep -w 3 /3littlepigs.txt` | Request replication factor 3 and wait for it to be reached; cluster capacity still limits placement. |
| `hadoop fs -checksum /3littlepigs.txt` | Display HDFS checksum information for integrity checking. |
| `hadoop fs -df -h /` | Display human-readable HDFS capacity and free space. |

Command anatomy:

```text
hadoop fs -ls /output
│      │  │   └─ absolute HDFS directory produced by the job
│      │  └──── filesystem-shell list operation
│      └─────── Hadoop filesystem shell
└────────────── Hadoop command launcher
```

`fs` selects Hadoop's filesystem command shell; with the cluster configuration used here, paths refer to HDFS. `-ls` lists matching HDFS paths and their metadata rather than printing file contents. An output listing can contain `part-00000`, `part-00001`, and `part-00002`—one data file per reducer—and an empty `_SUCCESS` marker showing that the job completed successfully.

Inspect the output from the EMR master:

```bash
hadoop fs -ls /output
hadoop fs -cat /output/part-00000
hadoop fs -cat /output/part-00001
hadoop fs -cat /output/part-00002
```

Or print all reducer parts in one command:

```bash
hadoop fs -cat '/output/part-*'
```

Here `-cat` streams file contents to the terminal, while `part-*` is an HDFS glob matching every reducer part. `_SUCCESS` contains no WordCount records and does not need to be inspected.

Direction memory aid:

```text
master local disk --put/copyFromLocal--> HDFS
master local disk <--get/copyToLocal---- HDFS
```

Use a normal ASCII hyphen (`-`) in commands. A formatted long dash such as `–put` copied from a PDF will fail.

## 6. Week 3 lab command runbook

### Local Windows PowerShell

Initial staging when the four downloaded files are still loose in one directory:

```powershell
New-Item -ItemType Directory -Path .\w3
Move-Item .\mapper.py, .\reducer.py, .\run-5.sh, .\3littlepigs.txt -Destination .\w3\
Get-ChildItem .\w3
```

For the current workspace, staging is already complete. Transfer the folder with:

```powershell
cd "C:\Users\samue\Downloads\Big Data Processing\Week 3"
Get-ChildItem .\w3
scp -r ".\w3" bdp-jump:~/
```

Configured shortcut that copies directly through the jumphost to EMR:

```powershell
scp -r ".\w3" bdp-emr:~/
```

### Jumphost (`ec2-user`)

```bash
cd
ls -l ~/w3
aws emr list-clusters --active --region us-east-1
aws emr describe-cluster --cluster-id j-XXXXXXXXXXXXX --region us-east-1
```

Course two-stage transfer to EMR:

```bash
chmod 400 s4271512-cosc2637.pem
scp -i s4271512-cosc2637.pem -r ~/w3 \
  hadoop@s4271512.emr.cosc2637.route53.aws.rmit.edu.au:~/
```

When completely finished:

```bash
./terminate_cluster.sh
```

### EMR master (`hadoop`)

```bash
cd ~/w3
pwd
ls -l

hadoop fs -put 3littlepigs.txt /
hadoop fs -ls /

chmod +x run-5.sh
./run-5.sh

hadoop fs -ls /output
hadoop fs -cat '/output/part-*'
hadoop fs -getmerge '/output/part-*' merged_output.txt
cat merged_output.txt
```

For a deliberate rerun with the same output path:

```bash
hadoop fs -rm -r /output
./run-5.sh
```

Only remove `/output` after confirming it is the intended HDFS result directory. The input can remain in HDFS across reruns.

## 7. Week 3 lab files

| File | Role |
|---|---|
| `3littlepigs.txt` | Input data copied into HDFS. |
| `mapper.py` | Reads lines from stdin and emits `word\t1`. |
| `reducer.py` | Reads grouped/sorted pairs and emits `word\ttotal`. |
| `run-5.sh` | Present in `Week 3/w3`; launches the Hadoop Streaming job with three reducers. |
| `/output/part-*` | One HDFS result file per reducer. |
| `merged_output.txt` | Optional merged local copy of all output parts. |

## 8. WordCount code pattern

Mapper:

```python
#!/usr/bin/env python3
import sys

for line in sys.stdin:
    for word in line.strip().split():
        print(f"{word}\t1")
```

Course mapper token-cleaning pattern:

```python
words = line.strip().split(" ")
for word in words:
    word = "".join(c for c in word if c.isalnum())
    if word:
        print(f"{word}\t1")
```

`isalnum()` retains letters/digits; the empty check suppresses punctuation-only tokens. It does not lowercase, so keys remain case-sensitive. `split()` is usually more robust for arbitrary whitespace than `split(" ")`.

Reducer:

```python
#!/usr/bin/env python3
import sys

current_word = None
current_count = 0

for line in sys.stdin:
    word, count = line.strip().split("\t", 1)
    try:
        count = int(count)
    except ValueError:
        continue

    if word == current_word:
        current_count += count
    else:
        if current_word is not None:
            print(f"{current_word}\t{current_count}")
        current_word = word
        current_count = count

if current_word is not None:
    print(f"{current_word}\t{current_count}")
```

Exam description:

```text
Mapper input:    one text line at a time
Mapper output:   (word, 1) for every word occurrence
Framework:       partitions, shuffles, sorts and groups by word
Reducer input:   one word followed by all its counts
Reducer output:  (word, total_count)
```

Execution order:

```text
HDFS input → input splits → mappers → partition/shuffle/sort → reducers → HDFS output
```

Reducer state trace:

```text
pig\t1  → start pig = 1
pig\t1  → pig = 2
wolf\t1 → emit pig\t2; start wolf = 1
EOF      → emit wolf\t1
```

Use `if current_word is not None` for the final emission; `if current_word == word` incorrectly emits `None\t0` when reducer input is empty.

Per-key average with a true combiner (Streaming: `-combiner combiner.py`):

```text
Mapper:   key\tvalue           → key\tvalue,1
Combiner: key\t[s,c ...]        → key\tΣs,Σc        (same shape as mapper output)
Reducer:  key\t[s,c ...]        → key\tΣs/Σc        (only stage that divides)
```

## 9. Iterative MapReduce pattern

```text
Driver reads small initialization state
  → writes/distributes current state
  → launches one multi-reducer Streaming job
  → reads only one summary per group
  → prints progress and tests convergence
  → repeats with a new HDFS intermediate directory
  → final converged MapReduce job writes the exact assessed HDFS output
  → cleans intermediate directories
```

| Stage | Representative record or rule |
|---|---|
| Mapper input | One raw record at a time; extract the item being assigned. |
| Mapper partial | `(group_id, item, partial_count)`; combine duplicates and flush periodically if needed. |
| Shuffle | Partition by `group_id`, so one reducer receives all partials for a group. |
| Reducer | Merge counts; use weighted calculations such as `Σ(weight × value) / Σweight`. |
| Iteration output | One small summary per group in a unique HDFS path. |
| Convergence | Compare deterministic summaries/signatures from consecutive assignments. |
| Final output | Keep it in the exact required HDFS directory; never mix intermediate parts into it. |

High-value correctness checks:

- Sum final group counts and confirm they equal the number of valid input records.
- Confirm mapper partial counts preserve multiplicity after local aggregation.
- Request the required reducer count on **every** iterative job.
- Keep `v` and `k` data-driven rather than hard-coding iteration or cluster counts.
- Remember that exact medoid selection is quadratic in distinct points per group even after duplicates are weighted.
- For the 2026 Assignment 1 interpretation, keep iteration control in the Bash entry point and do not create a local final text file merely to upload it as `part-00000`.
- Preserve a medoid point's coordinate text unless a fixed precision is explicitly required; format the assessed average dissimilarity to two decimals.

## 10. Week 5 lab runbooks and data-flow patterns

### EMR master: co-occurrence exercises

The supplied Week 5 folders contain `mapper.py`, `reducer.py`, `run.sh`, and `trip.txt`. Run these on the EMR master after uploading the folder and copying the input into HDFS:

```bash
cd ~/L4-code-pairs-cooccur
chmod +x run.sh
hadoop fs -copyFromLocal -f trip.txt /
./run.sh
hadoop fs -cat '/output/part-*'
```

Repeat with the stripes and relative-frequency folders. Their scripts use `/output` or `/output20`; the script may remove that path first. Confirm the exact path in `run.sh` before deleting anything. The relative-frequency pairs job requires `KeyFieldBasedPartitioner` with `-k1,1`; ordinary co-occurrence pairs do not need that custom partitioner because each complete pair can be reduced independently.

### Compact exam patterns

```text
Pairs mapper:  for each ordered (w1,w2), w1 != w2 → (w1,w2), 1
Pairs reducer: exact pair → sum all counts

Stripes mapper: for each w1 → w1, {w2: 1, ...}
Stripes reducer: same w1 → element-wise merge of neighbour maps

Relative pairs: emit (w1, *, 1) and (w1, w2, 1)
                 partition by w1; sort * first; divide N(w1,w2) by N(w1,*)

Relative stripes: merge all neighbours for w1; denominator is sum of the merged counts
```

For every exercise, be able to state: mapper input, exact emitted fields, which fields are the Streaming key, partitioner key, comparator order, reducer input group, and final output format. A common error is to partition pair records by the whole composite key when the reducer needs a left-word total.

## 11. Composite-key and multi-job patterns

Secondary-sort configuration:

```bash
-D stream.num.map.output.key.fields=2 \
-D mapred.text.key.partitioner.options='-k1,1' \
-D mapred.output.key.comparator.class=org.apache.hadoop.mapred.lib.KeyFieldBasedComparator \
-D mapred.text.key.comparator.options='-k1,1n -k2,2n' \
-partitioner org.apache.hadoop.mapred.lib.KeyFieldBasedPartitioner
```

Option memory aid:

```text
-k2,2   → field 2 only
n        → compare numerically
r        → reverse/descending
-k2,2nr → field 2, numeric descending
```

Streaming reduce-side join:

```text
A: join_id\t0\tmetadata
B: join_id\t1\tdetail
partition -k1,1; compare -k1,1 -k2,2n
reducer sees metadata before detail and emits joined records without a detail list
```

Three-job checklist:

| Check | Requirement |
|---|---|
| Job interfaces | Previous reducer output exactly matches the next mapper parser. |
| Paths | Use separate HDFS intermediate directories and one exact final path. |
| Reducers | Set the required count independently on every job. |
| Cleanup | Delete stale paths before starting; remove intermediates after downstream success. |
| Sorting | Comparator order is per partition; assign each record once to a disjoint ordered range if `getmerge` must be global. |
| Distinct count | Secondary-sort the distinct entity and count key changes rather than storing an unbounded set. |

Three-reducer global-sort requirement:

```text
mapper emits each summary once with an ordered range/bucket key
→ partitioner sends it to exactly one reducer
→ reducer receives only its range and streams comparator-sorted records
→ part-00000, part-00001, part-00002 cover high → middle → low ranges
```

Do not replicate the complete summary table to every reducer and do not store it in `records = []`. The 2026 Assignment 1 marker treated both as failures to partition and stream Big Data correctly.

## 12. Assignment verification and submission gate

### EMR master: verify execution and HDFS results

```bash
chmod +x task1-run.sh task2-run.sh task3-run.sh task1_mapper.py task1_reducer.py
./task1-run.sh
./task2-run.sh
./task3-run.sh

hadoop fs -ls /Output/task1 /Output/task2 /Output/task3
hadoop fs -cat '/Output/task1/part*' | head
hadoop fs -cat '/Output/task2/part*'
hadoop fs -cat '/Output/task3/part*'

# Expected final row counts for the original specification datasets
hadoop fs -cat '/Output/task1/part*' | wc -l    # 1,436
hadoop fs -cat '/Output/task2/part*' | wc -l    # 3
hadoop fs -cat '/Output/task3/part*' | wc -l    # 19

# Released grading datasets: 10 taxis, 357 Task 1/3 trips, 15 Task 2 trips
hadoop fs -cat '/Output/task1/part*' | wc -l    # 18
hadoop fs -cat '/Output/task2/part*' | wc -l    # 3; convergence after iteration 2
hadoop fs -cat '/Output/task3/part*' | wc -l    # 7

# Check the exact number of tab-separated fields in every row
hadoop fs -cat '/Output/task1/part*' | awk -F '\t' 'NF != 6 {bad++} END {print bad+0}'
hadoop fs -cat '/Output/task2/part*' | awk -F '\t' 'NF != 4 {bad++} END {print bad+0}'
hadoop fs -cat '/Output/task3/part*' | awk -F '\t' 'NF != 6 {bad++} END {print bad+0}'
```

For each job, confirm `_SUCCESS`, the expected number of data rows, exact tab-separated field counts, two-decimal formatting, and required ordering. Also inspect YARN/Streaming output to confirm that every required job actually launched three reducers; the number of non-empty final files alone is not sufficient evidence.

For a remark, download the submitted Canvas ZIP again, do not edit it, run that exact archive against the released grading files, and capture the commands plus exact HDFS output in one or more screenshots. A local replay supports algorithmic checking but does not replace the requested EMR/YARN evidence.

The three Canvas-download artifacts checked on 18 September 2026 (`s4271512_PG-1.zip`, `s4271512_PG-1.pdf`, and `s4271512_PG-2.doc`) were byte-for-byte identical to the frozen final ZIP, PDF, and DOC. The ZIP again contained the same 15 top-level files and the PDF contained 25 pages. The Canvas ZIP SHA-256 was `539374a20bb144f60e1056d05bf988ed769d6370fa6e7e0536e4d605bf187ce8`.

The subsequent AWS EMR remark run used that exact downloaded ZIP and the released `initialization.txt` (`k=3`, `v=4`) and `Trips_task2.txt` (15 records). Both Hadoop Streaming jobs launched three reducers. The submitted entry point exited with status `0`, stopped immediately after convergence in iteration 2, and produced these sorted HDFS rows:

```text
14.063  70.076  5  5.47
67.157  10.290  6  7.92
67.723  88.253  4  6.43
```

`10.290` and the published `10.29` are numerically identical; the difference is presentation only. A before/after hash comparison confirmed that every submitted `.py` and `.sh` file remained unchanged during the run. Retain the terminal transcript, full YARN log, sorted output, and screenshot together so the evidence can be audited. Never reconstruct a screenshot from published expected-output text.

Preserve a simple evidence chain for a remark run:

```text
Canvas-downloaded ZIP
  → calculate and record its SHA-256 before extraction
  → extract into a new EMR-master directory
  → replace only the external initialization input with the released grading file
  → upload released Trips_task2.txt to HDFS as /Input/Trips.txt
  → run the unchanged submitted task2-run.sh
  → capture iteration 2 convergence and hadoop fs -cat '/Output/task2/part*' | sort
```

The grading datasets are marker-supplied test inputs, not submission artifacts. Their absence from the submitted ZIP is correct and does not mean the submission was incomplete.

### Local Windows machine: build the upload set

For the postgraduate individual naming pattern, the three assessed uploads are:

```text
s4271512_PG.zip   ← one flat folder of all required .py/.sh files plus initialization.txt; no subfolders
s4271512_PG.pdf   ← standalone PDF containing all submitted code and shell scripts
s4271512_PG.doc   ← work log; Section 2 contains the step-by-step data-flow and `<key, value>` design explanation
```

The work-log DOC should retain Section 3's Submission Declaration Checklist. Do not confuse it with private operational notes: checklist confirmation belongs in the assessed template, while cluster lifecycle, hashes, test transcripts, and internal status commentary do not.

For a group, use the required `<GroupLeaderID>_Group<N>_PG` base name instead. The code PDF and work-log DOC are uploaded separately and must not be hidden inside the ZIP. Before uploading, extract the ZIP into a temporary folder and check that the run scripts, Python files, and `initialization.txt` are all at its top level with no naming collisions.

Keep private verification material outside the assessed set: project notes, checksums, EMR/YARN logs, HDFS output copies, page-render images, and cluster start/termination records are useful for personal evidence but are not substitutes for the required design explanation and should not be added unless the brief explicitly asks for them.

When comparing document designs, preserve the previous PDF and DOC in a separate backup directory and keep alternatives outside the assessed folder. Render every page of the candidate PDF and the actual submission-format DOC, then compare extracted text after ignoring page numbers. The final upload folder should still contain exactly one chosen ZIP, one chosen code PDF, and one chosen work-log DOC.

Final upload freeze: count the folder entries, confirm the three exact names and real file signatures, test ZIP extraction, verify that every archive entry matches the reviewed source, compile the extracted Python, run `bash -n` on every shell script, confirm every submitted source line appears in the Turnitin PDF, and render the actual DOC to inspect all pages. Also check comments, revisions, metadata, placeholders, and accidental private notes before uploading.

## 13. High-value rules and common failures

- **The output directory already exists:** Hadoop will not overwrite it; delete or choose a new path.
- **`Permission denied` for a script:** run `chmod +x script.sh`.
- **Streaming subprocess exits with code `127`:** check the shebang, execute permission and CRLF line endings; use `dos2unix` while debugging on EMR, but do not add environment-setup commands to the submitted run scripts.
- **Local `ChecksumException` after `copyToLocal`:** check for the matching hidden `.crc` file left beside the local copy; remove only that verified stale CRC before retrying.
- **`No such file or directory`:** run `pwd` and `ls`; confirm whether the path is local or in HDFS.
- **`bdp-emr` will not connect:** confirm the cluster is running and `WAITING`; remove an obsolete host key if reported.
- **One output file was expected but several appeared:** multiple reducers create multiple `part-*` files; use `-cat` or `-getmerge` when appropriate.
- **Reducer totals are wrong:** check tab separation, integer conversion, key-change output and the final post-loop output.
- **Combiner changes correctness:** a combiner is optional and repeatable; do not use unsafe “average of averages.” Preserve `(sum, count)` instead.
- **A custom partitioner was added without a grouping need:** use it only when selected composite-key fields must determine reducer placement; the default hash partitioner is correct when the complete mapper key is already the grouping key.
- **Final output is sorted with Bash:** encode ordering in mapper keys and Hadoop comparator settings. Local `sorted()` is acceptable only for bounded reducer-local algorithmic work or deterministic tie-breaking, not as a global Big Data sort.
- **A changing model is forced into many command-line parameters:** use scalar parameters for scalar controls and distribute structured centroid/medoid state with Streaming `-file`.
- **Iterative job reads too much into the driver:** keep the complete dataset in HDFS; return only bounded per-group summaries to the control process.
- **Iteration output collision:** give each iteration a fresh HDFS directory and keep all intermediates outside the required final output path.
- **Final iterative output is uploaded from a local text file:** for the 2026 Assignment 1 interpretation, make the converged MapReduce job create the assessed HDFS `part-*` output directly.
- **Duplicate compression changes results:** carry occurrence counts as weights and use them in every sum, average, cost, and final point count.
- **Reduce-side join buffers every detail:** secondary-sort a metadata tag first, retain only that metadata, and stream later detail records.
- **Distinct fleet/entity count uses a large set:** sort by `(group, entity)` and count entity-key changes in the reducer.
- **Each reducer part is sorted but `getmerge` is not:** a comparator gives only partition-local order; design ordered ranges/rank slices or another permitted global strategy.
- **Every reducer receives the complete sorted summary table:** emitting each summary to all reducer buckets is replication, not partitioning; route each summary once and stream only the assigned range.
- **Strict Bash mode causes an unexplained early exit:** `set -euo pipefail` is not inherently wrong, but explicitly handle every expected non-zero condition or use the course's explicit status-check pattern. The 2026 Assignment 1 marker deducted one functional point for strict mode even though the submitted scripts contained no pipelines, unset-variable dependency, or identified expected failure; for future work, follow the marker's requested explicit-check style unless written guidance confirms strict mode is acceptable.
- **A later job misparses an earlier job:** document and test every intermediate field, separator, HDFS path, and numeric format.
- **A result differs only at an exact half cent:** binary floating-point summation and mapper split order can change the final `%.2f` digit. For example, `356194.37 / 34 = 10476.305` can surface as either `10476.30` or `10476.31` depending on representation and the chosen tie rule. Use integer cents for partial sums and apply one documented `Decimal` rounding rule only after final aggregation.
- **All task folders exist, so the assignment looks finished:** code, cluster verification, the work-log explanation, and the three final upload artifacts are separate completion gates.
- **Pig casts the last CSV field to `null` or depends on converter behaviour:** Windows CRLF files leave `\r` on the final field; apply `TRIM` before `(int)`.
- **Pig ranking changes between runs or ties appear in the wrong order:** bags are unordered; order by the full key including the tie-breaker, and sort again inside a UDF before numbering ranks.
- **A Pig script fails on its second run:** `STORE` refuses an existing directory; start the script with `rmf /Output/taskN`.
- **Know the filesystem:** `ls` examines the current machine’s disk; `hadoop fs -ls` examines HDFS.
- **Always terminate EMR:** saving files does not stop billing; run `./terminate_cluster.sh` on `bdp-jump`.

## 14. Assignment 2 Pig runbook and submission gate (COSC2637, 2026)

`2026A2.pdf` assigns Postgraduate COSC2637 students Task 2. It requires Apache Pig on the RMIT EMR/HDFS environment, a Pig script named `task2.pig`, a Jython UDF named `task2.py`, and `START_YEAR`/`END_YEAR` parameters. The inputs are separate HDFS files at the root: `/medal_table.csv`, `/games.csv`, `/countries.csv` and `/population.csv`, the last of which is not needed for Task 2. The output directory is `/Output/task2`. All paths are case-sensitive.

Week 7 is the relevant preparation: Pig batch/Grunt use, HDFS CSV loading, joins, `STORE`, and UDF registration. The Olympic CSVs in `Assignment 2/Data/` are the A2 inputs; Week 7's taxi and URL-join files are practice data.

### EMR master: load inputs, run and inspect

```bash
hadoop fs -put -f countries.csv games.csv medal_table.csv population.csv /
pig -x mapreduce -param START_YEAR=2010 -param END_YEAR=2020 task2.pig
hadoop fs -cat '/Output/task2/part*'
ls /usr/lib/pig/lib | grep -i jython      # jython-standalone-2.7.0.jar on EMR (Pig 0.17.0)
```

### Compact Pig and Jython pattern

```pig
REGISTER 'task2.py' USING jython AS task2_udf;
%default START_YEAR 0
rmf /Output/task2
m  = LOAD '/medal_table.csv' USING PigStorage(',') AS (year:int, code:chararray, gold:int, silver:int, bronze:chararray);
mf = FILTER m BY year >= $START_YEAR AND year <= $END_YEAR;        -- filter first
mc = FOREACH mf GENERATE year, TRIM(code) AS code, gold, gold + silver + (int)TRIM(bronze) AS total;
j  = JOIN mc BY code, names BY code USING 'replicated';            -- small table last
g  = GROUP rows BY year;
t  = FOREACH g { s = ORDER rows BY gold DESC, code ASC; top = LIMIT s 3; GENERATE group AS year, top; };
```

```python
@outputSchema('report:chararray')          # injected by Pig; Jython 2.7 syntax
def format_games_report(year, host_city, top_gold, top_total):
    ...                                    # bags arrive as lists of tuples
    return '\n'.join(lines) + '\n'         # one record = several output lines
```

The expected output uses sequential ranks and breaks ties by country code: in 2018, Germany (14 gold) precedes Norway (14 gold) although Norway has more total medals. Country names come from `countries.csv`, so RUS prints as `Russia / ROC / OAR`. The Task 2 example in the brief shows only `Russia`; hard-coding that name would contradict the “no hard-coded output” rule.

The 27 September 2026 EMR verification ran the unchanged `task2.pig` and `task2.py` from the built ZIP. Twelve runs were compared byte for byte with an independent CPython recomputation, and all twelve matched. The runs covered the spec range `2010-2020`, a single Games (`2026`, `2006`), all years with and without parameters, a range with no Games (empty output), an immediate re-run, LF and header-row variants of the CSVs, and a test copy with `SET default_parallel 3`, whose three `part-*` files still concatenated in year order.

### Assignment 2 submission set

The Assignment 2 work log has only two sections: member contribution, which is not applicable for an individual submission, and the Submission Declaration Checklist. There is no design-explanation section, so design reasoning such as early filtering, the replicated joins and the join after aggregation must be visible in concise code comments.

```text
s4271512_PG.zip   ← task2.pig and task2.py only, flat, LF line endings
s4271512_PG.pdf   ← plain monospaced copy of both files for Turnitin, uploaded separately
s4271512_PG.doc   ← filled A2 work-log template saved as Word 97 .doc, uploaded separately
```

Week 10 is not an A2 prerequisite. Its lab is Spark Streaming with a socket word-count example. Broadcast and accumulator are presented as selective Spark topics and are not needed for this Pig assignment. Week 9 Spark Basics is also outside the A2 toolchain.

**UDF documentation version note:** the Canvas overview links Pig UDF documentation 0.17.0, while the detailed specification cites 0.18.0; the local guide is 0.17.0. The course EMR cluster runs Pig 0.17.0 on Hadoop 3.4.2 (checked 27 September 2026), so the 0.17.0 guide is the matching reference.

## 15. Assignment 3 Spark Streaming runbook and submission gate (COSC2637, 2026)

`2026A3.pdf` requires one Scala object, `streaming.a3`, in one `.scala` file. The job monitors an HDFS directory with 3-second batches and writes Task 1–3 output after every batch that has data. The source is `Assignment 3/a3-project/src/main/scala/streaming/a3.scala`.

The course EMR (emr-7.13.0, checked 25 October 2026) runs Spark 3.5.6, Scala 2.12.18 and Java 17. Compile against these versions with Spark as `provided`; `a3.jar` then contains only the project classes (about 30 KB).

### EMR master: run and test

```bash
hdfs dfs -rm -r -f /input /output; hdfs dfs -mkdir -p /input
spark-submit --class streaming.a3 --master yarn --deploy-mode client a3.jar hdfs:///input hdfs:///output 250 &
# wait until the YARN application is RUNNING, then add files while it runs:
hdfs dfs -put querylog_001.csv /input/
hadoop fs -cat '/output/task1-001/*'
kill -TERM <SparkSubmit pid>      # a background job in a script ignores SIGINT
```

### Data flow and code patterns

```text
new file -> lines -> parseRecord (skip header/malformed, clean text, drop empty) -> records (cached)
  Task 1  (query,1L) -> reduceByKey -> batchCounts (cached) -> sort -> task1-NNN
  Task 2  filter rt > threshold -> reduceByKey(count,sum,max,users) -> severity -> sort -> task2-NNN
  Task 3  batchCounts -> updateStateByKey(QueryStats) -> takeOrdered(10) -> task3-NNN
```

| Need | Pattern |
|---|---|
| Write only non-empty batches | `foreachRDD { rdd => if (!rdd.isEmpty()) ... }` |
| Folders `task1-001`, `-002`, … | per-task counter on the driver, incremented only when output is written |
| Globally ordered output without one bottleneck partition | `sortBy(key)` range-partitions: `part-00000`, `part-00001`, … hold consecutive ranges, so `cat taskN-NNN/*` is in order (the same lesson as the A1 marker's rejection of single-reducer designs) |
| Multi-key sort with DESC fields | negate the numbers in a tuple: `(-count, query)` |
| Top 10 from a large state | `rdd.takeOrdered(10)(ordering)`, never a full sort and `collect` |
| PG: no Task 3 output when idle | write only if some key has `currentBatchCount > 0` |
| Exact two-decimal average | `BigDecimal(sum) / count` with `setScale(2, HALF_UP)` |

`trend_status` is `NEW` when the state was empty, `INCREASED` when the key occurred in this batch, and `UNCHANGED` otherwise.

### Assignment 3 submission set

```text
s4271512_PG.zip   ← a3.jar and a3.scala only, flat
s4271512_PG.pdf   ← plain monospaced copy of a3.scala for Turnitin, uploaded separately
s4271512_PG.doc   ← filled A3 work-log template saved as Word 97 .doc, uploaded separately
```

The 25 October 2026 EMR run used the exact `spark-submit` command from the brief. Outputs `task1/2/3-001` and `-002` matched Appendix A line for line. A third file tested a comma inside a quoted query, a query that is empty after cleaning, CRLF line endings, `response_time_ms = 250` (not slow, because the rule is strictly greater) and a maximum of exactly 500 (`CRITICAL`, because the rule is `>=`). Idle batches and a header-only file produced no output folder.
