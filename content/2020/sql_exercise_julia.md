Title: SQL练手题：Number of unique hackers who made at least one submission each day
Date: 2020-09-09 09:27:56
Category: SQL习题
Tags: exercise, sql
CommentId: X

一道 hackerrank 的 SQL 题。

<!-- PELICAN_END_SUMMARY -->


## 题目

Julia conducted a 15 days of learning SQL contest. The start date of the contest was March 01, 2016 and the end date was March 15, 2016.

Write a query to print total number of unique hackers who made at least submission each day (starting on the first day of the contest), and find the `hacker_id` and `name` of the hacker who made maximum number of submissions each day. If more than one such hacker has a maximum number of submissions, print the lowest `hacker_id`. The query should print this information for each day of the contest, sorted by the date.

### Input Format

The following tables hold contest data:

```vim
    - Hackers: The `hacker_id` is the id of the hacker, and
               name is the name of the hacker.

    | Column    | Type    |
    |-----------+---------|
    | hacker_id | Integer |
    | name      | String  |

    - Submissions: The `submission_date` is the date of
                   the submission, `submission_id` is
                   the id of the submission, `hacker_id` is
                   the id of the hacker who made
                   the submission, and score is
                   the score of the submission.

    | Column          | Type    |
    |-----------------+---------|
    | submission_date | Date    |
    | submission_id   | Integer |
    | hacker_id       | Integer |
    | score           | Integer |
```

### Sample Input

For the following sample input, assume that the end date of the contest was March 06, 2016.

```vim
    - Hackers table

    | hacker_id  | name     |
    |------------+----------|
    | 15758      | Rose     |
    | 20703      | Angela   |
    | 36396      | Frank    |
    | 38289      | Patrick  |
    | 44065      | Lisa     |
    | 53473      | Kimberly |
    | 62529      | Bonnie   |
    | 79722      | Michael  |

    - Submissions table

    | submission_date | submission_id | hacker_id | score |
    |-----------------+---------------+-----------+-------|
    | 2016-03-01      |  8494         | 20703     | 0     |
    | 2016-03-01      |  22403        | 53473     | 15    |
    | 2016-03-01      |  23965        | 79722     | 60    |
    | 2016-03-01      |  30173        | 36396     | 70    |
    | 2016-03-02      |  34928        | 20703     | 0     |
    | 2016-03-02      |  38740        | 15758     | 60    |
    | 2016-03-02      |  42769        | 79722     | 25    |
    | 2016-03-02      |  44364        | 79722     | 60    |
    | 2016-03-03      |  45440        | 20703     | 0     |
    | 2016-03-03      |  49050        | 36396     | 70    |
    | 2016-03-03      |  50273        | 79722     | 5     |
    | 2016-03-04      |  50344        | 20703     | 0     |
    | 2016-03-04      |  51360        | 44065     | 90    |
    | 2016-03-04      |  54404        | 53473     | 65    |
    | 2016-03-04      |  61533        | 79722     | 45    |
    | 2016-03-05      |  72852        | 20703     | 0     |
    | 2016-03-05      |  74546        | 38289     | 0     |
    | 2016-03-05      |  76487        | 62529     | 0     |
    | 2016-03-05      |  82439        | 36396     | 10    |
    | 2016-03-05      |  90006        | 36396     | 40    |
    | 2016-03-06      |  90404        | 20703     | 0     |
```

### Sample Output

- 2016-03-01 4 20703 Angela
- 2016-03-02 2 79722 Michael
- 2016-03-03 2 20703 Angela 
- 2016-03-04 2 20703 Angela 
- 2016-03-05 1 36396 Frank 
- 2016-03-06 1 20703 Angela

### Explanation

On March 01, 2016 hackers 20703, 36396, 53473 and 79722 made submissions. There are 4 unique hackers who made at least one submission each day. As each hacker made one submission, 20703 is considered to be the hacker who made maximum number of submissions on this day. The name of the hacker is Angela.

On March 02, 2016 hackers 15758, 20703 and 79722 made submissions. Now 20703 and 79722 were the only ones to submit every day, so there are 2 unique hackers who made at least one submission each day. 79722 made 2 submissions, and name of the hacker is Michael.

On March 03, 2016 hackers 20703, 36396 and 79722 made submissions. Now 20703 and 79722 were the only ones, so there are 2 unique hackers who made at least one submission each day. As each hacker made one submission so 20703 is considered to be the hacker who made maximum number of submissions on this day. The name of the hacker is Angela.

On March 04, 2016 hackers 20703, 44065, 53473 and 79722 made submissions. Now 20703 and 79722 only submitted each day, so there are 2 unique hackers who made at least one submission each day. As each hacker made one submission so 20703 is considered to be the hacker who made maximum number of submissions on this day. The name of the hacker is Angela.

On March 05, 2016 hackers 20703, 36396, 38289 and 62529 made submissions. Now 20703 only submitted each day, so there is only 1 unique hacker who made at least one submission each day. 36396 made 2 submissions and name of the hacker is Frank.

On March 06, 2016 only 20703 made submission, so there is only 1 unique hacker who made at least one submission each day. 20703 made 1 submission and name of the hacker is Angela.


## 解答

以 PostgreSQL 写法作答:

```pgsql
WITH date_seq AS ( 
    SELECT generate_series(to_date('20160301', 'yyyymmdd')
                          ,to_date('20160306', 'yyyymmdd')
                          ,'1 day') AS submission_date
), attach_pre_date AS (
    SELECT s1.hacker_id
         , s1.submission_date
         , CASE WHEN s1.submission_date = '20160301'::date
		        THEN s1.submission_date
			    ELSE s2.submission_date
		   END        AS pre_date
      FROM submissions s1
 LEFT JOIN submissions s2
        ON s2.hacker_id = s1.hacker_id
	   AND s2.submission_date = s1.submission_date - 1
), stat_submission1 AS (
    SELECT t.submission_date
         , COUNT(DISTINCT t.hacker_id)  AS distinct_count
      FROM attach_pre_date t
     WHERE t.pre_date IS NOT NULL
  GROUP BY t.submission_date
), stat_submission2 AS ( 
    SELECT tmp.submission_date
         , tmp.hacker_id
         , ROW_NUMBER()
           OVER(PARTITION BY tmp.submission_date
                    ORDER BY tmp.hacker_submission_count DESC
                           , tmp.hacker_id ASC
               )    AS rn
      FROM (   SELECT t.submission_date
                    , t.hacker_id
                    , COUNT(1)       AS hacker_submission_count 
                 FROM attach_pre_date t
                WHERE t.pre_date IS NOT NULL
             GROUP BY t.submission_date, t.hacker_id
           ) tmp
)   SELECT ds.submission_date
         , ss1.distinct_count
         , ss2.hacker_id
         , h.name
      FROM date_seq ds
 LEFT JOIN stat_submission1 ss1
        ON ss1.submission_date = ds.submission_date
 LEFT JOIN stat_submission2 ss2
        ON ss2.submission_date = ds.submission_date
       AND ss2.rn = 1
 LEFT JOIN hackers h
        ON h.hacker_id = ss2.hacker_id
;

```
