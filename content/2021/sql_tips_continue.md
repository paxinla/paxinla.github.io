Title: SQL技巧：连续时间区间类问题
Date: 2021-04-15 17:08:26
Category: SQL技巧
Tags: sql
CommentId: X

有一类 SQL 题目，统计范围要求限定日期/时间要连续，以连续的部分为单位。


<!-- PELICAN_END_SUMMARY -->


如果有诸如“最近...”这样的条件，体现到 WHERE 子句中。如果一行记录中有多个时间粒度，只保留相关的时间粒度，用相关的维度去重，每个时间单位对每个分组维度只保留一条数据。这些都是常规操作了。


要点还是在于如何判断并分组符合题目“连续”定义的行。这时可以开窗口，PARTITION BY 主维度，ORDER BY 时间维度，用分析函数 `ROW_NUMBER` 给时间维度加序号。然后再用日期减去<span class="emp-text">序号个</span>时间单位。那么连续的时间值得到的<span class="emp-text">时间差值</span>结果将会是一样的，这就完成了对“连续”的时间区间的判断及分组。后面再做统计计算时，只需将这个时间差值加入到分组条件中即可。


上面这种方法，是因为 `ROW_NUMBER` 产生的序号，间隔是1；通常情况下，题目中“连续”的定义也是指时间单位间隔为1，所谓的 consecutive series of events 。因此“连续”时间区间的各个时间值减去自己对应的“序号个时间单位”，得到的值都是该时间区间中第一个时间减去它的“序号个时间单位”的值。

即:

```
隐含条件: gap = 1 才为“连续”

  date1 - sequence_no1
= some_date1


  date2 - sequence_no2
= (date1 + 1) - (sequence_no1 + 1)
= date1 + 1 - sequence_no1 - 1
= date1 - sequence_no1
= some_date1


  date3 - sequence_no3
= (date1 + 2) - (sequence_no1 + 2)
= date1 + 2 - sequence_no1 - 2
= date1 - sequence_no1
= some_date1


#这里 date4 = date3 + 2
  date4 - sequence_no4
= (date1 + 4) - (sequence_no1 + 3)
= date1 + 4 - sequence_no1 - 3
= date1 - sequence_no1 + 1
= some_date2

... ...
```


数据样例:

```
| data column | row number | date diff  |
|-------------+------------+------------|
| 2021-04-03  | 1          | 2021-04-02 |
| 2021-04-04  | 2          | 2021-04-02 |
| 2021-04-05  | 3          | 2021-04-02 |
| 2021-04-07  | 4          | 2021-04-03 | <-- gap before this row
| 2021-04-08  | 5          | 2021-04-03 |
| 2021-04-09  | 6          | 2021-04-03 |
| 2021-04-10  | 7          | 2021-04-03 |
| 2021-04-15  | 8          | 2021-04-07 | <-- gap before this row
| 2021-04-16  | 9          | 2021-04-07 |
| 2021-04-17  | 10         | 2021-04-07 |

... ...
```


如果时间“连续”的定义变化为只要不超过n个时间单位的时间都算是“连续”呢？比如，本来隔一天就不算是“连续每日”，现在要求将“间隔2天内”都当作是“连续”的日期。

这时就需要两个辅助数据，这里用 df 与 accdf 来标识。

在 PARTITION BY 的小分组中，对每一个日期与它 LAG 取的前一个日期相减得出的时间间隔 readTimeUnitDiff，与题目时间间隔条件相比较，如果符合“连续”的定义，则计该行的 df 值为 (readTimeUnitDiff - 1) ，否则为 0 。

在 PARTITION BY 的小分组中，开窗从整个小分组第一行到当前行的 df 累加值就是这一行的 accdf 值。

有了这两个辅助数据，在上面提到的方法中，对“时间差值”再减去一个 accdf 来“修正”，就可使得最后的差值与时间间隔为1个时间单位时一致。

即:

```
条件: gap <= 2 均视为“连续”

date1 - sequence_no1 = some_date1


#这里 date2 = date1 + 2, df=1, accdf=1
  date2 - sequence_no2 - accdf
= (date1 + 2) - (sequence_no1 + 1) - 1
= (date1 + 2) - (sequence_no1 + 1) - 1
= date1 + 2 - sequence_no1 - 1 - 2 + 1
= date1 - sequence_no1
= some_date1


#这里 date3 = date2 + 1 = date1 + 3, df=0, accdf=1
  date3 - sequence_no3 - accdf
= (date1 + 3) - (sequence_no1 + 2) - 1
= date1 + 3 - sequence_no1 - 2 - 1
= date1 - sequence_no1
= some_date1


#这里 date4 = date3 + 3 = date1 + 6, df=0, accdf=1
  date4 - sequence_no4 - accdf
= (date1 + 6) - (sequence_no1 + 3) - 1
= date1 + 6 - sequence_no1 - 3 - 1
= date1 - sequence_no1 + 2
= some_date2

#这里 date5 = date4 + 1 = date1 + 7, df=0, accdf=1
  date5 - sequence_no5 - accdf
= (date1 + 7) - (sequence_no1 + 4) - 1
= date1 + 7 - sequence_no1 - 4 - 1
= date1 - sequence_no1 + 2
= some_date2

... ...
```


数据样例:

```
| data column | row number | df | accdf | date diff  |
|-------------+------------+----+-------+------------|
| 2021-04-03  | 1          | 0  | 0     | 2021-04-02 |
| 2021-04-04  | 2          | 0  | 0     | 2021-04-02 |
| 2021-04-06  | 3          | 1  | 1     | 2021-04-02 |
| 2021-04-07  | 4          | 0  | 1     | 2021-04-02 |
| 2021-04-10  | 5          | 0  | 1     | 2021-04-04 | <-- gap before this row
| 2021-04-12  | 6          | 1  | 2     | 2021-04-04 |
| 2021-04-13  | 7          | 0  | 2     | 2021-04-04 |
| 2021-04-14  | 8          | 0  | 2     | 2021-04-04 |
| 2021-04-20  | 9          | 0  | 2     | 2021-04-09 | <-- gap before this row
| 2021-04-21  | 10         | 0  | 2     | 2021-04-09 |

... ...
```


再做一次判断+分组，把符合条件的“时间差值”归到一组中去，后续的统计要把这个新的“组”加到分组条件中。


例题: 有表 tableAAA 结构如下:

```
| column_name | data_type   |
|-------------+-------------|
| user_id     | varchar(35) |
| company_id  | varchar(35) |
| rec_date    | date        | 
| start_time  | timestamp   |
| end_time    | timestamp   |
```

1. 求最近两周每个用户最大连续使用服务天数。
2. 设间隔2天使用服务依然算是“连续使用服务”，求最近两周每个用户最大连续使用服务天数。


以 PostgreSQL 写法作答:

```pgsql
-- 1.
WITH step1 AS (
SELECT t.user_id
     , t.rec_date
     , ROW_NUMBER()
       OVER(PARTITION BY t.user_id
                ORDER BY t.rec_date)  AS rn
  FROM tableAAA t
 WHERE t.rec_date <= CURRENT_DATE - INTERVAL '2 WEEKS'
), step2 AS (
 SELECT a.user_id
      , a.rec_date
      , a.rec_date
      - (a.rn * '1 day'::interval)  AS diff_date 
   FROM step1 a
), step3 AS (
  SELECT b.user_id
       , b.diff_date
       , COUNT(1)    AS cnt
    FROM step2 b 
GROUP BY b.user_id, b.diff_date
) SELECT c.user_id
       , MAX(c.cnt)   AS max_consecutive_cnt
    FROM step3 c
GROUP BY c.user_id
;



-- 2.
WITH step1 AS (
SELECT t.user_id
     , t.rec_date
     , ROW_NUMBER()
       OVER(PARTITION BY t.user_id
                ORDER BY t.rec_date)  AS rn
     , CASE WHEN (t.rec_date
                  - LAG(t.rec_date, 1,
                        (t.rec_date - '1 day'::interval)::date)
                    OVER(PARTITION BY t.user_id
                             ORDER BY t.rec_date)
                 ) <= 2
            THEN (t.rec_date
                  - LAG(t.rec_date, 1,
                        (t.rec_date - '1 day'::interval)::date)
                    OVER(PARTITION BY t.user_id
                             ORDER BY t.rec_date)
                 ) - 1
            ELSE 0
       END             AS df
  FROM tableAAA t
 WHERE t.rec_date <= CURRENT_DATE - INTERVAL '2 WEEKS'
), step2 AS ( 
 SELECT a.user_id
      , a.rec_date
      , a.rec_date
      - (a.rn * '1 day'::interval)  AS origin_diff_date 
      , a.df
      , SUM(a.df)
        OVER(PARTITION BY a.user_id
                 ORDER BY a.rec_date 
                  ROWS BETWEEN UNBOUNDED PRECEDING
                           AND CURRENT ROW
            )      AS accdf
   FROM step1 a
), step3 AS (
  SELECT b.user_id
       , b.origin_diff_date
       - (b.accdf * '1 day'::interval)  AS diff_date
       , COUNT(1)    AS cnt
    FROM step2 b
GROUP BY b.user_id, diff_date
) SELECT c.user_id
       , MAX(c.cnt)   AS max_consecutive_cnt
    FROM step3 c
GROUP BY c.user_id
;

```
