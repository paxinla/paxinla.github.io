Title: Spark SQL
Date: 2021-05-11 10:47:15
Category: 数据平台
Tags: spark
CommentId: X


<!-- PELICAN_END_SUMMARY -->


统计信息在 join 时特别重要[ref]David Vrba Ph.D. Spark SQL Beyond Official Documentation. DATA+AI SUMMIT EUROPE 2020[/ref]。相关参数:

+ spark.sql.autoBroadcastJoinThreshold : 是否使用 BHJ ，默认10MB。
+ spark.sql.cbo.joinRecorder.enabled: 优化多表 join ，默认 false 。

## 查看统计信息

如何查看 Spark SQL 的统计信息？首先，CBO 必须打开:

```scala
spark.conf.set("spark.sql.cbo.enabled", true)
```

执行:

```scala
spark.sql("""ANALYZE TABLE table_name
             COMPUTE STATISTICS""").show(n=50)

spark.sql("""ANALYZE TABLE table_name
             COMPUTE STATISTICS
             FOR COLUMNS column_name""").show(n=50)

spark.sql("DESCRIBE EXTENDED table_name").show(n=50)

spark.sql("DESCRIBE EXTENDED table_name column_name").show()
```

从 Spark 3.0 起，可以执行:[ps: explain(true) 显示的是 logical plan ，explain 显示的是 physical plan。]

```scala
spark.table(table_name).explain(mode="cost")
```


