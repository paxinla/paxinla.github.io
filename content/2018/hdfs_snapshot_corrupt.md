Title: HDFS 数据块缺失
Date: 2018-03-16 15:19:23
Category: 数据平台
Tags: hadoop, hdfs
CommentId: 7

HDFS 上的部分文件出现了 corrupt blocks 怎么办？

<!-- PELICAN_END_SUMMARY -->

## 事件起因

　　之前在给 Hadoop 集群的部分节点更换磁盘[ps: 为什么是换磁盘而不是加磁盘，这里就不展开了。]的时候，导致 HDFS 的部分文件出现了 corrupt blocks ，这个通过以用户 hdfs 执行命令:

```bash
# 这个是列出发生了 corrupt 的文件
hdfs fsck / -list-corruptfileblocks

# 这个是删除掉已经 corrupt 的文件，执行前务必确认清楚。
hdfs fsck / -delete
```

　　解决了。之后再 `fsck /` 看起来是完全正常了。但是在 Cloudera Manager 中，HDFS 服务每次在重启后，还是显示错误，有文件块副本数不足；HA 的两个 namenode 就会进入安全模式，并一直保持在安全模式不退出。


　　因为已经确认过 HDFS 上的文件现在是没问题的，所以可以前行让 namenode 退出安全模式，此时 HDFS 可正常使用。但是文件块副本数不足的错误警告会一直存在，且重启 HDFS 的话， namenode 又会进入安全模式，治标不治本。

　　一番查找后，发现是以前在 HDFS 的某些目录里开启了 Snapshot 功能[ps: hdfs snapshot 功能参考: <i>http://hadoop.apache.org/docs/current/hadoop-project-dist/hadoop-hdfs/HdfsSnapshots.html</i> ]。磁盘故障，也造成了相关目录下的 `.snapshot` 目录下快照文件块的丢失。命令 fsck 是不会检查这里面的文件块的，但 HDFS 的 BlockManager 会检查，并在 Cloudera Manager 里报警。删除了旧的快照，重启 HDFS 服务之后，上述异常现象解除。
