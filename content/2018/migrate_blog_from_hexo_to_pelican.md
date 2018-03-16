Title: 迁移博客到 Pelican
Date: 2018-03-16
Category: 工具
Tags: Pelican, Hexo


又开始写博客了。

<!-- PELICAN_END_SUMMARY -->

## 为什么用 Pelican

当初使用 Hexo 来搭建博客，是因为觉得很多 Hexo 的主题很酷，Hexo 生成页面的命令也很方便。但是在某次 Hexo 升级之后，就无法生成博客页面了，加上我也懒，博客也就停更了近两年多。比起 JS ，我还是更熟悉 Python ，而且 Pelican 没有太多功能，简洁，很对我的口味，Python 也容易锁死 Pelican 的版本。因此我决定把个人博客从 Hexo 转到 Pelican 。

## 还是有一点点坑

最大的问题还是主题。过去用 Hexo 的时候，主题是用 [Modernist](https://github.com/heroicyang/hexo-theme-modernist) 的主题修改的。换成 Pelican 的话，不想再折腾这个主题了。直到某天我看到了 [CachesToCaches](http://cachestocaches.com) 的主题和它介绍自己的设计理念。现在本博客的主题就是基于它的主题修改而成。

![Hexo时代用的主题](/images/hexo_blog_snapshot.png)

Pelican 的代码高亮我是没用成功的，它解析我 Markdown 里的 Github 风格的代码块 [ps: 以 `` 3个反引号 ` 加语言名称开头 ``的多行代码] 的结果，总是一对 pre 的标签，没有 code 标签，也没有把语言名称这个信息带出来。自带的 Markdown 扩展 fenced_code 是无效的。好在 Pelican 的插件机制提供了许多钩子，很容易就写了个自己的扩展，来将 Markdown 里的反引号代码块在 Pelican 将它转换为 HTML 前，包装在 pre>code 标签中，并在 code 标签里，加上 class="lang-语言名称"。然后在模板中引用 [Prism](http://prismjs.com/) 的 css 及 js ，就可以实现代码块高亮功能了。

用 [Travis-CI](http://travis-ci.org) 来监控博客的 Github 库，在 Github 上直接用 Web 编辑器写 Markdown 格式的博客，保存后就会产生一个提交，自动触发页面的生成。

从决定将博客从 Hexo 转到 Pelican 到实施完成，前后用了3天时间。绝大部分时间还是花在了主题上面，最后的效果还是比较满意的 ^_^。
