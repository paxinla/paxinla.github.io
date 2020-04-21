Title: Hexo的一个问题
Date: 2015-06-07 10:03:00
Category: 故障
Tags: hexo
CommentId: 3


# Windows下Hexo升级后deploy问题

　　今天升级 hexo ，在 cmd (系统是 Win8 )中执行了 `hexo d`，显示不认识 github 。

<!-- PELICAN_END_SUMMARY -->

　　根据[官网Wiki的部署章节](http://hexo.io/zh-cn/docs/deployment.html)执行 `npm install hexo-deployer-git --save` 安装 deployer ，并把 `_cofing.yaml` 中的 deploy 这个 section 下的 type 值从 github 改为 git 后，再执行 `hexo d` ，显示如下：

```
INFO  Deploying: git
INFO  Clearing .deploy folder...
INFO  Copying files from public folder...
events.js:85
      throw er; // Unhandled 'error' event
            ^
Error: spawn git ENOENT
    at exports._errnoException (util.js:746:11)
    at Process.ChildProcess._handle.onexit (child_process.js:1053:32)
    at child_process.js:1144:20
    at process._tickCallback (node.js:355:11)
```

　　解决这个错误的方法是不在 cmd 下使用 hexo ，而是在 git bash 中。再执行 `hexo d` ，又报 Not a gitreposity 错误。在 git bash 下到博客目录下的 `.deploy_git` 中执行 `git init` （`_config.yaml` 里已配置好 repo 的地址），再次执行 `hexo d` ，部署成功！
