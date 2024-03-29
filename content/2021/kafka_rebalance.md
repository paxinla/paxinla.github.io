Title: [转] Kafka 平衡分区负载方法
Date: 2021-09-25 16:54:52
Category: 消息队列
Tags: 转载, kafka
CommentId: X

原文作者: 过往记忆大数据

原文链接: [https://www.iteblog.com/archives/10035.html](https://www.iteblog.com/archives/10035.html)

为防遗失，转载一份。完整版请至原文看，这里是选择性摘录。

<!-- PELICAN_END_SUMMARY -->


## 迁移已有的分区

通过官方提供的 `kafka-reassign-partitions.sh` 脚本来重新分配已有的分区。这个脚本支持整个 topic 的分区重新分配，也支持指定分区的重新分配。


## 新增分区

如果集群有新加节点机器，就可以对目标 topic 扩容分区数量。增加 topic 分区数量是快速完成的，无需等待。在没有分区变更的情况下，客户端由于 metadata 机制默认每 30s 自动更新一次，会很快感知到分区变化。生产者默认的写入策略是轮询，这样新增的流量会到新分区。有助于降低原有节点的负载。

这个方法容易造成分区数量的膨胀。如果数据写入时，有指定分区或者对分区数有依赖(如根据分区数做哈希)，这个方法也无效。


## 切换分区 leader

直接将高负载节点上的 leader 分区切换为 follower 。当集群中负载高的只有少数节点时，适合这个方法。

这个方法使得 leader 分区切换到了其他节点上，如果那个节点本来负载也不低，那么就会加大它的压力。而且当前 leader 负载高的时候，有可能副本掉出 ISR ；此时切换 leader 就会导致出现数据截断导致数据丢失。


## 删除分区 follower

follower 分区同步 leader 分区的数据也是要耗费机器资源的，直接将高负载节点上的 follower 分区去除掉，可以降低该节点的负载。

显然，这个方法会导致分区的副本数减少，降低分区数据可用的保障，也容易引起故障。因此，这个方法只能是一种临时手段。目标节点负载减低以后，应把停掉的分区 follower 重启。


## 其他思路

像删除 topic 再重建、垂直升级节点的配置等方法都需要停机时间，不赘述。



