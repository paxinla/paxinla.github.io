Title: ScalaPB - 在 Scala 中使用 gRPC
Date: 2021-04-16 14:18:29
Category: Scala
Tags: scala, scalapb, mill
CommentId: X


在 Scala 中使用 gRPC 的示例。


<!-- PELICAN_END_SUMMARY -->


## 什么是 gRPC

gRPC 是由 Google 开发并开源的一个跨平台的高性能 RPC 框架，支持多种语言。它基于 HTTP/2 设计，支持双向流、单 TCP 多路复用、服务端推送的特性。使用 protobuf 作为 IDL ，语法简单表达能力强、压缩传输效率高、平台无关。

gRPC 非常适合:

+ 内部服务之间的连接。
+ 连接到公开的 API 。
+ 给移动设备或 Web 提供数据。


要使用 gRPC :

1. 用户需要先用 IDL 定义服务和消息的数据结构(创建 .proto 文件)；
2. 将 .proto 文件编译为目标编程语言的骨架代码(服务端和客户端可以使用不同的编程语言)；
3. 用户实现具体的服务调用/处理逻辑。


## 使用 scalapb

gRPC 虽然支持多种语言，但是并不原生支持 Scala 。[ScalaPB](https://scalapb.github.io/) 是一个 scala 使用 gRPC 衔接的框架。官方网站只有基于 sbt 的例子，特别依赖于 sbt 插件，对使用其他构建工具的用户很不友好。我在本文中将使用 [mill](https://com-lihaoyi.github.io/mill/) 作为构建工具来展示一个简单的 scalapb 示例。

<p class="list-title">项目结构:</p>

<article><header><pre>
GRPCExample
  |
  +-- ServerSample
  |     |-- protobuf
  |     |     +-- hello.proto
  |     +-- src
  |           |-- gRPCServer.scala
  |           +-- HelloServer.scala
  |     
  +-- ClientSample
  |     |-- protobuf
  |     |     +-- hello.proto
  |     +-- src
  |           |-- HelloClient.scala
  |
  +-- build.sc
</pre></header></article>

### 定义服务

hello.proto 内容:

```proto
syntax = "proto3";

import "google/protobuf/wrappers.proto";
import "scalapb/scalapb.proto";

package learn.grpc.services;

service HelloWorld {
  rpc sayHello(ToBeGreeted) returns (Greeting) {}
}

message Person {
  string name = 1;
}

message ToBeGreeted {
  Person person = 1;
  google.protobuf.StringValue msg = 2;
}

message Greeting {
  string message = 1;
}
```


### 服务端

gRPCServer.scala 内容:

```scala
package learn.grpc.server

import io.grpc.{ServerBuilder, ServerServiceDefinition}

trait gRPCServer {
  def runServer(service: ServerServiceDefinition): Unit = {
    // 服务器端没配置 SSL 就是不用 SSL
    val server = ServerBuilder
      .forPort(40032)
      .addService(service)
      .build
      .start

    Runtime.getRuntime.addShutdownHook(new Thread() {
      override def run(): Unit = {
        println("Shutdown server.") 
        server.shutdown()
      }
    })

    println("Start Server.")
    server.awaitTermination()
  }
}
```


HelloServer.scala 内容:

```scala
package learn.grpc.hello.server

import scala.concurrent.{Future, ExecutionContext}

import learn.grpc.services._
import learn.grpc.server.gRPCServer

object HelloServer extends gRPCServer {

  class HelloService extends HelloWorldGrpc.HelloWorld {
    override def sayHello(request: ToBeGreeted): Future[Greeting] = {
      val greeter = request.person match {
        case Some(person) => person.name
        case None => "friend"
      }

      val messageText = request.msg.getOrElse("~No message~")
  
      Future.successful(Greeting(message = s"Hello ${greeter}, ${messageText}"))
    }
  }

  def main(args: Array[String]): Unit = {
    val service = HelloWorldGrpc.bindService(new HelloService, ExecutionContext.global)
    runServer(service)
  }
}
```


### 客户端

HelloClient.scala 内容:

```scala
package learn.grpc.hello.client

import scala.concurrent.Future

import learn.grpc.services._

object HelloClient {
  def main(args: Array[String]): Unit = {
    // 客户端设置 usePlaintext 才是不用 SSL
    val channel = io.grpc.ManagedChannelBuilder
      .forAddress("localhost", 40032)
      .usePlaintext
      .build

    val greeter = ToBeGreeted()
      .withMsg("remote greetings!")
      .withPerson(Person("Doris"))

    val asyncStub: HelloWorldGrpc.HelloWorldStub = HelloWorldGrpc.stub(channel)
    val futureResponse: Future[Greeting] = asyncStub.sayHello(greeter)

    import scala.concurrent.ExecutionContext.Implicits.global
    futureResponse.foreach( greeting => println(greeting.message) )

    val greeter2 = ToBeGreeted(person = Some(Person("Midori")), msg = Some("How are you?"))

    val syncStub: HelloWorldGrpc.HelloWorldBlockingClient = HelloWorldGrpc.blockingStub(channel)
    val response: Greeting = syncStub.sayHello(greeter2)

    println(s"${response.message}")
  }
}
```


### 构建工具

在 mill 中，有专门的 ScalaPBModule 来使用 scalapb 。

build.sc 内容:

```scala
import mill._
import mill.scalalib._

import $ivy.`com.lihaoyi::mill-contrib-scalapblib:$MILL_VERSION`

import mill.contrib.scalapblib._


trait ScalapbSample extends ScalaPBModule {
  def scalaVersion = "2.13.3"
  def scalaPBVersion = "0.9.1"
  def scalaPBFlatPackage = true
  def scalaPBIncludePath = Seq(scalaPBUnpackProto())

  override def ivyDeps = T {
    super.ivyDeps() ++ Agg(
      ivy"io.grpc:grpc-netty:1.37.0"
    )
  }
}

object ServerSample extends ScalapbSample {}

object ClientSample extends ScalapbSample {}
```


### 测试

在 GRPCExample 下执行 `mill -i ServerSample.run` 就会编译并执行服务端代码[ps: 在 Windows 上这个 `-i` 是不可缺少的。]，如果看到类似如下警告信息:

```
F:\testscala\GRPCExample\out\mill\scalalib\ZincWorkerModule\worker\dest\2.13.3\unpacked\xsbt\DelegatingReporter.scala:166: warning: match may not be exhaustive.
It would fail on the following inputs: ERROR, INFO, WARNING
    sev match {
    ^
warning: 4 deprecations
```

这是 mill 的问题，不影响执行结果。如果不想看到这个信息，可以修改 DelegatingReporter.scala 文件，在上面报警告这个地方，为 sev 的模式匹配里添加一条默认的匹配[ps: 比如：`case _  => WARNING` 。]即可。

在 GRPCExample 下执行 `mill -i ClientSample.run` 就会编译并执行客户端代码。可以客户端调用 sayHello 的结果：

```
Hello Midori, How are you?
Hello Doris, remote greetings!
```
