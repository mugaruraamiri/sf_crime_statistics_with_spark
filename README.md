# sf_crime_statistics_with_spark
**1. How did changing values on the SparkSession property parameters affect the throughput and latency of the data?.**


Changing SparkSession Property parameters played on the `processedRowsPerSecond` parameter value. The value could encrease or decrease with different paremeter settings choice.

**2. What were the 2-3 most efficient SparkSession property key/value pairs? Through testing multiple variations on values, how can you tell these were the most optimal?**

To miximize `processedRowsPerSecond` or system throughput the most efficient SparkSession property key/ Value after experimentation was:
```
1. spark.sql.shuffle.partitions
2. spark.default.parallelism
```
