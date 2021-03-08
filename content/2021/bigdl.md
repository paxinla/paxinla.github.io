Title: BigDL：值得关注的 Spark 上的深度学习库
Date: 2021-03-08 15:53:08
Category: 人工智能
Tags: spark, bigdl
CommentId: X

## BigDL 与 Analytics Zoo 简介

[BigDL](https://github.com/intel-analytics/bigdl) 是一个在 Apache Spark 上构建深度学习、数值计算及神经网络应用的库，它支持导入预先通过 Caffe、 Torch 或 Keras 训练的模型到 Spark 中。

<!-- PELICAN_END_SUMMARY -->

很多时候，待分析的数据已经存储在了 HDFS 或其他大数据存储设施上，使用 BigDL 可以直接在同一个大数据集群上进行分析、训练模型，充分利用已有的大数据集群。

[Analytics Zoo](https://github.com/intel-analytics/analytics-zoo) 是基于 BigDL 的一个平台，还内建了一些推荐系统、时序数据处理、NLP 等模型。


## 使用 BigDL

```scala
// 使用 BigDL 必须先初始化一个 Engine
import com.intel.analytics.bigdl.utils.Engine
val conf = Engine.createSparkConf()
            .setAppName("test")
            .set("spark.task.maxFailures", "1")
val sc = new SparkContext(conf)
Engine.init

// Do something ...

sc.stop
```

如果是作为本地的 Java/Scala 程序运行，则需要在代码中添加如下设置:

```scala
System.setProperty("bigdl.localMode", "true")
System.setProperty("bigdl.coreNumber", 使用的CPU核数)
```

BigDL 支持直接使用 Sequential/Functional API 建模，也可以导入 Caffe、Keras、Tensorflow 导出的模型，通过 Spark 应用到 Hadoop 上的数据集。


## 使用 Analytics Zoo

直接使用 BigDL 代码还是有点繁琐的，Zoo 提供了许多 Context 简化代码，与 Spark 的 DataFrame API 也更兼容。

