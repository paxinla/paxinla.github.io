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
#### Future

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

#### Task

```scala
// 使用 Monix 的 ExecutorService
import $ivy.{`io.monix::monix:3.2.2`}
import monix.execution.Scheduler
import monix.execution.Scheduler.Implicits.global
import monix.eval.Task
import monix.execution.CancelableFuture

// 这里只是定义了运算，并未开始执行。
val sumTask: Task[Int] = Task {
  var sum = 0
  for(i <- Range(1,100000)) sum = sum + i
  sum
}

import scala.util.{Try, Success, Failure}

// 开始执行运算
val cancelable1 = sumTask.runOnComplete {
  case Success(value) => println(value)
  case Failure(ex) => println(s"ERR: ${ex.getMessage}")
}

cancelable1.cancel()

val cancelable2 = sumTask.runAsync {
  case Right(value) => println(value)
  case Left(ex) => println(s"ERR: ${ex.getMessage}")
}


// Task 转换为 Future
val future1 = sumTask.runToFuture

// Future 转换为 Task
val task1 = Task.deferFuture {
  Future { println("Do something.") }
}


// 立即执行
val sumTask: Task[Int] = Task.now {
  var sum = 0
  for(i <- Range(1,100000)) sum = sum + i
  sum
}

```

### 日期时间

Scala 使用的是 Java 的日期时间 API 。自 Java 8 后提供了 java.time、java.time.format、java.time.chrono、java.time.zone 和 java.time.temporal 包。

```scala
// 时区
import java.time.ZoneId
val tzDefault = ZoneId.systemDefault
val tzHK = ZoneId.of("Asia/Hong_Kong")

import java.time.ZoneOffset
val tzBJ = ZoneOffset.of("+8")


// 时间戳是时间线上的一个点。在纪元 1970-01-01T00:00:00Z 后是正值，之前是负值。
import java.time.Instant

val timeStamp0 = Instant.EPOCH
val timeStampA = Instant.now()
timeStampA.getEpochSecond  // 精确到秒
timeStampA.toEpochMilli    // 精确到毫秒

// 日期时间转时间戳
val timeStampB = LocalDateTime.now().toInstant(ZoneOffset.of("+8"))
// 带时区的日期时间转时间戳不带参数
val timeStampC = ZonedDateTime.now(ZoneId.of("US/Pacific")).toInstant   


// LocalTime 只有时间、LocalDate 只有日期、LocalDateTime 既有日期又有时间
import java.time.LocalDate
import java.time.LocalTime
import java.time.LocalDateTime
import java.time.ZonedDateTime
import java.time.temporal.ChronoUnit

val date1 = LocalDate.now()
val date2 = LocalDate.of(2020, 3, 2)
val tomorrow = date1.plusDays(1)
val yestoday = date1.minus(1, ChronoUnit.DAYS)

val time1 = LocalTime.now()

val dateTime1 = LocalDateTime.now()
val dateTime2 = LocalDateTime.of(2020, 3, 2, 17, 5, 1)
val dateTime3 = LocalDateTime.ofInstant(Instant.now(), ZoneId.of("Asia/Shanghai"))  // 时间戳转日期
val dateTime4 = ZonedDateTime.now(ZoneId.of("US/Pacific"))


// 时间间隔 Period 基于日期， Duration 基于时间
import java.time.Period

val period1 = Period.of(3, 2, 1)  // 3年两个月一天的间隔
val period2 = Period.ofWeeks(2)
val period3 = Period.between(LocalDate.now(), LocalDate().minusDays(5))

import java.time.Duration

val duration1 = Duration.of(4, ChronoUnit.HOURS) // 4个小时的间隔
LocalDateTime.now().minus(duration1)
val duration2 = Duration.between(LocalDateTime.now(), LocalDateTime.now().minusHours(5))


// 相较于 java.text.SimpleDateFormat ，java.time.format.DateTimeFormatter 是线程安全的。
import java.time.format.DateTimeFormatter
import java.time.format.FormatStyle

val fmt1 = DateTimeFormatter.ofLocalizedDateTime(FormatStyle.MEDIUM)
val fmt2 = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")
datetime1.format(fmt1)

import java.time.format.DateTimeParseException

// 解析日期/时间字符串
val dateTime5 : LocalDateTime = LocalDateTime.parse("2020-01-02 13:01:06", fmt1)

```


