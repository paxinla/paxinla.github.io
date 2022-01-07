Title: Databricks 使用的一些 Tips
Date: 2022-01-07 13:47:21
Category: 数据平台
Tags: spark, scala
CommentId: X


<!-- PELICAN_END_SUMMARY -->

+ 在 databricks 上执行自己的 jar 包时，程序内不可有如 spark.close() 之类的关闭语句，否则会造成执行失败。
+ 用 airflow 的 DatabricksSubmitRunOperator 调度 databricks 上的 jar 包时，如果用 `spark_submit_task` 的方式，要求每次运行时都“新建”cluster ，无法使用已有的 cluster 。如果用 `spark_jar_task` 的方式，可以用 `existing_cluster_id` 来指定使用已有的 cluster ，但是要求连接 databricks 的 token 所属用户对 cluster 有 can manage 的权限。因为这种方式总是会将 jar 作为 library 安装到目标 cluster 上。
+ 用 airflow 的 DatabricksSubmitRunOperator 调度 databricks 上的 notebook (`notebook_task` 方式)时，在 notebook 中可以通过 `dbutils.widgets` 设置的变量接收 airflow 传递给它的参数。只要对 notebook 有运行权限即可。这种方式的调度粒度较粗，是整个 notebook ，无法指定执行 notebook 中的某个 cell 。
+ 用 airflow 的 DatabricksSubmitRunOperator 调度只能得到成功或失败的最终状态，不能在 airflow 的 task 日志中直接看到错误原因；但是可以看到 databricks 上的 task run 地址，浏览器打开这个地址，可以看到真实的错误原因。

