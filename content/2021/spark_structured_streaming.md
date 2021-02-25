Title: Spark Structured Streaming 概览
Date: 2021-02-20 15:35:42
Category: 数据平台
Tags: spark
CommentId: X

<!-- PELICAN_END_SUMMARY -->

## Spark 的流数据处理

Spark 处理流数据的模型就是用(微)批模拟流。

Spark Streaming 是 Spark 上的流处理库，抽象出基于 RDD 的 Dstream 。

[ref]<a href="http://spark.apache.org/docs/latest/structured-streaming-programming-guide.html">Spark Structured Streaming</a>[/ref] 从 Spark 2.0 开始引入，它是基于 SparkSQL 的流处理引擎，抽象出基于 Dataset/DataFrame 的 Stream DataFrame 。[ps: Spark 2.0 时，Dataset/DataFrame 不局限于 SparkSQL ，成为 Spark 全局的主要 API 。]它与 Spark Streaming 最大的区别就是它用几乎同一套 Dataset/DataFrame 的 API 来处理流数据和批数据。

<p class="list-title">部分算子不能用在流数据上：</p>

- 不可链式对多个流的聚合。
- 无法只取流的前N行。
- 不能对流 distinct ，应当通过流数据中的数据唯一的字段来 dropDuplicates 。
- 只有在输出模式为 complete 且流数据已经被聚合后才能进行排序。
- 不能直接对流 count ，应当 ds.groupBy().count() 。
- 不能直接对流 foreach ，应当 ds.writeStream.foreach(...) 。
- 不能直接对流 show ，只能用 Console sink 。
- 流不能和流或静态数据作 full outer join 。流和流之间依照水位线有条件地 join 、流和静态数据之间的 join ，静态数据不能作为“驱动方”。

Structured Streaming 的代码是先定义 Dataset/DataFrame 的产生、变换和输出，再 start 一个新的执行线程来触发执行之前的定义。在新的执行线程里需要<span class="emp-text">持续地</span>去发现新数据，进而<span class="emp-text">持续地</span>查询最新计算结果至输出，这个过程就是 continous query (<span class="emp-text">持续查询</span>)。


### SparkSession

在 Spark 2.x 种，程序入口简化为只有一个 SparkSession 。不用再显示创建 SparkConf, SparkContext 或 SQLContext ，它们都被封装在 SparkSession 中。

```scala
import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._

val spark: SparkSession = SparkSession
                            .builder
                            .master("...")
                            .appName("example")
                            .enableHiveSupport()
                            .getOrCreate()

// 可以读取嵌套结构
import spark.implicits._
```

```scala
// 设定 Spark 的运行时配置属性
spark.conf.set("spark.sql.shuffle.partitions", 10)
spark.conf.set("spark.executor.memory", "6g")

// 获取所有设定
val configMap: Map[String, String] = spark.conf.getAll()
```

SparkSession 将 catalog 作为一个公开的公共实例，该实例的操作元数据的方法返回 Dataset 形式的结果。

```scala
// 访问所有的表和数据库
spark.catalog.listDatabases.show(false)
spark.catalog.listTables.show(false)
```


### Source 和 Sink

Structured Streaming 通过 source 读取外部数据(不用像 Spark Streaming 里 StreamingContext 要设置 batch 的 duration )，通过 sink 写出到外部目标。Structured Streaming 对数据的容错一致性语义和 source/sink 息息相关。当 source 支持对已消费数据的定位和重放，且 sink 的输出操作是幂等时，Structured Streaming 可以做到 end-to-end exactly-once 语义。

截至本文写下时，Spark 内置的 source 有： File source, Kafka source, Socket source 和 Rate source ；内置的 sink 有： File sink, Kafka sink, Foreach sink, Console sink 和 Memory sink 。


### Window 和 watermark

Structured Streaming 的窗口使用的是数据时间 event time 。

当输出模式为 append 或 update 时，[ps: 输出模式有: append(默认,增量)、update(仅变动)、 complete(全量)这3种。]用户可以设置一个“迟到阈值”，在每个窗口的结束时间点，当前流中最大的 event time 减去这个阈值后得到的时间点就是水位线 watermark ，后续如果有“迟到”的数据，只要它的时间点比水位线低/小，这个数据就会被忽略掉。

当输出模式为 append 时，只有窗口的结束时间点小于水位线时，才会有结果输出，不会输出“中间”结果。

当输出模式为 update 时，每个窗口的 trigger 时间点，都有结果输出，所以可以看到输出里位于水位线上的“迟到”数据会被更新进结果中。

两个流在 join 时，“驱动方”需要设置 watermark ，关联条件中需要“被驱动方”设置好 event time + accepted delay time 。


### Checkpoint

检查点使 Structured Streaming 处理过程失败后重新开始时，获知上个检查点时处理状态。检查点功能需要在 HDFS 上使用一个目录。

```scala
someDF.writeStream
  .outputMode("complete")
  .option("checkpointLocation", "/someHDFSpath")
  .format("memory")
  .start()
```

