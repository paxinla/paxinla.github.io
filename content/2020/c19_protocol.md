Title: C19 协议简介
Date: 2020-12-22 16:41:56
Category: 分布式
Tags: protocol, gossip, c19
CommentId: X

[C19 Protocol](https://c19p.github.io) 是一个在分布式系统中同步状态的协议。

<!-- PELICAN_END_SUMMARY -->

C19 协议是 Gossip 协议的一个变种。Gossip 协议主要用在分布式系统中各节点同步数据，这些组成网络的节点都是对等节点，是非结构化网络。Gossip 协议是一种最终一致性的协议。C19 代理之间同步状态也是有 Push、Pull 模式。

C19 网络是没有中心节点的，多个节点可以组成一个 group ，在同一个 group 中，状态是一致的。但是目前官方文档中没有提到具体如何划分 group 。

一个 C19 Agent 有3个部分(layers)：agent, stat 及 connection 。3个部分的实现是独立的，不需要考虑其他部分具体使用了哪种类型的实现。

+ 代理(agent)负责与我们的应用交互，是我们读写 C19 中状态的接口。
+ 状态(state)负责存储管理数据。
+ 连接(connection)负责各代理之间的通信。

目前 C19 0.1 的版本只有 Default 类型的 State ，它存储格式为 key-value ，key 必须是字符串，value 是 JSON (带有 "value" 字段)。

目前 C19 0.1 的版本只有 Default 类型的 Agent ，它是一个接收 HTTP 请求的服务器，期望请求的数据部分是一个 JSON 对象，默认端口为 3097 。 [ps: Docker镜像: https://hub.docker.com/r/c19p/c19]

目前 C19 0.1 的版本只有 Default 类型的 Connection ，它连接到随机选择的 peers 来同步状态。peer provider 只有 K8s 和 Static 两种，不使用 Kubernetes 部署时只能采用 Static ，这需要在配置文件里硬编码所有的 peer 的 IP 地址。

C19 的配置文件是 YAML 格式的，启动 C19 程序时可以用 `--config` 选项指定配置文件。

配置文件样例:

```yaml
version: 0.1
spec:
  agent:
    # Default 类型的 agent 提供 HTTP 服务器，接收 JSON 格式的消息。
    kind: Default
    port: 3097
  state:
    # Default 类型的 state 提供 key-value 格式的存储，key 可以带 ttl 。
    kind: Default
    ttl: null
    # 单位是毫秒。
    purge_interval: 60000
    # 这是个可选项，当 agent 启动时可以从这里读取数据。
    # 目前 C19 0.1 的版本只有 File 类型的 Data Seeder 。
    data_seeder:
      kind: File
      filename: data.json
  connection:
    # Default 类型的 connection 使用 HTTP 来通信。
    kind: Default
    port: 4097
    # 对 Static 的 provider ，如果没指定 target_port
    # 在 peers 里地址的格式就应为 IP:Port
    target_port: 4097
    # 单位是毫秒。
    push_interval: 1000
    # 单位是毫秒。
    pull_interval: 60000
    # 每次发布消息给几个 agent 。
    r0: 3
    # 每次连接的超时，单位是毫秒。
    timeout: 100
    # 默认的 provider 是 K8s
    peer_provider:
      kind: Static
      peers:
        - 192.168.1.2
        - 192.168.86.204
```

在一个节点设置状态:
```sh
curl -X PUT localhost:3097/ -d '{"cat": {"value": "miaomiao"}}'
```

在其他节点获取到同样的状态:
```sh
curl -X GET another_host:3097/cat

# 得到 {"value":"miaomiao","ts":1603548753122,"ttl":null}
```

访问 connection 的端口可以获得所有的状态:
```sh
curl -s localhost:4097
```

如果设置状态时，有设置 ttl ，则在足够长的时间后尝试获取该 key 的值，会得到 `not found(404)` 。


目前 C19 协议还在 WIP 。

