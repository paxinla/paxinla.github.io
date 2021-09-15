Title: 使用 Maven 镜像的坑
Date: 2021-09-12 09:27:33
Category: 故障
Tags: windows, jar, maven, scala, sbt
CommentId: X


众所周知，在国内下载 maven 等依赖需要配置包管理软件使用 maven 镜像，才能得到尚可忍受的下载速度。

<!-- PELICAN_END_SUMMARY -->


## 基于 sbt 的方案

可以通过修改 `$HOME/.sbt/repositories` 文件[ps: Windows 上 HOME 目录通常指 C:\\Users\\你的系统用户名 。]来添加下载依赖的镜像列表，我一般用的如下:

```
[repositories]
local
aliyun: https://maven.aliyun.com/repository/public
typesafe: https://repo.typesafe.com/typesafe/ivy-releases/, [organization]/[module]/(scala_[scalaVersion]/)(sbt_[sbtVersion]/)[revision]/[type]s/[artifact](-[classifier]).[ext], bootOnly
ivy-sbt-plugin:https://dl.bintray.com/sbt/sbt-plugin-releases/, [organization]/[module]/(scala_[scalaVersion]/)(sbt_[sbtVersion]/)[revision]/[type]s/[artifact](-[classifier]).[ext]
sonatype-oss-releases
maven-central
sonatype-oss-snapshots
```

国内镜像主要用的是阿里云的镜像，毕竟财大气粗，也许维护得比其他友商好些。具体地址最好还是参考 [官方使用指南](https://developer.aliyun.com/mvn/guide) ，而不是抄简中网上搜索到的过时地址。

像 sbt、Ammonite、Mill 等工具，一般会使用本地已经缓存的依赖文件，这样可以不用每次构建时都重新下载。但是有的时候，即使第一次下载的依赖文件是有问题的，这些工具也不会删除缓存的有问题的依赖文件，重新下载；而是继续使用有问题的依赖文件来参与构建项目，在编译的时候报错信息也不提及依赖文件的正确性验证结果。这就会误导用户以为是依赖的第三方库有问题，比如版本号错误或者新版本作了不兼容的修改等，实际上只不过是下载的第三库文件有问题而已。

为了使这些工具重新下载已缓存的依赖文件，最简单直观的方案就是删掉已缓存的依赖文件。

缓存的依赖文件，除了一般常见的 `$HOME/.ivy/cache` 、 `$HOME/.ivy/local` 和 `$HOME/.m2/repository` 这些位置外，由于很多 Scala 的构建工具还会使用 [Coursier](https://get-coursier.io) 来下载依赖文件，还应检查 `$HOME/.cache/coursier/v1  (on Linux)` 或 `C:\Users\你的系统用户名\AppData\Local\Coursier\cache\v1  (on Windows)` 。


