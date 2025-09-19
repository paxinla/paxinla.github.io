Title: [转] How to handle "database is not accepting commands"
Date: 2025-09-19 09:41:59
Category: 数据库
Tags: 转载, postgresql
CommentId: X

原文作者: Laurenz Albe

原文链接: [https://www.cybertec-postgresql.com/en/database-is-not-accepting-commands/](https://www.cybertec-postgresql.com/en/database-is-not-accepting-commands/)

为防遗失，转载一份。

<!-- PELICAN_END_SUMMARY -->

If you ever get the error message "database is not accepting commands", you are dangerously close to [transaction ID wraparound](https://www.cybertec-postgresql.com/en/transaction-id-wraparound-a-walk-on-the-wild-side/) . Most PostgreSQL users understand [the principle behind transaction ID wraparound](https://www.cybertec-postgresql.com/en/autovacuum-wraparound-protection-in-postgresql/) , but I recently realized that even many PostgreSQL power users have a wrong idea of how to fix the problem. So I decided to write about it in some more detail.


## How do you end up with "database is not accepting commands"?

If you end up with this error, your application will have down time while you manually repair the problem. In this state, you can still run queries, but you cannot perform any more data modifications. Few people ever get that far, because PostgreSQL has several lines of defense before it has to take this last, invasive measure:

- if a table contains live rows older than autovacuum_freeze_max_age transactions (200 million by default), PostgreSQL will launch an anti-wraparound autovacuum worker
- if a table contains live rows older than vacuum_failsafe_age transactions (1.6 billion by default), PostgreSQL will launch an emergency anti-wraparound autovacuum worker that skips the index cleanup step and runs as fast as it can
- 40 million transactions before transaction ID wraparound, you will get warnings in the log

Only if none of these safeties can prevent the problem will PostgreSQL stop data modifications.

There are a few ways to prevent PostgreSQL from fixing the problem by itself:

- keep a database transaction open forever
- keep a prepared transaction around without committing it or rolling it back
- keep an orphaned replication slot with the standby server having hot_standby_feedback enabled
- have data corruption that makes VACUUM fail


## What is the proper measure against "database is not accepting commands"?

[The documentation](https://www.postgresql.org/docs/current/routine-vacuuming.html#VACUUM-FOR-WRAPAROUND) describes how to fix the problem:

In this condition, any transactions already in progress can continue, but only read-only transactions can be started. Operations that modify database records or truncate relations will fail. The VACUUM command can still be run normally. Note that, contrary to what was sometimes recommended in earlier releases, it is not necessary or desirable to stop the postmaster or enter single-user mode in order to restore normal operation. Instead, follow these steps:

1. Resolve old prepared transactions. You can find these by checking pg_prepared_xacts for rows where age(transactionid) is large. Such transactions should be committed or rolled back.
2. End long-running open transactions. You can find these by checking [pg_stat_activity](https://www.postgresql.org/docs/current/monitoring-stats.html#MONITORING-PG-STAT-ACTIVITY-VIEW) for rows where age(backend_xid) or age(backend_xmin) is large. Such transactions should be committed or rolled back, or the session can be terminated using pg_terminate_backend.
3. Drop any old replication slots. Use [pg_stat_replication](https://www.postgresql.org/docs/current/monitoring-stats.html#MONITORING-PG-STAT-REPLICATION-VIEW) to find slots where age(xmin) or age(catalog_xmin) is large. In many cases, such slots were created for replication to servers that no longer exist, or that have been down for a long time. If you drop a slot for a server that still exists and might still try to connect to that slot, that replica may need to be rebuilt.
4. Execute VACUUM in the target database. A database-wide VACUUM is simplest; to reduce the time required, it is also possible to issue manual VACUUM commands on the tables where relminxid is oldest. Do not use VACUUM FULL in this scenario, because it requires an XID and will therefore fail, except in super-user mode, where it will instead consume an XID and thus increase the risk of transaction ID wraparound. Do not use VACUUM FREEZE either, because it will do more than the minimum amount of work required to restore normal operation.
5. Once normal operation is restored, ensure that autovacuum is properly configured in the target database in order to avoid future problems.


## Inferior measures that tempt users

The documentation I quoted above takes care to point out the frequent fallacies:

- For reasons I will explain later, many people think that you need to shut down PostgreSQL and start it in [single-user mode](https://www.postgresql.org/docs/current/app-postgres.html#APP-POSTGRES-SINGLE-USER) to run VACUUM. But that is not necessary. On the contrary: starting the server in single-user mode will complicate recovery and increase the down time. Moreover, single-user mode disarms the safety that prevents you from using any more transaction IDs, and consuming transaction IDs will bring you closer to data corruption by transaction ID wraparound.
- Many people think of VACUUM (FULL) as "a better VACUUM", so they are tempted to use it in this dire situation. But VACUUM (FULL) does much more work than a plain VACUUM, and you would end up with a much longer down time. Besides, as the documentation mentions, it will force you to use the single-user mode (see the previous point).
- Using VACUUM (FREEZE) would fix the problem, but it freezes all rows of the table. That is more work than necessary and will lead to a longer down time.

So, why do people believe that you need single-user mode to recover from "database is not accepting commands"? To answer that, we have to dig into the history of PostgreSQL.


## Source code archaeology, or the history of an error message

If you don't know how to analyze the history of the PostgreSQL code, I recommend that you read [my article about the true power of open source](https://www.cybertec-postgresql.com/en/the-power-of-open-source-in-postgresql/) .


[Commit 60b2444cc3](https://postgr.es/c/60b2444cc3ba037630c9b940c3c9ef01b954b87b) added the safety margin of three million transaction IDs in 2005 with a message like this:
<blockquote>
<p>ERROR:  database is shut down to avoid wraparound data loss in database "..."</p>
<p>HINT:  Stop the postmaster and use a standalone backend to VACUUM in "...".</p>
</blockquote>

You see the first mention of single-user mode in the form "standalone backend". Since the server didn't actually shut down, [commit 8ad3965a11](https://postgr.es/c/8ad3965a115bbd5fbd1bb2f3585c2e34d569af7d), also in 2005, amended the message to read

<blockquote>
<p>ERROR:  database is not accepting queries to avoid wraparound data loss in database "..."</p>
<p>HINT:  Stop the postmaster and use a standalone backend to VACUUM database "...".</p>
</blockquote>

Note that back then, the advice to use single-user mode was actually correct, since VACUUM used to consume a transaction ID back then. In 2009, [commit 8d4f2ecd41](https://postgr.es/c/8d4f2ecd41312e57422901952cbad234d293060b) extended the hint to

<blockquote>
<p>ERROR:  database is not accepting queries to avoid wraparound data loss in database "..."</p>
<p>HINT:  Stop the postmaster and use a standalone backend to VACUUM database "...".</p>
<p>You might also need to commit or roll back old prepared transactions.</p>
</blockquote>

In 2013, [commit 7dfd5cd21c](https://postgr.es/c/7dfd5cd21c0091e467b16b31a10e20bbedd0a836) changed the wording to "single-user mode":

<blockquote>
<p>ERROR:  database is not accepting commands to avoid wraparound data loss in database "..."</p>
<p>HINT:  Stop the postmaster and vacuum that database in single-user mode.</p>
<p>You might also need to commit or roll back old prepared transactions.</p>
</blockquote>

And in 2017, [commit 2958a672b1](https://postgr.es/c/2958a672b1fed35403b23c2b453aede9f7ef4b39) added stale replication slots as a possible cause:

<blockquote>
<p>ERROR:  database is not accepting commands to avoid wraparound data loss in database "..."</p>
<p>HINT:  Stop the postmaster and vacuum that database in single-user mode.</p>
<p>You might also need to commit or roll back old prepared transactions, or drop stale replication slots.</p>
</blockquote>

This was the state of affairs until PostgreSQL v17. By then, the message had long been inaccurate, ever since [commit 295e63983d](https://postgr.es/c/295e63983d7596ccc5717ff4a0a235ba241a2614) introduced "lazy transaction ID allocation" in 2007. In October 2023, [commit 2406c4e34c](https://postgr.es/c/2406c4e34ccca697bd5a221f8375f335b5841dea) finally changed the error message to its current form:

<blockquote>
<p>ERROR:  database is not accepting commands that assign new XIDs to avoid wraparound data loss in database "..."</p>
<p>HINT:  Execute a database-wide VACUUM in that database.</p>
<p>You might also need to commit or roll back old prepared transactions, or drop stale replication slots.</p>
</blockquote>

So it is hardly surprising that many PostgreSQL old-timers still believe that you need single-user mode to recover from an impending transaction ID wraparound!

## Conclusion

We reviewed the correct way to handle "database is not accepting commands" (a plan VACUUM) and explored various inferior responses to the situation. This gave me the opportunity to dig into the history of the PostgreSQL source code again!

