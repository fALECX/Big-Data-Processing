#!/bin/bash    
hadoop jar /usr/lib/hadoop/hadoop-streaming.jar \
-D mapred.reduce.tasks=3 \
-file ./mapper.py \
-mapper ./mapper.py \
-file ./reducer.py \
-reducer ./reducer.py \
-input /3littlepigs.txt \
-output /output







