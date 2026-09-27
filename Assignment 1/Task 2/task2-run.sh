#!/bin/bash
# Task 2 - exact PAM/k-medoids clustering of trip drop-off locations.
# This script is the required end-to-end entry point on the EMR master node.

set -euo pipefail
cd "$(dirname "$0")"

# Hadoop Streaming launches these files directly on worker nodes.
chmod +x task2_mapper.py task2_reducer.py

python3 ./task2_driver.py
