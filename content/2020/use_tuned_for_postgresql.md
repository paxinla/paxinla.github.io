Title: 使用 tuned 动态调节 Linux 系统参数
Date: 2020-07-30 15:48:39
Category: 工具
Tags: postgresql, tuned
CommentId: X

ReadHat 提供了一个自动对系统参数(不用手工编辑 sysctl.conf )调优的工具 — `tuned` 。本文记录了我在 PostgreSQL 服务器上使用 tuned 的情况。

<!-- PELICAN_END_SUMMARY -->

## 安装

在基于 ReadHat 的发行版上，通常 tuned 都已经安装好了。如果系统尚未安装，则执行 `yum install tuned` (基于 Debian 的发行版上则是 `apt-get install tuned`)安装就好。

安装完成后就可以通过 systemd 来管理 tuned 服务。tuned 自带管理工具 `tuned-adm` 来管理各种系统参数调优的规则。

- `tuned-adm list` ，列出所有可用的 profiles 。
- `tuned-adm active` ，显示当前激活的 profile 。
- `tuned-adm profie SomeProfileName` ，激活对应的 profile 。

## Profile

![tuned-profile](/images/2020/tuned_inheritance.jpg)

tuned 的配置文件一般在 `/etc/tuned` 下。tuned 预置了一些常见系统的参数调优规则文件，一般在 `/usr/lib/tuned` 下。这些预置的系统规则可以用 `tuned-adm list` 列出。

在 `/etc/tuned` 下新建目录 `postgresql` ，在这个目录下新建配置文件 **tuned.conf** ，添加如下内容:

```ini
[main]
include=throughput-performance
summary=Optimize for PostgreSQL RDBMS

[vm]
transparent_hugepage=never

[sysctl]
fs.aio-max-nr=1048576
fs.file-max=76724600
fs.nr_open=20480000
kernel.core_pattern=/data/corefiles/core_%e_%u_%t_%s.%p
kernel.sched_autogroup_enabled=0
kernel.sched_migration_cost_ns=50000000
vm.dirty_background_bytes=134217728
vm.dirty_expire_centisecs=499
vm.dirty_ratio=90
vm.overcommit_memory=2
vm.overcommit_ratio=90
vm.swappiness=0
vm.zone_reclaim_mode=0
```

现在执行 `tuned-adm list` 就可以看到新加的 postgresql tuning profile 了。使用 `tuned-adm profile postgresql` 就可以应用新加的 postgresql tuning profile 。

编辑 `/etc/tuned/tuned-main.conf` ，修改 `dynamic_tuning = 1` ，则启用动态调优。在 `/var/log/tuned` 下可以看到 tuned 调优操作的日志。
