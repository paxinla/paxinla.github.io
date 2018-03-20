Title: Windows下Emacs的shell-mode乱码解决
Date: 2015-07-12 13:26:04
Category: 故障
Tags: Emacs, shell-mode, Windows
CommentId: 5


# shell-mode 中文乱码

办公室电脑系统 Windows 7 ，装的是 Emacs24 。在 Emacs 中切到 shell-mode ，使用的是 windows 的 cmd 。使用 dir 命令可以看到中文目录名正常显示。但是输入的中文（外部输入法：微软拼音输入法）不能正常显示。如输入 "echo 是" 回车后看到的是乱码。这种现象只在 shell-mode 中存在。

<!-- PELICAN_END_SUMMARY -->

根据网上搜到的方法，在 .emacs 中加入 (ansi-color-for-comint-mode-on) ，不能解决问题。


起初的 .emacs 中，我是根据网上搜到的参数来配置如下：

```lisp
;; 设置为中文简体语言环境
(set-language-environment 'Chinese-GB)
;; 设置emacs 使用 utf-8
(setq locale-coding-system 'utf-8)
;; 设置键盘输入时的字符编码
(set-keyboard-coding-system 'utf-8)
(set-selection-coding-system 'utf-8)
;; 文件默认保存为 utf-8
(set-buffer-file-coding-system 'utf-8)
(set-default buffer-file-coding-system 'utf8)
(set-default-coding-systems 'utf-8)
;; 解决粘贴中文出现乱码的问题
(set-clipboard-coding-system 'utf-8)
;; 终端中文乱码
(set-terminal-coding-system 'utf-8)
(modify-coding-system-alist 'process "*" 'utf-8)
(setq default-process-coding-system '(utf-8 . utf-8))
(setq-default pathname-coding-system 'utf-8)
(set-file-name-coding-system 'utf-8)
```

经过多次尝试，发现修改以下参数时，对 shell-mode 下的中文显示和输入问题有效:

```lisp
(modify-coding-system-alist 'process "*" 'gbk)
(setq default-process-coding-system '(gbk . gbk))
(setq-default pathname-coding-system 'gbk)
(set-file-name-coding-system 'gbk) 
```

但是会影响到其他 mode 下的中文显示，比如我的 org-mode 就会受影响。最后的 .emacs 设置为：

```lisp
;;;; 设置编辑环境
;; 设置为中文简体语言环境
(set-language-environment 'Chinese-GB)
;; 设置emacs 使用 utf-8
(setq locale-coding-system 'utf-8)
;; 设置键盘输入时的字符编码
(set-keyboard-coding-system 'utf-8)
(set-selection-coding-system 'utf-8)
;; 文件默认保存为 utf-8
(set-buffer-file-coding-system 'utf-8)
(set-default buffer-file-coding-system 'utf8)
(set-default-coding-systems 'utf-8)
;; 解决粘贴中文出现乱码的问题
(set-clipboard-coding-system 'utf-8)
;; 终端中文乱码
(set-terminal-coding-system 'utf-8)
(modify-coding-system-alist 'process "*" 'utf-8)
(setq default-process-coding-system '(utf-8 . utf-8))
;; 解决文件目录的中文名乱码
(setq-default pathname-coding-system 'utf-8)
(set-file-name-coding-system 'utf-8)
;; 解决 Shell Mode(cmd) 下中文乱码问题
(defun change-shell-mode-coding ()
  (progn
    (set-terminal-coding-system 'gbk)
    (set-keyboard-coding-system 'gbk)
    (set-selection-coding-system 'gbk)
    (set-buffer-file-coding-system 'gbk)
    (set-file-name-coding-system 'gbk)
    (modify-coding-system-alist 'process "*" 'gbk)
    (set-buffer-process-coding-system 'gbk 'gbk)
    (set-file-name-coding-system 'gbk)))
(add-hook 'shell-mode-hook 'change-shell-mode-coding)
(autoload 'ansi-color-for-comint-mode-on "ansi-color" nil t)
(add-hook 'shell-mode-hook 'ansi-color-for-comint-mode-on) 
```

问题解决。
