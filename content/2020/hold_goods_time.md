Title: 一道取数题目：购物车 hold 货时长
Date: 2020-06-10 10:28:56
Category: SQL习题
Tags: exercise, sql
CommentId: X


数仓微信群里，有群友问了这样一道SQL题目：

<!-- PELICAN_END_SUMMARY -->

```vim
表: 购物车表(表名: table_cart)，主键是 user_id+goods_id+add_time ，用于记录
客户不同时点放入购物车的商品情况(商品ID、商品数量、商品删除时间、商品购买
时间)

 +---------+----------+--------+---------------------+---------------------+---------------------+
 | user_id | goods_id | amount | add_time            | delete_time         | buy_time            |
 +---------+----------+--------+---------------------+---------------------+---------------------+
 |     111 | 56235    |      2 | 2014-10-22 10:01:10 |                     | 2014-10-22 10:20:10 |
 |     111 | 24466    |      1 | 2014-10-22 10:21:02 | 2014-10-22 10:29:25 |                     |
 |     111 | 25948    |      3 | 2014-10-22 10:24:03 |                     |                     |
 |     111 | 39555    |      1 | 2014-10-22 21:20:30 | 2014-10-22 21:56:50 |                     |
 |     111 | 98303    |      4 | 2014-10-22 21:24:10 |                     |                     |
 |     111 | 20249    |      2 | 2014-10-22 21:39:19 |                     |                     |
 +---------+----------+--------+---------------------+---------------------+---------------------+

备注: 客户主动删除商品或购买商品，时间分别记录在 delete_time 和 buy_time 两个
      字段，否则记录为空。

特卖模式下，客户把商品放入购物车后，需在20分钟内完成购买，每加入一件新的商品，购物
时长（即20分钟）将重新计算，若在20分钟内无放入购物车行为，购物车内商品会由系统自动
释放。请结合购物车表的数据结构，写出计算2014年3月每日平均每件商品 hold 货时长（即
商品的锁定时间）的逻辑和SQL代码，结果格式要求如下:

 +----------+----------------+
 | 日期     | 平均hold货时长 |
 +----------+----------------+
 | 2014/3/1 |                |
 | 2014/3/2 |                |
 |  ......  |                |
 +----------+----------------+

```

群友补充，该表不做物理删除，多次添加对应多条记录。

在这里假定时间戳字段都是同一时区。

题目里没有说明在特卖模式下，这张购物车表会如何记录。假如，当一个客户放入购物车内的商品，由于20分钟内既没有发生购买该物品行为，又没有新的商品放入购物车内，而导致该商品被系统自动释放。且这个自动释放的行为，在表中体现为，释放时间戳记录到 `delete_time` 字段中。那么所有的商品的生命周期还是好确定的:

1. 设统计结果的日期列为 `stat_time` ，计算时统一取时间部分为 23:59:59 ，展示时只取日期部分 。
2. 商品的 `start_time` <= 2014-03-01 。
3. 商品的 (`delete_time` 或 `buy_time`) >= 2014-03-01 或者 `delete_time` 与 `buy_time` 均为空。
4. 若商品最终被购买，则它(们)的 hold 货时长为 min(`stat_time`, coalesce(`delete_time`, `buy_time`)) - `start_time` 。


```sql
WITH src AS (
    SELECT tc.goods_id
         , tc.add_time       AS start_time
         , CASE WHEN tc.buy_time IS NOT NULL
                THEN tc.buy_time
                WHEN tc.delete_time IS NOT NULL
                THEN tc.delete_time
                ELSE NULL
           END               AS end_time
      FROM table_cart tc
     WHERE tc.start_time <= timestamp '2014-03-01 00:00:00'
       AND (   (     tc.delete_time IS NOT NULL
                 AND tc.delete_time >= timestamp '2014-03-01 00:00:00'
               )
            OR (     tc.buy_time IS NOT NULL
                 AND tc.delete_time >= timestamp '2014-03-01 00:00:00'
               )
            OR (     tc.delete_time IS NULL
                 AND tc.buy_time IS NULL
               )
           )
), stat_time_mar AS (
    SELECT dd                    AS stat_date
         , dd + time '00:00:00'  AS stat_time_start
         , dd + time '23:59:59'  AS stat_time
      FROM generate_series('2014-03-01'::date,
                           '2014-03-31'::date,
                           '1 day'::interval) dd
) 
SELECT t1.stat_date
     , SUM(t1.goods_life_time)/COUNT(1)  AS avg_hold_time_interval
  FROM (  SELECT t.goods_id
               , CASE WHEN t.end_time IS NULL
                      THEN d.stat_time
                      ELSE MIN(d.stat_time, t.end_time)
                 END - t.start_time     AS goods_life_time
               , d.stat_date
            FROM src t
               , stat_time_mar d
           WHERE t.start_time <= d.stat_time 
             AND (   t.end_time IS NULL
                  OR t.end_time >= d.stat_time_start
                 )
       ) t1
GROUP BY t1.stat_date
ORDER BY t1.stat_date

```

假如，特卖模式的自动释放行为并没有体现到 `delete_time` 字段。即 `delete_time` 字段就仅表示客户自行删除商品这一种情况了。这种情况下，虽然题目没有讲明，但是若 `buy_time` 不为空时，则这一行的商品必定没有被系统自动释放。并且，对一个客户按 `add_time` 升序查询 ，若某一行的 `buy_time` 不为空，则 `add_time` 在这一行之前的 `delete_time` 与 `buy_time` 的行的商品，要么随这一行的购买行为而被购买，要么已经因20分钟的超时限制已被系统自动释放。

此时，对购物车表中的每一行，若 `delete_time` 与 `buy_time` 均不为空，则这一行的商品实际终止时间，须由该客户从本行起在 `add_time` 增长方向上的下一条记录的 `add_time` 来判断: 

+ 若下一行的 `add_time` 已经超出本行的 `add_time + 20分钟` ，则本行的终止时间就是 `add_time + 20分钟` （即本行的商品已经被系统自动释放了）；并且在本行之前未被判断为购买的行，也应视为已经被系统自动释放了。
+ 若下一行的 `add_time` 尚未超出本行的 `add_time + 20分钟` ，且下一行的 `buy_time` 为空 ，则继续查询下一行的下一行的 `add_time` 作判断；
+ 若下一行的 `add_time` 尚未超出本行的 `add_time + 20分钟` ，且下一行的 `buy_time` 不为空，则本行及本行之前未被判断为已释放的行的终止时间，均为下一行的 `buy_time` 。

可以看出，这种情况下，虽然可以依靠分析函数和多层子查询写出统计 SQL ，但是代码的可读性不会好，也很容易出错。原因就在于，购物车表的结构设计，在这种假设下是糟糕的。这种结构不应该直接进入数据仓库，[ps: 我觉得对联机应用来说，这种结构也不会好用到哪里去。] 而是要先洗出每一行的终止时间，最好还能标识出每一行的商品是否是在特卖模式下产生的。尽量使每一行自身的状态、动作信息，在它本行的字段里就能找到，而不是依赖于其他行。

能写出复杂又高效的 SQL 取数，是数据仓库工程师的基本要求；但它绝不是应对数据统计需求的首选。用合理的模型、结构来储存数据，使它易于理解、易于使用，才是我们应当追求的第一选择。
