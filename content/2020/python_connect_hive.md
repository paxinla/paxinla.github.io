Title: Python 连接 Hive 的方式
Date: 2020-12-10 09:49:10
Category: 数据平台
Tags: hadoop, hive, python
CommentId: X


Python 连接 Hive 的方式都有哪些呢？

<!-- PELICAN_END_SUMMARY -->

连接 Hive 的方式无非 Thrift、JDBC、ODBC 几种，都需要服务端开启 HiveServer2 的服务。

## 通过 Thrift

客户端环境可能需要先配置好 SASL、Thrift 相关包的部署。

### PyHive

[PyHive](https://github.com/dropbox/PyHive) 可以连接 Hive 和 Presto 。

[HiveServer2](https://cwiki.apache.org/confluence/display/Hive/Setting+up+HiveServer2) 是一个基于 Thrift 的服务，是 [HiveServer](https://cwiki.apache.org/confluence/display/Hive/HiveServer) 的替代。

### pyhs2

[pyhs2](https://github.com/BradRuderman/pyhs2) 是一个 HiveServer2 的客户端驱动，但它从 2016 年起就已经无人维护，不推荐继续使用。

### impyla

[impyla](https://github.com/cloudera/impyla) 在 Windows 下的表现不错。


## 通过 JDBC

Hive 自己的 beeline 客户端就是通过 JDBC 连接 HiveServer2 的。Python 操作 JDBC 需要 [JPype](https://github.com/jpype-project/jpype) 。

### JayDeBeApi

[JayDeBeApi](https://github.com/baztian/jaydebeapi) 是最常见的 Python 下操作 JDBC 的库。


## 通过 ODBC
### pyodbc

[pyodbc](https://github.com/mkleehammer/pyodbc) 需要客户端先配置好 Data Source 。Linux 下可能需要额外安装 ODBC 驱动。


