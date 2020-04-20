Title: 在 XPS 13 7390 上安装 Ubuntu
Date: 2020-03-17 15:31:08
Category: 工具
Tags: xps ubuntu i3
CommentId: X


## XPS 13 7390

为自己工作挑选专用笔记本，千挑万选最终选择了戴尔的 XPS 13 7390 (not 2 in 1)。

- 第一个理由，够轻够小的本本里，XPS 的接口算是够用的，当然比 Thinkpad 的接口还是少了。
- 第二个理由，是 XPS 对 Linux 的支持最好，配置较合理[ps: 内存和硬盘一次加够。]，工作够用，特别是没有鸡肋的独显[ps: 娱乐需求靠台式机，笔记本纯工作。]。触摸屏也不需要。
- 第三个理由，是颜值高，和 macbook 有得拼。13 机子里塞进了14尺的屏幕，边框窄，看着并不难受。

国内买不到 Developer Edition ，预装的 Windows 10 中文家庭版。自己装的 Ubuntu 18.04 + i3wm 的方案。

<!-- PELICAN_END_SUMMARY -->

## Ubuntu 18.04

XPS 13 的 BIOS 已经不支持 Legacy Mode 了，所以安装U盘需要以 UEFI+GPT 的方式制作。

开机出现 DELL logo 按 F12 进入 UEFI 。首先，在 "System Configuration" 里设置 SATA Operation 为 AHCI 模式；[ps: 机器预装的 Win10 是采用的 Raid0 模式。] 关闭 SMART Reporting ，打开 USB 及雷电3接口的 bootable 选项。接着，在 "Secure Boot" 里关闭 Secure Boot 。可选的，在 "POST Behaviour" 里将 Fastboot 的选项设置为 Thorough 。

设置完这些，还需要在 "Boot Options" 里手动添加启动项，选择 `/EFI/BOOT/grubx64.efi` 文件。[ps: EFI 期望默认的引导装载程序时 /EFI/BOOT/BOOTx64.EFI ，但我用 grubx64.efi 才成功了。]

戴尔笔记本有个“动态屏幕亮度调节”的特性，机器会根据屏幕上显示的内容自动调节屏幕亮度，给人的感觉像是在闪烁，关闭这个特性，需要在 UEFI 中关闭 "Video" 中的 EcoPower 。

保存退出后，插上启动U盘重启，选择自己手工添加的启动项，即可进入 Ubuntu 安装界面。安装过程按部就班，没什么特别的地方。主要是在硬盘分区时，必须要有 EFI 分区，并指定系统从这个 EFI 分区引导。我没打算留预装的 Win10 ，直接用了它名为 "Windows Manager" 的 EFI 分区来引导 Ubuntu 。

XPS 对 Ubuntu 的支持很好，除了电源开关键上的指纹识别用不了外[ps: 据说随着 XPS 13 2020 版的发售，Ubuntu 下的指纹识别也将支持。]，所有的硬件都工作得很好。

戴尔有个命令行的管理工具 "Dell Command | Configure 4.2.1"，可以到 [这里下载](https://www.dell.com/support/article/zh-cn/sln311302/dell-command-configure?lang=en) 。

开机时的 grub 系统菜单如果想跳过，修改 /etc/default/grub ，设置 `GRUB_DISABLE_OS_PROBER=true` 。

开机进入系统后，有时会弹出 系统出现问题 的提示框(崩溃文件记录在 /var/crash 下)。如果觉得烦，可以修改 /etc/default/apport 里修改 `enabled=1` 为 `enabled=0` 。

Ubuntu 的网卡名称与众不同，不喜欢的话，可以在 /etc/default/grub 中找到 `GRUB_CMDLINE_LINUX=""` ，改为 `GRUB_CMDLINE_LINUX="net.ifnames=0 biosdevname=0"` ，网卡名称就会变得“传统”些。

修改完 /etc/default/grub ，记得执行 `sudo update-grub` 。


## i3wm

安装上我惯用的 i3[ps: 默认安装的 gnome 也没删。] + [i3-gaps](https://github.com/Airblader/i3) + [rofi](https://github.com/davatorium/rofi)[ps: rofi 的美化可参考: https://github.com/davatorium/rofi-themes] 。在 i3 下，终端用了 roxterm ，设置默认 shell 为 zsh ，加 [oh-my-zsh](https://github.com/ohmyzsh/ohmyzsh) + [spaceship-prompt](https://github.com/denysdovhan/spaceship-prompt) (以前的 spaceship-zsh-theme) [ps: fish 对 bash 的兼容不好，不考虑。]。文件浏览器还是用的 nautilus ，启动时加 `--no-desktop` 选项即可。(如果出现了图标缺失的情况，需要安装如 Faenza-icon-theme 这样在 gnome 和 i3 下都兼容的图标主题)。多媒体文件用 vlc 即可搞定。壁纸用 feh 显示。Fn 功能键的控制，有的需要在 i3 的配置文件设置。最小化安装的 Ubuntu 不带 playerctl (媒体功能控制) 、light (屏幕亮度控制) ，需要自行安装。音量控制用 amixer ，不用 pactl 。

锁屏我用的 i3lock ，它现在只支持 png 格式的图片作为锁屏背景图。解锁时，直接输入密码，回车。虽然屏幕没有显示任何东西，但是其实是输入进去了的。不知道这个的话，可能会在 "Verifying" 的圆圈那里感到迷惑。

使用 xrandr 管理屏幕输出，它对外接显示器的支持也不错，不过需要自己在 i3 的配置文件中设置。

状态栏我没有使用 i3 的 status bar ，而是用了 polybar ，如果嫌自己设置太麻烦，可以到 [https://github.com/adi1090x/polybar-themes](https://github.com/adi1090x/polybar-themes) 里选一个修改[ps: 有的方案有多个字体的下的设置，需根据自己机器上预览的效果，确定最终使用的配置。]。注意 polybar 的很多“图标”其实是字体，需要自行安装。polybar 的 `internal/xbacklight` 是不支持 XPS 的，换成 `internal/backlight` 。

触摸板在 gnome 下工作得很好，在 i3 下却没有默认开启 tap 功能。不建议使用如:

```vim
xinput set-prop <device> <property> 1
```

这样的方式来修改。新增文件 `/usr/share/X11/xorg.conf.d/90-touchpad.conf` ，内容为:

```vim
Section "InputClass"
        Identifier "libinput touchpad catchall"
        MatchIsTouchpad "on"
        Driver "libinput"
        Option "Tapping" "on"
        Option "TappingButtonMap" "lrm"
        Option "NaturalScrolling" "on"
        Option "ScrollMethod" "twofinger"
EndSection
```

Tapping=on 是单指点击为鼠标左键；TappingButtonMap=lrm 是两指点击为鼠标右键、三指点击为鼠标中键；ScrollMehtod=twofinger 是两指滑动为滚动效果，如果改为 edge 则是在触摸板的边缘滑动为滚动效果。


输入法用的是 fcitx-rime 。fcitx 的输入法和皮肤似乎是分开的，皮肤文件要放到 `$HOME/.config/fcitx/skin` 下[ps: 在 http://github.com/fcitx/fcitx-artwork 可以下载到一些皮肤]，再在 fcitx-config 里设置“外观”。


