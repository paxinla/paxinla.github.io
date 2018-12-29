Title: 用 riemann 监控 PostgreSQL
Date: 2018-08-20 14:43:38
Category: 工具
Tags: riemann, postgresql
CommentId: 12


## PostgreSQL 的监控工具真的不够用

传统的运维工具如: Zabbix、Ganglia 等，所提供的监控 PostgreSQL 的插件，默认监控的指标都太过简单。如果你想要监控更多的指标，则必须根据它们特有的配置语法来定制数据库查询，这些配置语法当然没有代码灵活。像 Promethus 之类的方案，倒是可以满足我容易制作 Dashboard 的需求。但这些方案依赖的组件太多，配置还是稍显麻烦。[ps: 特别是它的 postgres_exporter 我硬是没编译成功过。]对收费的监控工具，我总觉得没达到 Oracle Enterprise Manager 的水准，就不太想用。像 pg_activity 、pgcenter 这类工具又是命令行的 UI ，不方便向非 DBA 人群展示信息。

除了外部工具对 PostgreSQL 的针对性不强外，PostgreSQL 本身的监控数据也不太好用。像完全访问 pg_stat_activity、pg_stat_replication 需要 superuser 角色，[ps: 从 10 版本起，有了像 pg_monitor、pg_read_all_stats 等角色可以用来赋给非 superuser 的监控用户]缺乏足够多的易用的监控视图等[ps: 像 Oracle 的 V<span>$</span> 视图之于 X<span>$</span> 表]。

我对 PostgreSQL 的监控工具有以下的期望:

1. 它要么本身高度专业，对数据库收集足够丰富的指标；要么足够灵活，允许我容易地将自行收集的监控数据发送给它存储、处理。
2. 它应当易于部署。尽量少的依赖组件，尽量简单的配置。
3. 它应当有一个易用的 Dashboard 来展示存储/处理的指标，以便向数据库管理员之外的人展示。
4. 它应当易于集成外部的程序，以便实现发送报警邮件、向其他系统如 Kafka 、Elasticsearch 、InfluxDB 发送自己收到的指标数据。

<!-- PELICAN_END_SUMMARY -->

## 为什么是 Riemann

[Riemann](http://riemann.io) 是一个事件流处理器。它足够轻量，我使用的是它的预编译二进制文件，没有其他的依赖。它的配置文件就是一个 clojure 程序，如果我需要添加自定义的功能，只需要编写普通的 clojure 代码，并在配置文件中引入即可。[ps: 当然，这需要 JRE 。]没有什么特别的 DSL ，就是 clojure 代码。Riemann 本身的处理逻辑非常简单，就是将接收到的 event (包裹了监控数据的容器) 根据配置文件中的代码分发到各个用户定义的子 stream 中。用户在子 stream 中使用 riemman 提供的 API 及自己的 clojure 代码处理 event ，决定哪些/什么样的 event 进入到最终存储的表 index 中。

需要展示 Dashboard ，用[Riemann-dash](http://riemann.io/dashboard.html) 可以读取并展示 index 中的数据。

需要将 riemann 的监控数据共享给其他系统[ps: Riemann 自带易用的发送邮件 API 。]，在配置文件里设置[向这些系统发送 event 的子 stream](http://riemann.io/howto.html#integrating-with-other-systems) 即可。

我使用了 python 读取 PostgreSQL 的监控数据，sqlalchemy 查询数据库指标，psutil 查询系统指标，bernhard 发送监控数据给 riemann 。riemann 所需要的 event 就是一个具有特别字段的 map 而已。[ps: riemann 支持许多语言的 client: http://riemann.io/clients.html] 我可以在自己的程序里先行做一定的计算，再将结果组装为 python 的 dict ，即可发送给 riemann 。


## 一点心得

官方文档对 riemann 的配置文件已有说明，我自用的一个示例文件[在这里](https://gist.github.com/paxinla/39e19a4d30f4bb74c87c5dacc884165d)。下面记录些官方文档没详细说明的。

### riemann-dash 里 metric 的颜色

在 riemann-dash 的面板里，metric 的颜色有灰色、绿色、黄色和红色共4种，它取决于这个 event 的 state 字段的值。当 state 为 "ok" 时，显示绿色；当 state 为 "warning" 时，显示黄色；当 state 为 "critical" 时，显示红色；其他任意值，都显示灰色。[ps: state 的值默认是 nil ，所以默认显示的是灰色。]

### 自定义 event 的字段

发送给 riemann 的 event 只要满足 http://riemann.io/concepts.html 上的 Event 表格里的字段即可，必需的字段只有 host、service、metric ，其他的字段都是可选的。注意，这里只有 tags 字段可以有多个值，这些值的顺序在到达 riemann 后是保留的。官方文档声称可以随意加上自定义的字段。我实际使用时发现似乎不可行，event 到了 riemann 后自定义的字段就丢失了。自定义字段通常都是字符串，因此我都将自定义的字段值放到 tags 字段里。在 riemann 的配置代码中，再提取出来使用。

在 riemann 中往 index 输出的 event ，这里加上的自定义字段是会保留的(还可以改写 tags 字段的值)，可以在 riemann-dash 里的使用。[ps: 一般是在图表的 row 部分使用，因为 column 只能是 host 或 service ]。比如 tags 字段中具有相同值的不同 service 的数据可以展现到一个图表中，达到官方网站上 dashboard 示例里的多列的图表效果。

### riemann-dash 的配置

riemann-dash 有 ruby 的依赖，不一定能部署在 riemann 所在机器上。 riemann-dash 和 riemann 不是一定要部署在同一台机器上的，在 riemann-dash 的面板的右上角，可以输入 riemann 监听的地址和端口，去读取 riemann 的数据。

系统包安装的 riemann-dash 的配置文件通常在 `/usr/local/lib` 或 `/var/lib` 下的 `ruby/gems/<gem的版本号>/gems/riemann-dash-<riemann-dash版本号>` 目录下。复制这下面的 `example/config.rb` 到别处，用 `riemann-dash /SomePath/config.rb` 来启动 riemann-dash 。

riemann-dash 里的图表布局是通过键盘在初始面板里划分出来的，最后结果存储在一个 json 文件中，位置在上面提到的路径下[ps: 如果在浏览器里按 s 保存时提示无法保存，则需要检查 riemann-dash 配置路径下 config 目录的权限是否正确设置。]。把这个 json 文件复制到其他机器上的 riemann-dash 可读的路径下，修改 riemann-dash 的配置文件 config.rb ，修改 `config.store[:ws_config]` 的值为生成的布局 json 文件的路径，即可在这台机器的 riemann-dash 面板上获得同样的图表布局。
