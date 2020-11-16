Title: 一些 Scala 的 Tips
Date: 2020-04-20 15:38:25
Category: Scala
Tags: scala
CommentId: X


## 一些良好的实践

 - [Scala Best Practices](https://nrinaudo.github.io/scala-best-practices/)
 - [Scala 手账](https://scala.chobit.org)


## 工具相关
### Ammonite

自定义 [Ammonite](https://ammonite.io/) 国内仓库镜像，修改 `$HOME/.ammonite/predef.sc` ，添加如下内容：

```scala
import coursierapi.MavenRepository

interp.repositories() ++= Seq(
  MavenRepository.of("file://" + scala.sys.env("HOME") + "/.m2/repository/"),
  MavenRepository.of("file://" + scala.sys.env("HOME") + "/.ivy2/cache/"),
  MavenRepository.of("https://maven.aliyun.com/repository/public/"),
  MavenRepository.of("https://maven.aliyun.com/repository/central/"),
  MavenRepository.of("https://maven.aliyun.com/repository/google/"),
  MavenRepository.of("https://maven.aliyun.com/repository/apache-snapshots/"),
  MavenRepository.of("https://mirrors.huaweicloud.com/repository/maven/"),
  MavenRepository.of("https://repo1.maven.org/maven2/")
)

```

如果是在 Windows 下，环境变量 HOME 改为 HOMEPATH 。

### 临时的数据库服务器

有的时候，会需要一个临时的数据库服务器来进行一些测试。此时，不必在本地完整
安装全套数据库的服务器组件，可以在内存里模拟一个临时的数据库服务器实例。

以在 Ammonite 中执行为例:

运行一个 MySQL 服务器:

```scala
{
  import $ivy.{
    `com.wix:wix-embedded-mysql:4.6.1`
  }
  import java.util.concurrent.{ TimeoutException, TimeUnit }
  import com.wix.mysql.config.MysqldConfig.aMysqldConfig
  import com.wix.mysql.config.SchemaConfig.aSchemaConfig
  import com.wix.mysql.config.Charset.UTF8
  import com.wix.mysql.EmbeddedMysql.anEmbeddedMysql
  import com.wix.mysql.distribution.Version.v5_7_latest

  val config = aMysqldConfig(v5_7_latest).
               withCharset(UTF8).
               withPort(3306).
               withUser("SomeUserName", "SomePassword").
               withTimeZone("Asia/Shanghai").
               withTimeout(30, TimeUnit.MINUTES).
               withServerVariable("max_connect_errors", 100).build()

  val server = anEmbeddedMysql(config).
               addSchema(aSchemaConfig("test").build()).
               start()
}

// 关闭服务器: server.stop
```

运行一个 PostgreSQL 服务器:

```scala
{
  import $ivy.{
    `com.opentable.components:otj-pg-embedded:0.13.3`
  }
  import com.opentable.db.postgres.embedded.EmbeddedPostgres

  val server = EmbeddedPostgres.builder().setPort(5432).start()
}

// 关闭服务器: server.close
```

## 代码片段

### 线程池

```scala
// 使用 Java 的 ExecutorService
import java.util.concurrent.{Executors, ExecutorService}
// 使用 Monix 的 ExecutorService
import $ivy.{`io.monix::monix:3.2.2`}
import monix.execution.Scheduler

import scala.concurrent.{Future, ExecutionContext}


// 使用 Java 的 ExecutorService
// 偷懒 import scala.concurrent.ExecutionContext.Implicits.global

implicit val ec = ExecutionContext.fromExecutor(
  Executors.newFixedThreadPool(6)]
)
// 使用 Monix 的 ExecutorService
// 偷懒 import monix.execution.Scheduler.Implicits.global
implicit val ec = Scheduler.fixedPool(name="testpool", poolSize=6)

val sumFuture: Future[Int] = Future[Int] {
  var sum = 0
  for(i <- Range(1,100000)) sum = sum + i
  sum
}

// 同步阻塞
import scala.concurrent.Await
import scala.concurrent.duration.Duration

val rs: Int = Await.result(sumFuture, Duration.Inf)


// 回调
import scala.util.{Try, Success, Failure}

//// 仅在成功后调用，使用 onSuccess
//// 或 foreach(A => Unit)、map(A => A)、flatMap(A => Future[A])

sumFuture.onSuccess {
  case number => println(s"Succeed with: ${number}")
}


//// 成功失败都有调用的，使用 onComplete(Try[A] => Unit)、andThen
//// 或 transform(Try[A] => Try[B])、transformWith(Try[A] => Future[B])

def printResult[A](result: Try[A]): Unit = result match {
  case Failure(exception) => println(s"Failed with: ${exception.getMessage}")
  case Success(number)    => println(s"Succeed with: ${number}")
}
sumFuture.onComplete(printResult)

sumFuture.andThen {
  case Success(v) => println(s"The answer is $v")
} andThen {
  case Success(_) =>  sendSuccessSignalHTTPRequest()
  case Failure(_) =>  sendFailureSignalHTTPRequest()
}

val transformed = Future.successful(42).transform {
  case Success(value) => Success(s"Successfully computed the $value")
  case Failure(cause) => Failure(new IllegalStateException(cause))
}

val transformed2 = Future.successful(42).transformWith {
  case Success(value) => Future.success(s"Successfully computed the $value")
  case Failure(cause) => Future.failure(new IllegalStateException(cause))
}


// 对特定异常进行“掩盖”
val recoveredF: Future[Int] = Future(3 / 0).recover {
  case _: ArithmeticException => 0
}

val recoveredWithF: Future[Int] = Future(3 / 0).recoverWith {
  case _: ArithmeticException => sumFuture
}

val failedInt: Future[Int] = Future.failed(
  new IllegalArgumentException("Boom!")
)
failedInt.fallbackTo(Future.successful(42))

```