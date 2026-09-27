#!/usr/bin/env python3
"""Orchestrate iterative three-reducer Hadoop Streaming jobs for Task 2.

Hadoop MapReduce is not itself iterative, so this driver performs the control
flow: read v and the k initial medoids, run one assignment/update job per PAM
iteration, read the k small reducer summaries, print the required progress,
test whether assignments changed, and publish the final k lines to HDFS.
"""

import os
import subprocess
import sys


HADOOP_STREAMING_JAR = "/usr/lib/hadoop/hadoop-streaming.jar"
INPUT_PATH = "/Input/Trips.txt"
FINAL_OUTPUT = "/Output/task2"
TEMP_OUTPUT_BASE = "/tmp/bdp_assignment1_task2"
INITIALIZATION_FILE = "initialization.txt"
MEDOIDS_FILE = "task2_medoids.txt"
LOCAL_FINAL_FILE = "task2_final_output.txt"
NUM_REDUCERS = 3


def run(command, capture_output=False):
    result = subprocess.run(
        command,
        text=True,
        capture_output=capture_output,
        check=False,
    )
    if result.returncode != 0:
        if capture_output and result.stderr:
            print(result.stderr, file=sys.stderr, end="")
        sys.exit(
            "Command failed with exit code %d: %s"
            % (result.returncode, " ".join(command))
        )
    return result


def read_initialization(path):
    with open(path, encoding="utf-8") as source:
        lines = [line.strip() for line in source if line.strip()]

    if len(lines) < 2:
        raise ValueError("initialization.txt must contain v and at least one medoid")

    try:
        max_iterations = int(lines[0])
    except ValueError:
        raise ValueError("The first line of initialization.txt must be an integer v")
    if max_iterations < 1:
        raise ValueError("v must be at least 1")

    medoids = []
    for line_number, line in enumerate(lines[1:], start=2):
        try:
            x_text, y_text = line.split()
            medoids.append((float(x_text), float(y_text)))
        except ValueError:
            raise ValueError(
                "Line %d of initialization.txt must contain medoid_x medoid_y"
                % line_number
            )

    return max_iterations, medoids


def write_medoids(medoids):
    with open(MEDOIDS_FILE, "w", encoding="utf-8", newline="\n") as destination:
        for x, y in medoids:
            destination.write("%.3f %.3f\n" % (x, y))


def run_iteration(iteration, medoids):
    write_medoids(medoids)
    output_path = "%s/iteration_%03d" % (TEMP_OUTPUT_BASE, iteration)

    run(["hadoop", "fs", "-rm", "-r", "-f", output_path])
    run(
        [
            "hadoop",
            "jar",
            HADOOP_STREAMING_JAR,
            "-D",
            "mapred.reduce.tasks=%d" % NUM_REDUCERS,
            "-file",
            "./task2_mapper.py",
            "-mapper",
            "./task2_mapper.py",
            "-file",
            "./task2_reducer.py",
            "-reducer",
            "./task2_reducer.py",
            "-file",
            "./%s" % MEDOIDS_FILE,
            "-input",
            INPUT_PATH,
            "-output",
            output_path,
        ]
    )
    return output_path


def read_iteration_output(output_path):
    result = run(
        ["hadoop", "fs", "-cat", output_path + "/part-*"],
        capture_output=True,
    )
    clusters = {}

    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        fields = line.split("\t")
        if len(fields) != 6:
            raise ValueError("Unexpected reducer output: %s" % line)
        cluster_index = int(fields[0])
        clusters[cluster_index] = (
            float(fields[1]),
            float(fields[2]),
            int(fields[3]),
            float(fields[4]),
            fields[5],
        )

    return clusters


def publish_final_output(clusters, medoids):
    with open(LOCAL_FINAL_FILE, "w", encoding="utf-8", newline="\n") as destination:
        for index, (fallback_x, fallback_y) in enumerate(medoids):
            if index in clusters:
                medoid_x, medoid_y, count, cost, _signature = clusters[index]
            else:
                medoid_x, medoid_y, count, cost = fallback_x, fallback_y, 0, 0.0
            destination.write(
                "%.3f\t%.3f\t%d\t%.2f\n"
                % (medoid_x, medoid_y, count, cost)
            )

    run(["hadoop", "fs", "-rm", "-r", "-f", FINAL_OUTPUT])
    run(["hadoop", "fs", "-mkdir", "-p", FINAL_OUTPUT])
    run(
        [
            "hadoop",
            "fs",
            "-put",
            "-f",
            LOCAL_FINAL_FILE,
            FINAL_OUTPUT + "/part-00000",
        ]
    )


def main():
    try:
        max_iterations, medoids = read_initialization(INITIALIZATION_FILE)
    except (OSError, ValueError) as error:
        sys.exit("Initialization error: %s" % error)

    cluster_count = len(medoids)
    previous_signatures = None
    clusters = {}

    # Remove stale results before beginning so a failed run cannot be mistaken
    # for the current run's final output.
    run(["hadoop", "fs", "-rm", "-r", "-f", FINAL_OUTPUT])
    run(["hadoop", "fs", "-rm", "-r", "-f", TEMP_OUTPUT_BASE])

    for iteration in range(1, max_iterations + 1):
        output_path = run_iteration(iteration, medoids)
        clusters = read_iteration_output(output_path)

        new_medoids = []
        signatures = []
        print("Iteration %d" % iteration)

        for index in range(cluster_count):
            if index in clusters:
                medoid_x, medoid_y, count, cost, signature = clusters[index]
            else:
                # A cluster can be empty, especially with duplicate initial
                # medoids. Keep its current medoid and still emit a final line.
                medoid_x, medoid_y = medoids[index]
                count, cost, signature = 0, 0.0, "EMPTY"
                clusters[index] = (
                    medoid_x,
                    medoid_y,
                    count,
                    cost,
                    signature,
                )

            new_medoids.append((medoid_x, medoid_y))
            signatures.append(signature)
            print(
                "cluster %d\tmedoid=(%.3f, %.3f)\t#points=%d\tavg_dissimilarity=%.2f"
                % (index, medoid_x, medoid_y, count, cost)
            )

        assignments_unchanged = (
            previous_signatures is not None and signatures == previous_signatures
        )
        medoids = new_medoids

        if assignments_unchanged:
            print("Assignments unchanged; converged after %d iteration(s)." % iteration)
            break

        previous_signatures = signatures

    publish_final_output(clusters, medoids)
    run(["hadoop", "fs", "-rm", "-r", "-f", TEMP_OUTPUT_BASE])
    print("Final output written to %s" % FINAL_OUTPUT)

    for local_temporary_file in (MEDOIDS_FILE, LOCAL_FINAL_FILE):
        try:
            os.remove(local_temporary_file)
        except OSError:
            pass


if __name__ == "__main__":
    main()
