Title: 让 beeline 使用 hive on tez
Date: 2018-03-20 11:17:45
Category: 数据平台
Tags: hadoop, cdh, hive, tez, beeline
CommentId: 9


## 配置 hive on tez

　　公司的 Hadoop 集群是 **CDH 5.12.0** ，它的 Hive 的版本是 *1.1.0* 。我用的 tez 版本是 0.9.0 。

　　让 hive 使用 Apache Tez 不难，参考[tez官方文档](https://github.com/apache/tez/blob/master/docs/src/site/markdown/install.md)编译即可。

<!-- PELICAN_END_SUMMARY -->

注意的点有以下几个：

1. Tez 依赖 protobuf ，编译的机器上要先安装这个。我用的是 protobuf-2.5.0 。
2. Tez 需要用 maven3 来编译，版本最低也要 3.1.1 。
3. 修改 tez 源代码目录下的全局 pom.xml ，改 `hadoop.version` 的值，和目标 cdh 的 hadoop version 相同。
4. 修改 tez 源代码目录下的全局 pom.xml ，添加如下内容：

```xml
&lt;profile&gt;
   &lt;id&gt;cdh5.12.0&lt;/id&gt;
   &lt;activation&gt;
      &lt;activeByDefault&gt;true&lt;/activeByDefault&gt;
   &lt;/activation&gt;
   &lt;properties&gt;
      &lt;hadoop.version&gt;2.6.0-cdh5.12.0&lt;/hadoop.version&gt;
   &lt;/properties&gt;

   &lt;pluginRepositories&gt;
     &lt;pluginRepository&gt;
        &lt;id&gt;cloudera&lt;/id&gt;
        &lt;url&gt;https://repository.cloudera.com/artifactory/cloudera-repos/&lt;/url&gt;
     &lt;/pluginRepository&gt;
     &lt;pluginRepository&gt;
        &lt;id&gt;nexus public&lt;/id&gt;
        &lt;url&gt;http://central.maven.org/maven2/&lt;/url&gt;
     &lt;/pluginRepository&gt;
   &lt;/pluginRepositories&gt;
   &lt;repositories&gt;
     &lt;repository&gt;
        &lt;id&gt;cloudera&lt;/id&gt;
        &lt;url&gt;https://repository.cloudera.com/artifactory/cloudera-repos/&lt;/url&gt;
     &lt;/repository&gt;
     &lt;repository&gt;
        &lt;id&gt;nexus public&lt;/id&gt;
        &lt;url&gt;http://central.maven.org/maven2/&lt;/url&gt;
     &lt;/repository&gt;
   &lt;/repositories&gt;
&lt;/profile&gt;
```

5. 修改 tez 目录下 `tez-mapreduce/src/main/java/org/apache/tez/mapreduce/hadoop/mapreduce/JobContextImpl.java` ，添加如下内容:

```java
@Override
public boolean userClassesTakesPrecedence() {
    return getJobConf().getBoolean(MRJobConfig.MAPREDUCE_JOB_USER_CLASSPATH_FIRST, false);
}
```

6. 在 HDFS 上直接放 `tez-0.9.0.minial.tar.gz` 也可以。但我是将它解压后再放到 HDFS 上。


## 让 beeline 也支持 hive on tez

　　这里主要参考了[这个文档](https://gist.github.com/epiphani/dd37e87acfb2f8c4cbb0)，因为我这里的集群 HDFS 的 namenode 开了 HA ，所以在 `tez-site.xml` 里设置 **tez.lib.uris** 时，变量是用的 *${fs.defaultFS}* ，如果没有 HA ，应该用 *${fs.default.name}* 。

　　注意在设置 HiveServer2 的环境变量时， `HADOOP_CLASSPATH` 是要包含 tez-site.xml 所在目录的。

　　设置好重启 HiveServer2 服务后，就可以在 beeline 里，通过

```sql
SET hive.execution.engine=tez;
```

　　来使用 hive on tez 了。

　　如果在执行查询语句时，出现了 `Caused by: java.lang.ClassNotFoundException: com.esotericsoftware.kryo.Serializer` 这样的错误时，可将 `/opt/cloudera/parcels/CDH/jars/kryo-2.22.jar` [ps: 我这里是 parcel 方式安装的 CDH 集群，习惯放到 /opt 目录下。]放到 HiveServer2 节点本地及 HDFS 上的 tez 的 lib 目录下。
