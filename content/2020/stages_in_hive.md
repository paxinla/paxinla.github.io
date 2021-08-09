Title: Hive 如何划分 Stage
Date: 2020-12-11 14:08:39
Category: 数据平台
Tags: hadoop, hive
CommentId: X


<!-- PELICAN_END_SUMMARY -->

最近面试时我被问到 Hive 是如何划分 stage （阶段）的。[ps: 这个问题作为面试题还是挺 SB 的。]

简明扼要的讲，就是以执行这个 Operator 时，它所依赖的数据是否已经“就绪”为标准。

一个 Hive 任务会包含一个或多个 stage，不同的 stage 间会存在着依赖关系，越复杂的查询通常会引入越多的 stage (而 stage越多就需要越多的时间时间来完成)。

用户提交的 Hive QL 经过词法、语法解析后得到 AST 。语义分析器遍历 AST 抽象出 QueryBlock 。逻辑计划生成器遍历 QueryBlock ，将它们翻译为 Operator（这些 Operator 就是 Hive 对计算抽象出来的算子）生成 OperatorTree 。逻辑计划优化器对 OperatorTree 进行变换，得到优化后的 OperatorTree （即重写了逻辑执行计划）。物理计划生成器遍历 OperatorTree ，翻译为用计算引擎作业任务描述的物理执行计划 TaskTree 。物理计划优化器再对 TaskTree 进行变换，生成最终物理执行计划，以提交给计算引擎执行。

Hive 支持 MapReduce、Tez 、Spark 等计算引擎，可以将逻辑算子转换成对应计算引擎的物理任务。

stage 的划分发生在物理计划生成器将 OperatorTree 转化为 TaskTree 的阶段。基本上是按深度优先遍历 OperatorTree ，根据计算引擎的 Compiler 的规则，生成相应的 Task 。

一个 stage 可以是一个 MapReduce 任务(或者一个 Map Reduce Local Work)，也可以是一个抽样阶段，或者一个合并阶段，还可以是一个 limit 阶段，以及 Hive 需要的其他某个任务的一个阶段。默认情况下，Hive 会一次只执行一个 stage ，当然如果使用了并行执行，也可以同时执行几个没有依赖关系的 stage 。

并不是所有列在 explain 计划里的 stage 都会真正执行的，有些 stage 经过优化器优化后实际上是空的 stage 。观察执行日志，经常可以发现如 "Stage-3 is filtered out by condition resolver" 之类的记录。

参考执行计划输出设置:

- 输出执行计划到日志需设置 `set hive.log.explain.output=true` (default false) 。
- 输出执行计划到 WebUI 需设置 `set hive.server2.webui.explain.output=true` (default false) 。
- 输出更有可读性的 Hive on Tez 执行计划需设置 `set hive.explain.user=true` (default false) 。
- 输出 Hive on Spark 执行计划到日志需设置 `set hive.spark.explain.user=true` (default false) 。









