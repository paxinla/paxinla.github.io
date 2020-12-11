Title: pgBouncer 的 pool mode
Date: 2020-07-27 09:36:18
Category: 数据库
Tags: postgresql, pgbouncer
CommentId: X


pgBouncer 的连接池模式默认为会话模式 `pool_mode = session` 。

<!-- PELICAN_END_SUMMARY -->

在这种模式下，一个从客户端连接到 pgBouncer 的连接，只要客户端没有 disconnect ，这条连接就会和 pgBouncer 到 PostgreSQL 服务器的连接一直 paired 下去，无论此时客户端是否有在执行查询。

最近碰到了这种情况，后台服务器也有它自己的连接池，这个连接池里会配置一定数量的常驻连接。这些常驻连接是会长期“占用”pgBouncer 中同样数量的连接，无论这些连接实际上是否在执行查询。此时，如果后台服务器继续向 pgBouncer 发起新的连接，就会导致 pgBouncer 到 PostgreSQL 也生成新的连接，很容易就会达到 PostgreSQL 的 `max_connections` 的限制。

若 pgBouncer 的 `pool_mode = transaction` ，就可以规避这个常驻连接引起的问题。但是后台服务大量使用 prepared statement ，则 pgBouncer 只能是设为会话模式。

另一种规避的方案是，在后台服务器上和数据库服务器上都部署 pgBouncer ，后台服务器上的 pgBouncer 使用会话模式，而数据库服务器上的 pgBouncer 使用事务模式。这样后台服务器依然可以按老样子维护它的数据库连接，而对数据库服务器则有效地减少了连接数。但是这种方案要求能够在后台服务器上部署 pgBouncer 。
