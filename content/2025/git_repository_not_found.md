Title: git push ssh key 不匹配的问题
Date: 2025-03-03 10:34:55
Category: 故障
Tags: git, github
CommentId: X

git push 遭遇 ERROR: Repository not found.

<!-- PELICAN_END_SUMMARY -->

## 迷惑人的错误提示信息

今天，在 push 提交到一个一直以来都能正常 pull/push 的 github 仓库时失败了，遭遇 `ERROR: Repository not found.` 。报错信息倒是有提到要我确认是否有权限对仓库进行操作。

这个仓库是我在 github.com 上，在公司的路径下创建的一个私有仓库，在仓库的 *Collaborators and teams* 里，我的角色是 *Role:admin* ，当然是有读写的权限的。何况一周前我还推送过提交，一切都很正常。

既然一直以来都能正常推送，那也不会是 **remote-url** 的问题， `git remote -v` 看到的值和仓库网页上 `Code -> Clone -> SSH` 里的值，完全一致，并无更改。

在本地仓库里，执行 `ssh -T -v git@github.com` ，可以看到是哪些 ssh key 文件被选择使用，结果能正常 authenticate 。这个测试没能提供什么有用的信息。

在本地仓库里，执行 `git config -l` 和 `git config --local -l` 。可以看到我在本地仓库里是重新设定了 **user.name** 和 **user.email** 的，它们的值与全局设置的 name 和 email 不同。

再在 github.com 的个人(不是仓库)的 `Settings -> SSH and GPG keys -> SSH keys` 页面上查看，发现不知为何没有对应本地仓库 **user.email** 的 ssh 公钥条目。


## 是 ssh key 的设置问题

既然是缺失 ssh 公钥造成的，那就再补上。首先，如果本地没有对应 **user.email** 的 ssh key 的话，就新生成一对:

```sh
ssh-keygen -t ed25519 -C "yourmail@somewhere.com"
```

这里的 "yourmail@somewhere.com" 填的是本地仓库里设置的 **user.email** 的值。然后编辑本地的 ssh 配置文件，如 `~/.ssh/config` ，加入如下配置:

```
Host github.com
HostName github.com
User useraaa
IdentityFile ~/.ssh/id_ed25519
IdentitiesOnly yes
```

这里的 **User** 填写的是本地仓库里设置的 **user.name** 的值， **IdentityFile** 填写的是新生成的 ssh key 对里的 **私钥文件** 的路径。

打开 github.com 的个人(不是仓库)的 `Settings -> SSH and GPG keys -> SSH keys` 页面，点击“New SSH key”按钮，添加新生成的 ssh key 对里的 **公钥文件** 的内容。

如果有在使用 ssh-agent 的话，还需要 ssh-add 新生成的 ssh key 对里的 **私钥文件** 。

至此，已经能正常地在本地仓库里与远程的 github 仓库进行交互了。

