Title: 未安装 Oozie Server 共享库
Date: 2018-03-19 14:52:59
Category: 数据平台
Tags: hadoop, oozie, extjs
CommentId: 8


Cloudera Manager 里报 “存在隐患 : 未安装 Oozie Server 共享库。”

<!-- PELICAN_END_SUMMARY -->

　　CDH 对 oozie 有个 “Oozie Server 共享库检查”的测试，可使用 启用 Oozie Server 共享库版本检查 Oozie Server 监控设置来启用或禁用该测试。最近突然报“未安装 Oozie Server 共享库”的警告。这个警告实际上是因为“Oozie Server”实例所在机器上缺少 **ext-2.2.zip** 所致。

　　下载 **ext-2.2.zip** [ps: 官网现在已经不提供下载了，可以到 http://archive.cloudera.com/gplextras/misc/ext-2.2.zip 下] 解压到 “Oozie Server”实例所在机器的 `/var/lib/oozie` 目录[ps: parcel方式安装的CDH目录我一般放在 /opt 目录下，所以 `/opt/cloudera/parcels/CDH/lib/oozie/libext` 指向的也是 `/var/lib/oozie` ]下，以使链接 `/var/lib/oozie/tomcat-deployment/webapps/oozie` 生效，注意目录 `/var/lib/oozie/ext-2.2` 的属主要设为 oozie:oozie 。

　　在 Cloudera Manager 的 Oozie 服务页里，点“操作”->“安装 Oozie 共享库”，待命令执行完成。

　　重启 Oozie 服务，警报消失。
