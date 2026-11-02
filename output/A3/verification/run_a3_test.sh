#!/bin/bash
# EMR end-to-end test of a3.jar with the exact spark-submit command from the specification.
cd ~/a3test
hdfs dfs -rm -r -f -skipTrash /input /output /s4271512/checkpoint > /dev/null 2>&1
hdfs dfs -mkdir -p /input
spark-submit --class streaming.a3 --master yarn --deploy-mode client a3.jar hdfs:///input hdfs:///output 250 > run.log 2>&1 &
PID=$!
for i in $(seq 1 60); do
  yarn application -list -appStates RUNNING 2>/dev/null | grep -q "A3 Query Log" && break; sleep 2
done
sleep 12   # streaming context running; several empty batches pass first
echo "[$(date +%T)] put querylog_001.csv"; hdfs dfs -put querylog_001.csv /input/
sleep 12   # 4 batches: one with data, three idle (PG: no task3 output when idle)
echo "[$(date +%T)] put querylog_002.csv"; hdfs dfs -put querylog_002.csv /input/
sleep 12
echo "[$(date +%T)] put header_only.csv (no valid records -> no output)"; hdfs dfs -put header_only.csv /input/
sleep 12
echo "[$(date +%T)] put querylog_003.csv"; hdfs dfs -put querylog_003.csv /input/
sleep 15
kill -TERM $PID; wait $PID
echo "== exit code $?"
echo "== hdfs dfs -ls /output"; hdfs dfs -ls /output | awk '{print $NF}'
for d in $(hdfs dfs -ls /output | awk '{print $NF}' | grep task | sort); do echo "== hadoop fs -cat $d/*"; hadoop fs -cat "$d/*"; echo "   files: $(hdfs dfs -ls $d | awk 'NR>1{print $NF}' | xargs -n1 basename | tr '\n' ' ')"; done
echo "== checkpoint dir"; hdfs dfs -ls /s4271512/checkpoint | head -5
echo "== errors in run.log"; grep -E "ERROR|Exception" run.log | head -20
