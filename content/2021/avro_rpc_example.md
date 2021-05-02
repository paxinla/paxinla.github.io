Title: Avro - 在 Scala 中使用 Avro RPC
Date: 2021-05-02 10:38:30
Category: Scala
Tags: scala, avro, mill
CommentId: X


在 Scala 中使用 Avro RPC 的示例。


<!-- PELICAN_END_SUMMARY -->


## 什么是 Avro

[Apache Avro](http://avro.apache.org/)


## 使用 Avro

Apache Avro 通常作为序列化/反序列化的工具来使用，它也提供 RPC 的功能。

Apache Avro 虽然支持多种语言，但是并不原生支持 Scala 。我在本文中将使用 [mill](https://com-lihaoyi.github.io/mill/) 作为构建工具来展示一个简单的使用 Avro 作为 RPC 的示例。本文的例子使用与[gRPC例子](https://paxinla.github.io/posts/2021/04/scalapb-zai-scala-zhong-shi-yong-grpc.html)相似的结构。


<p class="list-title">项目结构:</p>

<article><header><pre>
AvroExample
  |
  +-- ServerSample
  |     |-- resources
  |     |     +-- hello.avpr
  |     +-- src
  |           |-- RPCServer.scala
  |           +-- HelloServer.scala
  |     
  +-- ClientSample
  |     |-- resources
  |     |     +-- hello.avpr
  |     +-- src
  |           +-- HelloClient.scala
  |
  +-- build.sc
  |
  +-- lib
       +-- avro-tools-1.10.2.jar
</pre></header></article>


### 定义服务

Avro 定义数据结构有几种方式，通常 `.avdl` 用一种紧凑的方式定义数据结构，`.avpr` 用类似 JSON 的形式定义一个 Protocol ，`.avsc` 用类似 JSON 的形式定义一个 Schema 。这里我用 Protocol 的方式。

hello.avpr 内容:

```avro
{ "protocol": "HelloWorld",
  "namespace": "learn.avro.services",

  "types": [
    { "name": "Person",
      "type": "record",
      "fields": [
        { "name": "name",
          "type": "string"
        }
      ]
    },
    { "name": "ToBeGreeted",
      "type": "record",
      "fields": [
        { "name": "person",
          "type": "Person"
        },
        { "name": "msg",
          "type": "string"
        }
      ]
    },
    { "name": "Greeting",
      "type": "record",
      "fields": [
        { "name": "message",
          "type": "string"
        }
      ]
    }
  ],

  "messages": {
    "sayHello": {
      "request": [
         { "name": "request",
           "type": "ToBeGreeted"
         }
       ],
      "response": "Greeting"
    }
  }
}
```


### 服务端

RPCServer.scala 内容:

```scala
package learn.avro.server

import java.net.InetSocketAddress

import org.apache.avro.ipc.Server
import org.apache.avro.ipc.netty.NettyServer
import org.apache.avro.ipc.specific.SpecificResponder


trait RPCServer {
  def runServer(
    responder: SpecificResponder,
    address: InetSocketAddress
  ): Unit = {
    val server = new NettyServer(
      responder,
      address
    )

    println("Start Server.")

    Runtime.getRuntime.addShutdownHook(new Thread() {
      override def run(): Unit = {
        println("Shutdown server.")
        server.close()
        server.join()
      }
    })
      
  }
}
```


HelloServer.scala 内容:

```scala
package learn.avro.hello.server

import java.net.InetSocketAddress

import learn.avro.server.RPCServer
import learn.avro.services._

import org.apache.avro.ipc.specific.SpecificResponder


object HelloServer extends RPCServer {

  class HelloService extends HelloWorld {
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
    val responder = new SpecificResponder(classOf[HelloWorld], serviceHandler)

    runServer(responder, new InetSocketAddress("127.0.0.1", 40032))
  }
}
```


### 客户端

HelloClient.scala 内容:

```scala
package learn.avro.hello.client

import java.net.InetSocketAddress

import org.apache.avro.ipc.netty.NettyTransceiver
import org.apache.avro.ipc.specific.SpecificRequestor

import learn.avro.services._


object HelloClient {
  def main(args: Array[String]): Unit = {
    val timeoutMs = 3000

    val client = new NettyTransceiver(
      new InetSocketAddress("127.0.0.1", 40032),
      timeoutMs
    )

    val syncStub = SpecificRequestor.getClient(classOf[HelloWorld], client)

    val greeter = new ToBeGreeted()
    greeter.setPerson(new Person("Doris"))
    greeter.setMsg("remote greetings!")

    val response: Greeting = syncStub.sayHello(greeter)

    println(s"${response.getMessage()}")
    client.close(true)
  }
}
```


### 构建工具

因为没有插件支持 mill 来根据 Avro 服务定义生成相应代码，所以在 mill 里自定义了 Command 类型的 Task ，命令行调用 avro tools 的 jar 包来生成 Java 代码。

build.sc 内容:

```scala
import mill._
import mill.scalalib._

trait ScalaAvroSample extends ScalaModule {
  def scalaVersion = "2.13.3"
  def AvroVersion = "1.10.2"

  override def ivyDeps = T {
    super.ivyDeps() ++ Agg(
      ivy"org.apache.avro:avro:$AvroVersion",
      ivy"org.apache.avro:avro-ipc-netty:$AvroVersion"
    )
  }

  def avroToolsJar = os.pwd / 'lib / s"avro-tools-${AvroVersion}.jar"
  def sharedAvroProtocol = "hello.avpr"
  def projectRoot = os.pwd
  def avprPath = projectRoot / 'resources / sharedAvroProtocol
  def genAvroPath = projectRoot / 'src


  def genAvro() = T.command {
    os.proc('java, "-jar", avroToolsJar,
            "compile", "protocol",
            avprPath, genAvroPath
           ).call()
  }
}

// java -jar lib\avro-tools-1.10.2.jar compile protocol ServerSample\resources\hello.avpr ServerSample\src
object ServerSample extends ScalaAvroSample {
  override def projectRoot = os.pwd / 'ServerSample
}

// java -jar lib\avro-tools-1.10.2.jar compile protocol ServerSample\resources\hello.avpr ClientSample\src
object ClientSample extends ScalaAvroSample {
  override def projectRoot = os.pwd / 'ClientSample
}
```


### 测试

首先，在 AvroExample 下执行 `mill -i ServerSample.genAvro`，在 `ServerSample/src` 下就会生成对应 avro 定义的 Java 代码。[ps: 在 Windows 上这个 `-i` 是不可缺少的。]再执行 `mill -i ServerSample.run` 就会编译并执行服务端代码。

在 AvroExample 下执行 `mill -i ClientSample.genAvro`，在 `ClientSample/src` 下就会生成对应 avro 定义的 Java 代码。再执行 `mill -i ClientSample.run` 就会编译并执行客户端代码。可以客户端调用 sayHello 的结果：

```
Hello Doris, remote greetings!
```
