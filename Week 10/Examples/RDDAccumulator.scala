package org.example

import org.apache.spark.sql.SparkSession

object RDDAccumulator extends App{
  //A SparkSession is the entry point to using Spark functionality. It manages the configuration of the Spark application and coordinates the creation of RDDs, DataFrames, and SQL tables, among other things. A SparkContext, on the other hand, represents the connection to a Spark cluster and is used to configure the cluster resources, execute tasks, and collect results.

  //In most cases, a SparkSession should be used as it includes the functionality of a SparkContext and more. However, in some advanced scenarios, it may be necessary to use a SparkContext directly.

  val spark = SparkSession.builder()
    .appName("Accumulator")
    .master("local")
    .getOrCreate()

  //example 1
  val threshold = args(1).toInt
  var blankline = spark.sparkContext.longAccumulator("Blank Lines")
  spark.read.textFile(args(0)).foreach { line =>
    if (line.length() > threshold) blankline.add(1)
  }
  System.out.println(s"The value returned by accumulator is ${blankline.value}")
  System.out.println(s"*************The value returned by accumulator")

  //System.out.println(blankline)

  //example 2
  val longAcc = spark.sparkContext.longAccumulator("SumAccumulator")
  val rdd = spark.sparkContext.parallelize(Array(1, 2, 3, 4, 5, 6, 7, 8, 9, 10))
  rdd.foreach(x => longAcc.add(x))
  System.out.println(s"The value returned by accumulator is ${longAcc.value}")
}
