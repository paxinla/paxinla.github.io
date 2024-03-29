Title: 跨平台的离线 cheatsheet 方案
Date: 2019-09-12 15:56:02
Category: 生活
Tags: cheatsheet, vim
CommentId: X

稳定的 cheatsheet 工具很有必要。

<!-- PELICAN_END_SUMMARY -->

## 从 cheat 到 vim helpfile

　　最近把原先使用 <a href="https://github.com/cheat/cheat">cheat</a> 管理的 cheatsheet 文档都改为使用 Vim 的 help 文档。解决了跨平台的离线 cheatsheet 的显示、搜索问题。

　　我办公室的 PC 是装的 Debian ，家里的 PC 是 Windows 。cheat 在 Linux 上工作得不错，但是在 Windows 下的表现糟糕透了，既难装又难看。

　　因为我日常在 Debian 和 Windows 上都有使用 Vim (因它在两个平台的表现都很稳定，不像 Emacs 在 Windows 上有很多问题，而且启动速度快)，一番尝试后，决定利用 Vim 自身的帮助文档系统来管理我的 cheatsheet 文档。这样无论在哪个平台，在 Vim 里都能正常显示文档内容，自带语法高亮。能利用 help 的 tag 系统，Vim 提供了 helpgrep 等工具来方便查找内容。

　　这个方案需要满足以下条件:
1. 机器上装有 Vim ，不需要其他依赖。
2. 文档目录的结构需为 XXX/doc 形式，文档都放到 doc 下面。把 XXX 加入到 Vim 的查找路径中。
3. 文档本身就是普通的文本文件，但需要组织为 Vim 的 helpfile 格式。

### 安装 Vim

　　Vim 在多个平台上都有安装方案，这个参考<a href="https://www.vim.org/download.php">官网</a>上的信息就可以了，在 Linux 和 Windows 上的安装都是很简单的。


### cheatsheet 的文档组织

　　我用 git 来管理 cheatsheet 文档，当然也可以用如 Dropbox 之类的文件同步工具。设文档目录在 PC-A 机器(Linux)上的路径为: `~/document/cheat` ，在 PC-B 机器(Windows)上的路径为 `E:\MyDocuments\cheat` 。

　　cheatsheet 文件都放到 cheat 目录下的 doc 目录下。在 PC-A 的 vimrc (默认位置为 ~/.vimrc)中设置 `set rtp+=~/document/cheat` ，在 PC-B 的 vimrc (默认在安装目录下的 `_vimrc`)中设置 `set rtp+=E:\MyDocuments\cheat` 。这样 Vim 就可以找到这些 cheat 下 doc 里的文档了。

　　为了方便浏览，我建了一个单独的文档作为其他 cheatsheet 文档的目录[ps: 这个目录文件不是必须的。]，格式仿照 Vim 自带的 help.txt 。在 Vim 中执行 `:set helpfile?` 可以看到当前 Vim 的默认 help 目录文件。在 Vim 中执行 `:help` 时就是打开的这个目录文件。


### cheatsheet 的文档格式

　　cheatsheet 的文档为文本文件，格式如下:

```vim
*标签*     大标题     最后更新时间:XXXX年Y月
*另一个标签*


介绍之类的文字。


===============================================================================
目录

    1. 第一小标题 ...................................... |小标题1的标签|
    2. 第二小标题 ...................................... |小标题2的标签|

===============================================================================
第一小标题                                               *小标题1的标签*

正文


-------------------------------------------------------------------------------
第二小标题                                               *小标题2的标签*

正文


-------------------------------------------------------------------------------
vim:tw=78:ts=8:ft=help:norl:
```


　　文件第一行的格式是必须严格遵守的，必须是三列字段，不可省略。第一个字段须是标签，但内容一般就是文件名，如: git.txt 。第二个字段一般是标题，其实写啥都行。第三个字段一般是最后修改日期，其实写啥都行。

　　文件如果需要有多个标签标识的，通常其他标签从第二行起，每行一个标签。

　　文件的尾部一般都是以 `vim:` 开头的一些文档设置项。

　　中间的内容其实都随便写，可以参考 vimfiles/doc 下面 VIM 自带的帮助文档来写。

　　Vim 的标签格式为英文星号括起来的文字，链接的格式为英文竖线括起来的文字(内容与标签中文字一致)。这样在利用 Vim 的 helptags 命令生成 tags 文件后，当光标位于链接上时，按下 `Ctrl + ]` 就会跳转到相应标签所在位置。


### 使用帮助文档系统

　　完成了上述的工作后，在 Vim 中执行: `:helptags ALL` ，VIM 就会为所有的帮助文档(包括我们的cheatsheet文档)生成名为 tags 的文件[ps: 这就是普通的文本文件，你甚至可以手写一个这样的文件，只要格式符合且文件名为 tags 。]，有了这个文件，在用 VIM 打开有链接的文件时，就可以用 `Ctrl + ]` 跳转到相应的标签所在的位置。

　　如果在生成 tags 时，遇到错误码为 E670 的报错信息时，看看是不是因为文件的首行格式不对。

　　现在，在 Vim 中执行 `:h 标签名` 可以直接打开相应标签所在文档。执行 `:helpgrep 模糊搜索` 可以所有帮助文档中的匹配内容。
