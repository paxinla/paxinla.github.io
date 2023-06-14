Title: 去除 Ubuntu 的 snap
Date: 2023-06-14 14:43:44
Category: 工具
Tags: ubuntu, snap
CommentId: X


<!-- PELICAN_END_SUMMARY -->

## 起因

我使用的 Ubuntu 18.04 上，如果键入 `lsblk` 或 `fdisk -l` ，会看到很多的 loop 设备。snap 是 Ubuntu 在强推的一个软件安装工具，这些 loop 则是 [snap 管理它安装的软件版本的方式](https://docs.snapcraft.io/core/versions) 。为了让我的设备列表能干净些，需要彻底去除 snap 。


## 操作步骤

snap 安装的软件，可以通过 `snap list` 列出来。通常应该会有一些 gnome 的组件，其他的都是可以无忧删除的，完全可以通过 apt 或 deb 的方式再安装。


首先，先通过 snap 卸载掉那些本就已经不再使用的软件。执行 bash 脚本:

```sh
#!/bin/bash
set -eu
snap list --all | grep -vE "^Name" | awk '/disabled/{print $1,$3}' |
    while read snapname revision; do
        sudo snap remove "$snapname" --revision="$revision"
    done
```

接着，彻底卸载 snapd (这个过程会自动删除掉 `/var/cache/snapd`):

```sh
sudo apt autoremove --purge snapd gnome-software-plugin-snap
sudo apt-mark hold snapd
```

重新安装 gnome 相关包，但不要通过 snap 的方式:

```sh
sudo apt install --no-install-recommends gnome-software
```

即使卸载了 snapd ，在更新系统及软件时，Ubuntu 还是有可能会再安装上 snap 。这需要修改 preferences 。编辑 `/etc/apt/preferences.d/nosnap.pref` :

```
Package: snapd
Pin: release a=*
Pin-Priority: -10
```

 ᕙ(•̤᷆ ॒ ູ•̤᷇)ᕘ₊˚ 收工。

