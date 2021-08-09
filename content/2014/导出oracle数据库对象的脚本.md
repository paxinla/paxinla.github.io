Title: 导出Oracle数据库对象的脚本
Date: 2014-04-26 21:45:00
Category: 数据库
Tags: oracle, PL/SQL, sql
CommentId: 2

spool 是常用的手段。

<!-- PELICAN_END_SUMMARY -->

# 将oracle对象DDL语句spool成sql文本

　　在我的工作实践中，常常需要将数据库中的表结构、函数、存储过程等导出成sql文本。一般都是用PL/SQL Developer来导出的。但是有时也会碰到没有PL/SQL Developer的环境，就自己写了几个脚本，用sqlplus将这些数据库对象spool出来。

　　这套sql脚本共7个。分别可导出表结构、视图定义、自定义类型、序列、函数、存储过程和包。主要是使用ORACLE的包DBMS_METADATA的SET_TRANSFORM_PARAM来去除不必要的信息，用GET_DDL函数来获取对象的DDL。

　　splplus的设置主要有:

```sql
SET ECHO OFF
SET TRIMSPOOL ON
SET VERIFY OFF
SET FEEDBACK OFF
SET FEED OFF
SET TIMING OFF
SET LINESIZE 4000
SET PAGESIZE 1000
SET LONG 90000
SET NEWPAGE NONE
SET HEADING OFF
SET TERMOUT OFF
SET WRAP ON
```

设置DDL中哪些信息不取:

```sql
BEGIN 
    -- 不要 STORAGE 的信息
    DBMS_METADATA.SET_TRANSFORM_PARAM( DBMS_METADATA.SESSION_TRANSFORM
                                     , 'STORAGE'
                                     , FALSE
                                     );
    -- 不要 TABLESPACE 的信息
    DBMS_METADATA.SET_TRANSFORM_PARAM( DBMS_METADATA.SESSION_TRANSFORM
                                     , 'TABLESPACE'
                                     , FALSE
                                     );
    -- 不要 SEGMENT_ATTRIBUTES 的信息
    DBMS_METADATA.SET_TRANSFORM_PARAM( DBMS_METADATA.SESSION_TRANSFORM
                                     , 'SEGMENT_ATTRIBUTES'
                                     , FALSE
                                     );
    -- 对 DDL 语句进行简单的格式化
    DBMS_METADATA.SET_TRANSFORM_PARAM( DBMS_METADATA.SESSION_TRANSFORM
                                     , 'PRETTY'
                                     , TRUE
                                     );  
    -- 每条 DDL 语句后加分号
    DBMS_METADATA.SET_TRANSFORM_PARAM( DBMS_METADATA.SESSION_TRANSFORM
                                     , 'SQLTERMINATOR'
                                     , TRUE
                                     );
    -- 不要约束的信息
    DBMS_METADATA.SET_TRANSFORM_PARAM( DBMS_METADATA.SESSION_TRANSFORM
                                     , 'CONSTRAINTS'
                                     , FALSE
                                     );
END;
/
```

　　为防止导出的语句内出现折行，必须设定 COLUMN 的宽度。这个值默认是200字节，最大可达60000字节。

```sql
COL DDL_STR FORMAT A30000
```

脚本代码：

- [导出表结构](https://github.com/paxinla/orasql/blob/master/ExportDDL4Table.sql)
- [导出视图](https://github.com/paxinla/orasql/blob/master/ExportDDL4View.sql)
- [导出类型](https://github.com/paxinla/orasql/blob/master/ExportDDL4Type.sql)
- [导出序列](https://github.com/paxinla/orasql/blob/master/ExportDDL4Sequence.sql)
- [导出函数](https://github.com/paxinla/orasql/blob/master/ExportDDL4Function.sql)
- [导出存储过程](https://github.com/paxinla/orasql/blob/master/ExportDDL4Procedure.sql)
- [导出包](https://github.com/paxinla/orasql/blob/master/ExportDDL4Package.sql)

