Title: Thrift - 在 Scala 中使用 Thrift RPC
Date: 2021-05-09 15:33:18
Category: Scala
Tags: scala, thrift, mill
CommentId: X


在 Scala 中使用 Thrift RPC 的示例。


<!-- PELICAN_END_SUMMARY -->


## 什么是 Thrift

[Apache Thrift](https://thrift.apache.org/) 是一种接口描述语言和二进制通讯协议，它被用来定义和创建跨语言的服务。它最初是由 Facebook 为“大规模跨语言服务开发”而开发的，现在是 Apache 的开源项目。

Thrift 的特点:

+ 使用二进制格式，跨语言序列化的代价较低。
+ 数据结构与传输表现分离，支持多种消息格式。
+ 支持丰富的数据类型，性能优异。
+ 很多开源项目都支持 thrift 。


## 使用 Thrift

Apache Thrift 可以作为 RPC 框架，也可作为序列化/反序列化工具来使用。

Apache Thrift 虽然支持多种语言，但是并不原生支持 Scala 。我在本文中将使用 [mill](https://com-lihaoyi.github.io/mill/) 作为构建工具来展示一个简单的使用 Thrift 作为 RPC 的示例。本文的例子使用与[gRPC例子](https://paxinla.github.io/posts/2021/04/scalapb-zai-scala-zhong-shi-yong-grpc.html)相似的结构。


<p class="list-title">项目结构:</p>

<article><header><pre>
ThriftExample
  |
  +-- ServerExample
  |     |-- resources
  |     |     +-- hello.thrift
  |     +-- src
  |           |-- RPCServer.scala
  |           +-- HelloServer.scala
  |     
  +-- ClientExample
  |     |-- resources
  |     |     +-- hello.thrift
  |     +-- src
  |           +-- HelloClient.scala
  |
  +-- build.sc
  |
  +-- lib
       +-- thrift-0.14.1.exe
</pre></header></article>


### 定义服务

hello.thrift 内容:

```thrift
namespace java learn.thrift.services

struct Person {
  1:  string  name
}

struct ToBeGreeted {
  1:  Person  person,
  2:  string  msg
}

struct Greeting {
  1:  string  message
}

service HelloWorld {
  Greeting sayHello(1:ToBeGreeted request)
}
```


### 服务端

RPCServer.scala 内容:

```scala
package learn.thrift.server

import java.net.InetSocketAddress

import org.apache.thrift.TProcessor
import org.apache.thrift.protocol.TBinaryProtocol
import org.apache.thrift.server.TServer
import org.apache.thrift.server.TServer.Args
import org.apache.thrift.server.TSimpleServer
import org.apache.thrift.transport.TServerSocket
import org.apache.thrift.transport.TServerTransport


trait RPCServer {
  def runServer(
    processor: TProcessor,
    address: InetSocketAddress
  ): Unit = {
    val serverTransport: TServerTransport = new TServerSocket(address)
    val serverArgs: Args = new Args(serverTransport)
    serverArgs.processor(processor)
    serverArgs.protocolFactory(new TBinaryProtocol.Factory())
    // TSimpleServer 简单地阻塞IO，一次只能接收和处理一个 Socket 连接。
    val server: TServer = new TSimpleServer(serverArgs)
    println("Start Server.") 

    Runtime.getRuntime.addShutdownHook(new Thread() {
      override def run(): Unit = {
        println("Shutdown server.")
        server.stop()
      }
    })

    server.serve()
  }
}
```


HelloServer.scala 内容:

```scala
package learn.thrift.hello.server

import java.net.InetSocketAddress

import learn.thrift.server.RPCServer
import learn.thrift.services._


object HelloServer extends RPCServer {

  class HelloService extends HelloWorld.Iface {
    override def sayHello(request: ToBeGreeted): Greeting = {
      val greeter = request.getPerson() match {
        case aperson: Person => aperson.getName()
        case _ => "friend"
      }

      val messageText = request.getMsg().toString match {
        case msg if msg.length > 0 => msg
        case _ => "~No message~"
      }

      val greeting = new Greeting(s"Hello ${greeter}, ${messageText}")
      greeting
    }
  }

  def main(args: Array[String]): Unit = {
    val serviceHandler = new HelloService()
    val serviceProcessor = new HelloWorld.Processor(serviceHandler)

    runServer(serviceProcessor, new InetSocketAddress("127.0.0.1", 40032))
  }
}
```


### 客户端

HelloClient.scala 内容:

```scala
package learn.thrift.hello.client

import scala.util.{Try, Success, Failure}

import org.apache.thrift.transport.TTransport
import org.apache.thrift.transport.TSocket
import org.apache.thrift.protocol.TBinaryProtocol
import org.apache.thrift.protocol.TProtocol

import learn.thrift.services._


object HelloClient {
  def main(args: Array[String]): Unit = {

    val tsocket: TSocket = new TSocket("127.0.0.1", 40032)
    tsocket.setTimeout(3000)
    val transport: TTransport = tsocket
    transport.open()

    val callRpcResult = Try {
      val protocol: TProtocol = new TBinaryProtocol(transport)
      val syncStub: HelloWorld.Client = new HelloWorld.Client(protocol)

      val greeter = new ToBeGreeted()
      greeter.setPerson(new Person("Doris"))
      greeter.setMsg("remote greetings!")

      val response: Greeting = syncStub.sayHello(greeter)
      response
    }

    transport.close()

    callRpcResult match {
      case Success(response) => println(s"${response.getMessage()}")
      case Failure(e) => throw e
    }
  }
}
```


### 构建工具

因为没有插件支持 mill 来根据 Thrift 服务定义生成相应代码，所以在 mill 里自定义了 Command 类型的 Task ，命令行调用 Apache Thrift compiler 来生成 Java 代码。

build.sc 内容:

```scala
import mill._
import mill.scalalib._


trait ScalaThriftExample extends ScalaModule {
  def scalaVersion = "2.13.3"
  def thriftVersion = "0.14.1"

  override def ivyDeps = T {
    super.ivyDeps() ++ Agg(
      ivy"org.apache.thrift:libthrift:${thriftVersion}",
    )
  }

  def thriftTool = os.pwd / 'lib / s"thrift-${thriftVersion}.exe"
  def sharedThriftInterface = "hello.thrift"
  def projectRoot = os.pwd
  def thriftPath = projectRoot / 'resources / sharedThriftInterface
  def genThriftPath = projectRoot / 'src


  def genThrift() = T.command {
    os.proc(thriftTool,
            "--out", genThriftPath,
            "--gen", "java",
            "-r", thriftPath
           ).call()
  }
}

// lib\thrift-0.14.1.exe --out ServerExample\src --gen java \
\\    -r ServerExample\resources\hello.thrift
object ServerExample extends ScalaThriftExample {
  override def projectRoot = os.pwd / 'ServerExample
}

// lib\thrift-0.14.1.exe --out ClientExample\src --gen java \
//    -r ClientExample\resources\hello.thrift
object ClientExample extends ScalaThriftExample {
  override def projectRoot = os.pwd / 'ClientExample
}
```


### 测试

首先，在 ThriftExample 下执行 `mill -i ServerExample.genThrift`，在 `ServerExample/src` 下就会生成对应 Thrift 定义的 Java 代码。[ps: 在 Windows 上这个 `-i` 是不可缺少的。]再执行 `mill -i ServerExample.run` 就会编译并执行服务端代码。

在 ThriftExample 下执行 `mill -i ClientExample.genThrift`，在 `ClientExample/src` 下就会生成对应 Thrift 定义的 Java 代码。再执行 `mill -i ClientExample.run` 就会编译并执行客户端代码。可以客户端调用 sayHello 的结果：

```
Hello Doris, remote greetings!
```

