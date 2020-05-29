Title: 浅谈缓慢变化维
Date: 2020-04-20 15:38:25
Category: 数据仓库
Tags: datawarehouse, star-schema
CommentId: X


最近我被问到，如何向一个完全不了解数据仓库/星型模式的人简要地解释什么是“缓慢变化维”。

<!-- PELICAN_END_SUMMARY -->

既然假设听众完全不了解星型模式，那么简要地向他介绍“事实”与“维度”的概念是必要的。

在用于支持业务过程的分析场景下，分析是通过对业务过程度量来实现的。业务过程数据中的“度量”被称为“事实”，度量的应用“环境”被称为“维度”。大多数事实是数值，通常可以对它们进行汇总。维度通常充当条件过滤器、定义分组或者分类汇总的层次等。

按 Ralph Kimball 自己在其著作[ref]<i>The Data Warehouse Toolkit: The Definitive Guide to Dimensional Modeling, Third Edition</i>. ISBN: 978-7-302-38553-0[/ref]里说的，“维度表属性相对稳定，但它们还是会发生变化的，尽管相当缓慢，属性值仍会随时间发生变化”。这里“缓慢变化”维的“缓慢”，应该是指与积累数据行较为快速的事实表比较，维度积累变化相对缓慢。所以叫“缓慢”变化维(Slowly Changing Dimension, SCD)，也有人译作“渐变维”的。

通常说的“拉链表”，指的是处理缓慢变化维的典型技术中的“变化类型2”。