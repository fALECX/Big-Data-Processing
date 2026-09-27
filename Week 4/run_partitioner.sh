#!/bin/bash    
hadoop jar /usr/lib/hadoop/hadoop-streaming.jar \
-D stream.num.map.output.key.fields=2 \
-D mapred.text.key.partitioner.options=-k2,2 \
-D mapred.reduce.tasks=3 \
-file ./mapper.py \
-mapper ./mapper.py \
-file ./reducer.py \
-reducer ./reducer.py \
-input /highestSalary_sample.txt \
-output /output \
-partitioner org.apache.hadoop.mapred.lib.KeyFieldBasedPartitioner






