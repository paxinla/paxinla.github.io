Title: SQL练手题：计算用户留存率
Date: 2020-12-08 17:38:47
Category: SQL习题
Tags: exercise, sql
CommentId: X


一条 SQL 计算用户留存率。

<!-- PELICAN_END_SUMMARY -->

## 题目

一个用户登录的日期距离它第一天登录的日期为 N 天，则称该用户在第 N 天留存。第一天登录用户数 M 中，有 m 个用户在第 N 天有登录，则称 N 日用户留存率为: m/M 。


设用户登录日志表为:

```vim
  - Table: user_login

  | Column     | Type    |
  |------------+---------|
  | user_id    | Integer |
  | login_date | Date    |

```

要求用一条 SQL 计算 1,3,5,7,13,15 日的用户留存率，要求 SQL 有<em class="emp-text">扩展性</em>，以便日后新增查询 Y 日用户留存率时尽量减少代码修改量。


## 解答

以 PostgreSQL 写法作答:

```pgsql
WITH user_first_login AS (
    SELECT DISTINCT
           ulog.user_id
         , ulog.login_date
         , FIRST_VALUE(ulog.login_date)
           OVER (PARTITION BY ulog.user_id
                     ORDER BY ulog.login_date ASC)  AS first_login_date
         , ulog.login_date
         - FIRST_VALUE(ulog.login_date)
           OVER (PARTITION BY ulog.user_id
                     ORDER BY ulog.login_date ASC)  AS login_date_gap
        
         , COUNT(1)
           OVER (PARTITION BY ulog.login_date)      AS user_count_day0
      FROM user_login ulog
), user_retention_count AS (
     SELECT ufd.login_date
          , ufd.first_login_date
          , ufd.login_date_gap
          , COUNT(1)       AS user_count
          , ufd.user_count_day0
       FROM user_first_login ufd
      WHERE ufd.login_date_gap IN (0,1,3,5,7,13,15)
   GROUP BY ufd.login_date, ufd.first_login_date
          , ufd.login_date_gap, ufd.user_count_day0
)      SELECT urc.login_date
            , urc.login_date_gap
            , urc.user_count       AS retention_count
            , urc.user_count::float/urc2.user_count_day0::float AS retention_rate
         FROM user_retention_count urc
    LEFT JOIN user_retention_count urc2
           ON urc2.login_date = urc.first_login_date
          AND urc2.login_date_gap = 0
 ORDER BY urc.login_date, urc.login_date_gap
;

```

如果在子查询 `user_retention_count` 中不限定 where 条件，则最后得到的结果可以查任意 N 日用户留存率。
