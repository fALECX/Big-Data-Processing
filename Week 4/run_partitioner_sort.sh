#!/bin/bash
hadoop jar /usr/lib/hadoop/hadoop-streaming.jar \
-D mapred.output.key.comparator.class=org.apache.hadoop.mapred.lib.KeyFieldBasedComparator \
-D stream.num.map.output.key.fields=2 \
-D mapred.text.key.partitioner.options=-k1,1 \
-D mapred.text.key.comparator.options='-k2,2nr -k1,1' \
-D mapred.reduce.tasks=3 \
-file ./mapper.py \
-mapper ./mapper.py \
-file ./reducer.py \
-reducer ./reducer.py \
-input /highestSalary_sample.txt \
-output /output \
-partitioner org.apache.hadoop.mapred.lib.KeyFieldBasedPartitioner







