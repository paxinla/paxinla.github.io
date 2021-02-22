Title: HDFS 概览
Date: 2021-02-08 14:26:03
Category: 数据平台
Tags: hadoop, hdfs
CommentId: X

<!-- PELICAN_END_SUMMARY -->

## HDFS 的设计背景

HDFS （Hadoop Distributed File System）是一个适合运行在廉价商业机器上的关注吞吐量的分布式文件系统，是对 Google 的 GFS 的开源模仿。面向大规模数据集，能够横向扩展。


<p class="list-title">HDFS 的特性:</p>

- 适合大文件，不适合海量小文件。
- 流式访问数据：适合一次写入，多次读出的场景。(流式的意思是来一点就处理一点，不积攒)
- 数据访问的延迟较高，不适合低延迟的场景。
- 只支持单个写入者，不支持并发写入。
- 不支持文件随机修改，仅支持追加写入。

## HDFS 的架构
### NameNode

NameNode 有一个 Active NameNode ，一个 Standby NameNode ，两台 NameNode 互为冷备，只有处于 Active 状态的 NameNode 对外提供读写服务。每次 Active NameNode 写 editlog 的时候，除了写入本地磁盘外，还会提交到 JournalNode 集群，Standby NameNode 再从 JournalNode 集群定时同步 editlog ，再把同步的 editlog 应用到内存中的 fsimage 上。[ps: 从 JournalNode 上同步的 editlog 都是处于 finalized 状态的 editlog segment 。]

epoch 是一个单调递增的整数，用来标识每一次 Active NameNode 的生命周期，每次主备 NameNode 切换，epoch 就会加 1 。

<p class="list-title">NameNode 存储元数据:</p>

- 管里 HDFS 的 namespace 。
- 配置副本策略。
- 文件到数据块的映射。
- 处理客户端的读写请求。

namenode 的 `hdfs-site.xml` 里的 `dfs.hosts` 指定允许连接到 namenode 的主机列表文件。如果该值为空，则允许所有主机，可以不配置；`dfs.hosts.exclude` 指定不允许连接到 namenode 的主机列表文件，如果该值为空，则不排除任何主机。

### DataNode

若干个 DataNode 为存储数据块的机器:

- 存储实际的数据块。
- 执行数据块的读写操作。

DataNode 会同时向主备两个 NameNode 上报数据块的位置信息。

<p class="list-title">DataNode 心跳机制的作用:</p>

1. 当 datanode 启动时，将自身的信息上报给 namenode ，namenode 经过 check 后使其成为集群的成员，维护 datanode 的信息。
2. 当 datanode 启动时，将 block 信息汇报给 namenode ，使 namenode 可以维护数据块和数据节点之间的映射关系。
3. 定期发送心跳，告诉 namenode 自己是存活的；执行 namenode 通过心跳响应传过来的指令(如删除数据块)。

在 datanode 向 namenode 注册时，namenode 会根据用户定义的 Java 类或自定义脚本来确定该 datanode 所属机架，如果不指定脚本则默认所有 datanode 属于一个机架 `/default-rack` 。[ps: 机架感知默认没有启用，需要指定 hdfs-site.xml 的参数 `topology.node.switch.mapping.impl` 或 `topology.script.file.name` 。]

当 datanode 成功添加或删除一个 block 后，需要向 namenode 汇报以更新 namenode 内存中数据块和数据节点之间的映射关系。

datanode 的 hdfs-site.xml 的 `dfs.datanode.data.dir` 指定了本节点上用来存储 HDSF 数据的本地磁盘目录。参数 `dfs.datanode.failed.volumes.tolerated` 表示本 datanode 可以接受前者的磁盘列表里有多少个磁盘发生故障，默认值为0。

datanode 周期性检查块副本的数据是否与校验和一致。如果发现副本损坏，则通知 namenode 。namenode 会优先复制未损坏的副本，当副本数达到复制因子 `dfs.replication` 再删除损坏的副本。


### Zookeeper(ZKFC)

两个 NameNode 上都有一个 ZKFailoverController 独立进程，来对 NameNode 的主备切换进行总体控制。ZKFC 能及时检测到 NameNode 的健康情况，在 Active NameNode 不可用时可借助 Zookeeper 实现自动的主备选举和切换。[ps: 也支持不依赖于 Zookeeper 的手工主备切换。]

### 共享存储系统(QJM)

共享存储系统保存了 namenode 在运行过程中所产生的 HDFS 的元数据。主 namenode 和备 namenode 通过共享存储系统实现元数据同步。在进行主备切换的时候，新的主 namenode 在确认元数据完全同步之后才能继续对外提供服务。JournalNode 集群还向 Active NameNode 提供 epoch 。

OJM (Quorum Journal Manager) 在 2N+1 个 JournalNode 上存储 NameNode 的 editlog ，每次写入操作都通过 Paxos 保证写入的一致性，它最后允许有 N 个 JournalNode 同时故障。

处于 Standby 状态的 NameNode 转换为 Active 状态的时候，有可能上一个 Active NameNode 发生了异常退出，那么 JournalNode 集群中各个 JournalNode 上的 editlog 就可能会处于不一致的状态，所以首先要做的事情就是让 JournalNode 集群中各个节点上的 editlog 恢复为一致。在 JournalNode 集群中各个节点上的 editlog 达成一致之后，新的 Active NameNode 要从 JournalNode 集群上补齐落后的 editlog。只有在这两步完成之后，当前新的 Active NameNode 才能安全地对外提供服务。


### 客户端

客户端负责:

- 将文件切分成数据块。
- 与 namenode 交互，获取文件的位置信息。
- 与 datanode 交互，读取或写入数据。
- 通过命名管理 HDFS、访问 HDFS 。


## HDFS 的块大小
### HDFS 是基于块存储的

使用块的好处是:

- 单个文件的大小可以超过 HDFS 集群中单个节点的磁盘大小，单个节点只存储这个文件部分的块。
- 提高容错性，每个块都有副本在别的机器上，若块丢失/损坏，系统可以读副本中的数据。

HDFS 的数据块默认存 3 份，第二个副本在与第一个副本同机架的不同的 datanode 上，第三个副本存在与第二个副本不同的机架上。

HDFS 的 fsck 可以显示块信息，如: `hdfs fsck / files -blocks` 。

### HDFS 的块大小

HDFS 块大小是通过设置 `hdfs-site.xml` 的参数 `dfs.blocksize` (一般设为 512 的整数倍)来完成的。`dfs.blocksize` 的值要**大于**`dfs.namenode.fs-limits.min-block-size` 的值。[ps: 需要停止 hadoop 集群再修改，修改完毕后再启动。]

HDFS 块大小的默认值从2.7.3版本起是 128 MB，之前版本默认是 64 MB。HDFS 的块比磁盘的默认的块大小(512B)大，目的是为了最小化磁盘寻址开销，这也是 HDFS 块大小设置的原则。

<p class="list-title">影响 HDFS 块大小的因素主要有以下几个:</p>

1. 减少磁盘寻址时间。同样的数据，数据块越大，数据块的数量越少；数据块越小，数据块的数量越多。数据块在磁盘上不是连续存储的，随机寻址的较慢。所以读越多的(小)数据块，磁盘的总寻址时间就越长(小块的传输时间短)；读越少的(大)数据块，总寻址时间就越短(大块的传输时间长)。合适的块大小有助于减少磁盘寻址时间，提高系统吞吐量。
2. 减少 namenode 的内存消耗。如果数据块设置得太小，则 fsimage 需要维护的数据块的信息就太多，占用 namenode 的内存。
3. 提高 MapReduce 的 map 任务处理速度。一个 map 任务一次只能处理一个块，如果块太大，则任务数变少，作业的处理速度就变慢了。
4. 减少 MapReduce 的 map 任务恢复时间。map 任务崩溃后重启的过程中需要加载数据，数据块越大，数据加载时间越长。

从经验值说，磁盘寻址的时间是磁盘传输时间的 1% ，寻址时间约为 10ms 。那么如果磁盘传输时间为 100MB/s ，则块大小设置约为 100MB(128MB)。对固态硬盘，可以忽略寻址时间，块大小设置可以尽量接近传输时间。


## HDFS 读写过程

客户端向 datanode 、datanode 之间传输数据的单位是 packet ，默认 64KB 。

客户端向 datanode 、datanode 之间数据校验的单位是 chunk ，默认 512 字节；每个 chunk 需带 4B 的校验位，所以实际每个 chunk 写入 packet 的大小是 516B 。

### HDFS 的写数据过程

1. 客户端向 namenode 请求上传文件，namenode 检查目标文件、父目录是否存在、权限等，若通过检查则分配元数据，创建空文件，将创建操作写入 editlog ，然后向客户端返回输出流对象(真正执行写数据的就是它)。
2. 客户端向 namenode 请求一个新的空数据块。
3. namenode 返回存储这个数据块的 3 个 datanode 节点列表。[ps: 因为块默认存3份。]
4. 客户端与第一个 datanode 交互，请求上传数据 (给第一个 datanode 的除了数据还有 datanode 列表)，第一个 datanode 收到请求后继续调用第二个 datanode ，第二个 datanode 调用第三个 datanode ，通信管道 pipeline 建立完成。
5. 客户端先往第一个 datanode 以 packet 为单位上传第一个 block ，第一个 datanode 收到一个 packet 就会转发给第二个 datanode ，第二个 datanode 再转发给第三个 datanode 。所有 datanode 确认传输完成后，由第一个 datanode 通知客户端写入成功，每个 datanode 接收 block 成功后都会向 namenode 汇报，namenode 更新内存中数据块与节点的映射信息。
6. 每个 block 传输完成后，再重复第 5 步，直至所有数据块传输完毕。客户端通知 namenode 文件写入成功，namenode 确认副本数是否满足后，将相关结果提交到 editlog 中。

客户端切分文件为数据块。

在写入时候，块大小是以客户端的配置为准的，客户端没有配置才以服务端为准。

<p class="list-title">如果写入过程中出现故障:</p>

1. 输出流中缓存的没有确认的数据包会重新加入发送队列，这种机制确保了数据节点出现故障时不会丢失任何数据，所有的数据都是经过确认的。
2. 故障数据节点会从输入流管道中删除，然后输出流会通知 namenode 分配新的 datanode 到 pipeline 中，并使用新的时间戳重新建立数据流管道。由于新添加的 datanode 上并没有存储这个新的 block ，这时客户端会通知 pipeline 中的一个 datanode 复制这个 block 到新的 datanode 上。
3. pipeline 重新建立之后，输出流会更新 namenode 中的元数据。至此，一个完整的故障恢复流程就完成了，客户端可以正常完成后续的写操作了。

如果多个节点写入失败，只要满足了最小备份数 `dfs.namenode.replication.min` ，写入也会成功。


### HDFS 的读数据过程

1. 客户端向 namenode 请求下载文件，namenode 通过查询元数据，找到文件数据块所在的 datanode 列表。
2. 客户端挑一台 datanode (就近原则，然后随机)请求传输数据。
3. datanode 传输数据给客户端(并行，多个 block 可以一起读)，以 packet 为单位校验。客户端以 packet 为单位接收到本地缓存，再写入文件。[ps: block 的应答包中不仅包含了数据，还包含了校验值。客户端接收到数据应答包时，会对数据进行校验，如果出现校验错误，客户端就会向 namenode 汇报这个损坏的 block 副本，同时尝试从其他的 datanode 读取这个数据块。]
4. 重复第 3 步直至数据传出完成。


## HDFS 容量伸缩

HDFS 支持动态的扩容、缩容，原有的 namenode 和 datanode 都不需要停止服务。增减节点时，需要对 yarn 的节点也做增减相关的操作。

### HDFS 扩容
#### 横向扩容

首先配置好新增的 datanode 机器。集群所有机器添加新增节点到操作系统的 hosts 文件及 namenode 的 slaves 文件里。[ps: hdfs-site.xml 里 dfs.hosts 若有指定的文件，则须添加上新增节点。]，配置 namenode 到该 datanode 的 ssh 免密码登录。

在新节点上启动新增的 datanode ，集群节点数量增加。 

新加入的节点，没有 block 的存储，集群整体负载不均衡。因此需要对 HDFS 负载均衡。[ps: 注意！Rebalance 是一个相当耗时的操作，并且在这个过程中，数据可能无法正常写入。]

默认 balancer 的阈值为10%(各节点与集群总存储使用率相差不超过10%)，可将其设置为5%:

```sh
sbin/start-balancer.sh -threshold 5
```

默认的数据传输带宽较低，可设置为64MB，修改 hdfs-site.xml 的 `dfs.datanode.balance.bandwidthPerSec` 的值或者执行命令:

```sh
hdfs dfsadmin -setBalancerBandwidth 67108864
```

#### 纵向扩容

将现有的 datanode 硬盘容量扩大。首先将目标 datanode 下线，在机器上新增硬盘，分区、格式化、挂载好后，配置 hdfs-site.xml 的 `dfs.datanode.data.dir` 添加新的本地目录，再重启该 datanode 即可。

### HDFS 缩容
#### 横向缩容

namenode 的 hdfs-site.xml 的 `dfs.hosts.exclude` 指向的文件里，添加要退役的机器IP或 hostname 。

在 namenode 执行命令刷新 namenode :

```sh
hdfs dfsadmin -refreshNodes
```

要退役的节点变为只读，存储的块会移动到其他 datanode 上。

在 HDFS WebUI 页面(或者命令行 hdfs dfsadmin -report)观察、等待要退役的节点状态为 decommissioned ，再关闭该节点[ps: 如果服役的节点少于副本数，则无法退役成功。]，更新集群配置并同步(namenode 的 exclude 文件、slaves 文件，所有节点的 hosts 文件移除退役的节点)，如果有需要还可对 HDFS 再次进行负载均衡。

#### 纵向缩容

移除 datanode 上的硬盘不能直接移除。只能一块一块盘的操作，每移除一块磁盘，都会有若干副本丢失。

首先停止目标 datanode ，修改它的 hdfs-site.xml 的 `dfs.datanode.data.dir` 移除目标本地目录，再重启 datanode 。此时检查集群数据副本状况，会提示 block 损坏的情况和副本的丢失情况。

重新生成副本以达到复制因子，如执行命令:

```sh
# 设副本数为 3
hdfs dfs -setrep 3 -R -w /
```

检查报告看有哪些目录的数据丢失，如果是无关数据则删除掉，如:

```sh
hdfs fsck 目录 -delete
```

每移除一块硬盘都要重复这个过程。
