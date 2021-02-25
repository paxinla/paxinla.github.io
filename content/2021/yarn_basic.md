Title: YARN 概览
Date: 2021-02-22 09:27:35
Category: 数据平台
Tags: hadoop, yarn
CommentId: X

<!-- PELICAN_END_SUMMARY -->


## YARN 的设计背景

[Apache Hadoop YARN](https://hadoop.apache.org/docs/current/hadoop-yarn/hadoop-yarn-site/YARN.html) 是 Hadoop 的统一资源管理和调度平台，让各种不同的计算框架(如：MapReduce、 Spark 等)能通过它共享一个分布式集群的资源。YARN 是 Hadoop 2 开始引入的，最初是从 MapReduce 中剥离出来以达到应用程序管理与资源管理两部分分离的目的，所以也叫 MRv2 。与它的竞争对手 [Apache Mesos](http://mesos.apache.org/) 相比，YARN 不需要接入的计算框架事先部署在 YARN 中，它们是作为客户端的库来使用，运行、升级和使用上更方便。

<p class="list-title">YARN 的特性:</p>

1. 支持多种计算框架。YARN 提供了一个全局的资源调度器，所有接入的计算框架需要先向该全局资源管理器申请资源，申请成功之后，再由框架自身的调度器决定资源交由哪个任务使用，也就是说，整个大的系统是个双层调度器，第一层是统一管理和调度平台提供的，另外一层是框架自身的调度器。YARN 提供了资源隔离机制，避免不同的框架运行在同一个集群中由于资源争用导致的效率下降。
2. 扩展性。YARN 支持系统的线性扩展。
3. 容错性。YARN 在保持原有计算框架的容错特性基础上，自身也有良好的容错性。
4. 支持多租户，高资源利用率。
5. 细粒度的资源分配。资源分配的对象是 Task ，不是 Job, Framework 或 Application 。这有利于高资源利用率、快速的响应时间和好的数据本地性。


## YARN 的架构

YARN 是一个典型的 master/slave 架构。master 节点主要负责全局的资源分配及对 slave 节点的管理，slave 节点主要负责本节点的各项信息收集、汇报，本节点上资源的分配工作。最重要的组成是 Resource Manager, Node Manager, Container 和 Application Master 。

### Resource Manager

Resource Manager 是整个集群的资源管理者，负责整个集群的资源管理和任务分配，它又由两个组件构成，分别是调度器(Scheduler)和应用程序管理器(Application Manager)。

Scheduler 负责将系统资源分配给各个正在运行的应用程序，它不参与任何与具体应用相关的工作，如监控应用或跟踪其执行状态，也不负责重启失败的任务，仅根据各个应用程序的资源需求进行资源分配。

Application Manager 负责管理整个集群中的所有应用程序，包括应用程序提交、与 Scheduler 协商资源以启动 Application Master ，监控 Application Master 的状态以及在任务失败时重新启动 Application Master 。

Resource Manager 有一个 Active Resource Manager 和一个 Standby Resource Manager 。

Resource Manager 通过 RMStateStore 来存储内部数据、主要应用数据和标记等。

#### Zookeeper Failover Controller

和 HDFS 不同，ZKFC 是嵌入在 Resource Manager 的一个服务，而不是一个独立进程存在的。ZKFC 负责监控 Resource Manager 的健康状况并定期向 Zookeeper 发送心跳。


### Node Manager

Node Manager 是每个节点上的资源和任务管理器，一方面，它会定时地向 Resource Manager 汇报本节点上的资源使用情况和各个 Container 的运行状态；另一方面，它接收并处理来自 Application Master 的 Container 启动/停止等各种请求。

Node Manager 启动时向 Resource Manager 注册，注册信息中就包含了该节点可分配的 CPU 和内存总量。参见 yarn-site.xml 的参数：

- `yarn.nodemanager.resource.memory-mb` : 可分配的物理内存总量，默认是8GB，不会动态调整。
- `yarn.nodemanager.resource.cpu-vcores` : 可分配的虚拟CPU个数，默认是8，不会动态调整。[ps: 为了更细粒度地划分CPU资源，YARN 允许管理员将每个物理CPU划分为若干个虚拟CPU，用户提交应用程序时也可指定每个任务需要的虚拟CPU数量。vcore 的数量直接影响单个 Node Manager 能分配的 Container 数量。]
- `yarn.nodemanager.vmem-pmem-ratio` : 任务使用单位物理内存量对应最多可用的虚拟内存，默认时2.1，表示使用1MB的物理内存，最多可用2.1MB的虚拟内存总量。
- `yarn.nodemanager.pmem-check-enabled` : 是否启动一个线程检查每个任务正使用的物理内存量，如果任务超出分配值，则直接将其杀掉，默认是 true 。
- `yarn.nodemanager.vmem-check-enabled` : 是否启动一个线程检查每个任务正使用的虚拟内存量，如果任务超出分配值，则直接将其杀掉，默认是 true 。

### Container

Container是 YARN 中的资源抽象，它封装了某个节点上的多维度资源，如内存、CPU、磁盘、网络等，当 Application Master 向 Resource Manager 申请资源时，Resource Manager 为 Application Master 返回的资源便是用 Container 表示。YARN 会为每个任务分配一个 Container ，且该任务只能使用该 Container 中描述的资源。实际运行时，每一个 Container 就是一个独立的 JVM 实例。

- `yarn.scheduler.minimum-allocation-mb` : 可申请的最少内存资源，默认1GB。
- `yarn.scheduler.maximum-allocation-mb` : 可申请的最多内存资源，默认8GB。
- `yarn.scheduler.minimum-allocation-vcores` : 可申请的最少虚拟CPU数量，默认1。
- `yarn.scheduler.maximum-allocation-vcores` : 可申请的最多虚拟CPU数量，默认32。

### Application Master

Resource Manager 对每一个提交到 YARN 的 Application ，都会从集群中选择一个 Node Manager 启动一个 Container  来运行一个 Application Master 来负责这个 Application 的任务执行的资源分配、生命周期监控等工作。Application Master 与 Resource Manager 和 Node Manager 都有交互：向 Resource Manager 申请资源，请求 Node Manager 启动或停止 task 。

每个 Application 都有自己的 Application Master ，每个 Application Master 只负责自己的资源调度，整个集群所有在运行的 Application 的 Application Master 不会集中在一个节点上。 

### JobHistory Server 和 Timeline Server

JobHistory Server 是查看 YARN 已经完成的 MapReduce 任务的历史日志记录的服务。需要管理员配置和启动该服务。

Timeline Server 记录与展示所有运行在 YARN 上的任务的通用数据。需要管理员配置和启动该服务。

JobHistory Server 所完成的功能只是 Timeline Server 的一部分。


### 资源调度

YARN 是两层调度模型。Resource Manager 将资源分配给 Application Master ，后者再进一步将资源分配给它的内部任务。

YARN 的资源分配是异步的，资源调度器将资源分配给一个 Application 后，会暂时放到一个缓冲区，待 Application Master 通过周期性的心跳来主动获取。

YARN 采用增量资源分配机制，当 Application 申请的资源暂时无法保证时，预留一个节点上的资源直到累计释放的空闲资源满足需求，这会造成浪费，但会避免饿死现象。

<p class="list-title">YARN 支持的调度语义:</p>

- 请求某个机架上的特定资源量。
- 请求某个节点上的特定资源量。
- 拉黑某些节点，不再为自己分配这些节点上的资源。
- 请求归还某些资源。

<p class="list-title">YARN 不支持的调度语义:</p>

- 请求任意机架上的特定资源量。
- 请求任意节点上的特定资源量。
- 请求符合某种条件的资源。
- 超细粒度资源，如CPU性能要求、绑定CPU等。
- 动态调整 Container 资源，允许根据需要动态调整 Container 资源量。

#### 资源调度器

YARN 资源调度器提供了三种资源调度器：FIFO Scheduler、 Capacity Scheduler 和 Fair Scheduler 。通过 yarn-site.xml 的参数 `yarn.resourcemanager.scheduler.class` 指定。这三种方式都是按照层级队列方式组织资源。用户也可按照接口规范编写自己的资源调度器。

##### FIFO Scheduler

FIFO Scheduler 是 Hadoop 设计之初提供的一个最简单的调度机制：即先来先服务。所有应用程序被统一提交到一个队列中，按照提交顺序依次被运行。只有等先来的应用程序资源满足后，才开始为下一个应用程序进行调度运行和分配资源。

应用程序并发度低；所有任务只能照同一个优先级处理；无法适应多租户资源管理，容易阻塞、造成饥饿现象。

##### Capacity Scheduler

Capacity Scheduler 是 Apache Hadoop 2.x 默认的资源调度器，以队列为单位划分资源。每个队列可设定一定比例的资源最低保证和使用上限。每个用户也可设置一定的资源使用上限，以防资源滥用。并支持资源共享，将队列剩余资源共享给其他队列使用。它基于一个很朴素的思想：每个用户都可以使用特定量的资源，但集群空闲时，也可以使用整个集群的资源。

<p class="list-title">Capacity Scheduler 特点:</p>

- 资源的层次化管理。通过层次化的队列设计保证了子队列可以使用父队列设置的全部资源，更容易合理分配和限制资源的使用。
- 弹性调度。如果队列中的资源有剩余或空闲，可暂时共享给其他有需要的队列(同父队列的子队列)。当该队列有新的应用程序需要资源运行时，则其他队列释放的资源会归还给该队列(非强制回收)。弹性灵活地分配调度资源。
- 提高多租户并行度。支持多用户共享集群资源和多应用程序同时运行。
- 资源隔离。可对每个用户可用资源设置上限。每个队列设置严格的 ACL ，用户只能向自己的队列里提交任务，而不能访问其他队列的任务。

为什么叫容量调度？队列资源采用容量占比的方式进行分配；队列间的资源分配算法也是采用最小资源使用率；每个用户的资源限制是资源量占比。

Capacity Scheduler 不支持抢占式调度，必须等上一个任务主动释放资源。

##### Fair Scheduler

Fair Scheduler 是 CDH 默认的资源调度器，根据队列的权重属性自动分配资源。它能在不饿死长作业的同时(可能不能及时获取到所有需要的资源)，优先让短作业先运行完成。Fair Scheduler 的队列根据权重(这个权重就是对公平的定义)大小来决定如何优先分配资源，同时也支持设置每个队列能使用的最小资源、最大资源、同时运行的最大应用程序数量。

<p class="list-title">Fair Scheduler 特点:</p>

- 资源公平共享。同一队列中的作业公平共享队列中的所有资源，不同队列中的作业按权重作为优先级分配资源，优先级越高分配越多。在资源有限的情况下，作业的资源缺额越大越优先执行。[ps: 每个作业需要的资源和实际获得的资源的差值叫做资源缺额。]多个任务可以同时运行。
- 调度策略配置灵活。每个队列中，Fair Scheduler 可选择 FIFO, fair(默认策略，基于内存的) 或 DRF(dominant resource fairness ，CDH的默认策略，基于vcore和内存) 策略为应用程序分配资源。
- 支持资源抢占。队列空闲资源被共享给其他队列后，如果再提交用户程序，需要计算资源，调度器需要为它回收资源。为了尽可能降低不必要的计算浪费，调度器采用了先等待再强制回收的策略。如果等待一段时间后尚有未归还的资源，则会进行资源抢占：从超额使用资源的队列中杀死一部分任务，进而释放资源。
- 负载均衡。Fair Scheduler 尽可能把系统中的任务均匀分配到各个节点上。

#### Node Label

Node Label 是一个为了给异构的集群机器分组的解决方案。因为公司的集群机器可能是在不同的时间不同来源加入的，所以随着时间推移，同一个集群中的机器配置往往不同。那么就可以配置分组，比如机器组 A 用来跑 MapReduce ，机器组 B 用来跑 Spark  ，机器组 C 用来跑 AI/ML 任务等。

Label 需要关联到 Queue 上，一个 Application 只能使用一个 Queue 下的一个 Label 。

使用这个方案需要在 HDFS 上创建一个专门用于存放标签的目录，给每一台机器打标签。

### YARN 的容错机制

1. 避免单点故障。每个 Application 都有自己的 Application Master ，一个计算程序的失败不会影响到另一个计算程序，而且 YARN 支持 Application Master 失败重试。
2. 减轻调度压力。每个 Application Master 只负责自己的资源调度，而且每个 Application Master 是启动在不同的节点上，降低了任务执行失败的风险。
3. 降低集成耦合度。YARN 只负责资源管理，不负责具体的任务调度，只要计算框架继承了 YARN 的 Application Master ，都可以使用一个统一资源的视图。

YARN 中的 application 在运行失败时有几次重试机会，重试失败则作业运行失败。Resource Manager 检测到 Application Master 失败时在一个新的容器开始一个新的 Application Master 实例。 Application Master 最大重试次数由参数 `yarn.resourcemanager.am.max-attempts` 设置，默认是2。

如果一个 Node Manager 上运行的任务失败次数过多，即使 Node Manager 自己并没有失败过，Application Master 也会拉黑它，尽量将任务调度到不同的节点上。Resource Manager 如果长时间没有收到 Node Manager 的心跳，也会将它从自己的节点池中移除。


## X on YARN

程序/框架只要实现了 Application Master 和资源申请模块，就可以运行在 YARN 上。

<p class="list-title">对提交到 YARN 的应用，YARN 的一般调度步骤：</p>

1. 客户端提交应用信息(包括代码及一切需要的参数和环境信息)到 Resource Manager 。
2. Resource Manager 向 Node Manager 申请一个 Container ，并要求 Container 启动 Application Master 。
3. Application Master 启动后将自己注册到 Resource Manager ，为自己的 Task 申请 Container 。Resource Manager 收到请求后，选择 Node Manager 要求分配资源。
4. 资源分配完毕后， Application Master 发送请求给 Node Manager 启动任务。
5. Node Manager 设置 Container 的运行时环境(如：jar包、环境变量、任务启动脚本)， Node Manager 的 ContainerLauncher 会通过脚本启动任务。
6. 任务执行过程中，task 向 Application Master 汇报任务状态和进度信息，如任务启停、状态更新，Application Master 利用这些信息监控 task 整个执行过程。同时，Node Manager 和 Resource Manager 保持心跳信息。
7. Application Master 在检测到作业运行完毕后，向 Resource Manager 删除自己并停止自己。

### MapReduce on YARN

1. MapReduce 程序提交到客户端所在节点，客户端向 Resource Manager 申请运行 Application 。
2. Resource Manager 将该 Application 的资源路径及 application id 返回给客户端。
3. 客户端将运行所需资源上传到 HDFS 上，申请 mrAppMaster 。
4. Resource Manager 选择一个 Node Manager 创建 Container 并产生 mrAppMaster 。
5. mrAppMaster 向 Resource Manager 申请运行 map task 容器。
6. Resource Manager 分配几个 Node Manager 创建 Container 。mrAppMaster 向这些 Node Manager 发送程序启动脚本，Node Manager 启动 map task ，计算数据、分区排序。
7. mrAppMaster 向 Resource Manager 申请运行 reduce task 容器。
8. reduce task 向 map task 获取相应分区的数据，计算数据。
9. 程序运行完成，mrAppMaster 向 Resource Manager 注销自己并释放资源。

### Spark on YARN

1. 客户端提交一个 Application ，Resource Manager 将该 Application 的资源路径及 application id 返回给客户端，客户端将运行所需资源上传到 HDFS 上。 yarn-client 模式下，客户端启动一个 driver 进程，driver 进程向 Resource Manager 申请 Application Master ； yarn-cluster 模式下，客户端向 Resource Manager 申请 Application Master 。
2. Resource Manager 选择一个 Node Manager 创建 Container 并产生 Application Master 。在 yarn-client 模式下，Application Master 只是负责启动 Executor ，Executor 启动后是与客户端的 driver 进行交互的；在 yarn-cluster 模式下，Application Master 上运行 driver 。
3. Application Master 向 Resource Manager 申请 Container 资源。
4. Resource Manager 分配几个 Node Manager 创建 Container 。Application Master 向 Node Manager 发送命令启动 Executor 。
5. Executor 启动后反向注册到 driver ， driver 发送 task 到 Executor ，执行情况和结果返回给 driver 。
6. 程序运行完成，Application Master 向 Resource Manager 注销自己并释放资源。

