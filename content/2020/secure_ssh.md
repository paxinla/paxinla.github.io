Title: SSH 的安全设置
Date: 2020-05-29 17:22:03
Category: 工具
Tags: ssh, security
CommentId: X


ssh 的基本安全设置。

<!-- PELICAN_END_SUMMARY -->

一般我对服务器上的 ssh 服务，至少[ps: 更改默认端口、加上 fail2ban 之类的另说。]会设置 `/etc/ssh/sshd_config` :

```bash
PasswordAuthentication no
ChallengeResponseAuthentication no
PubkeyAuthentication yes
AuthorizedKeysFile .ssh/authorized_keys .ssh/authorized_keys2
PermitEmptyPasswords no
PermitRootLogin no
```

但是这样的设置是不够的，需要更多额外的安全设置。如果密钥使用的是 RSA 算法生成，则还需注意 RSA 的长度需要足够长(4096以上)。

比如，客户端生成密钥文件时，使用足够安全的方式:

```bash
ssh-keygen -t ed25519 -o -a 100
ssh-keygen -t rsa -b 4096 -o -a 100
```

本文里额外的安全设置，主要采用了 stribika 的 [这篇文章](https://stribika.github.io/2015/01/04/secure-secure-shell.html) 里的结论。


关闭 OpenSSH 的 UseRoaming 特性，在服务器上，设置 `/etc/ssh/ssh_config` :

```bash
Host *
    UseRoaming no
```


### 密钥交换

为了使密钥交换更安全，在服务器上，设置 `/etc/ssh/sshd_config` :

```bash
KexAlgorithms curve25519-sha256@libssh.org,diffie-hellman-group-exchange-sha256
```

设置 `/etc/ssh/ssh_config` :

```bash
Host *
    KexAlgorithms curve25519-sha256@libssh.org,diffie-hellman-group-exchange-sha256
```

### 认证

在服务器上，重新生成新的更安全的 key 文件:

```bash
cd /etc/ssh
sudo rm ssh_host_*key*
sudo ssh-keygen -t ed25519 -f ssh_host_ed25519_key -N "" < /dev/null
sudo ssh-keygen -t rsa -b 4096 -f ssh_host_rsa_key -N "" < /dev/null
```

在服务器上，设置 `/etc/ssh/ssh_config` :

```bash
    Protocol 2
    HostKey /etc/ssh/ssh_host_ed25519_key
    HostKey /etc/ssh/ssh_host_rsa_key

    PasswordAuthentication no
    ChallengeResponseAuthentication no

    PubkeyAuthentication yes
    HostKeyAlgorithms ssh-ed25519-cert-v01@openssh.com,ssh-rsa-cert-v01@openssh.com,ssh-ed25519,ssh-rsa
```

可以考虑在服务器上的 `/etc/ssh/sshd_config` 里设置 `AllowGroups` ，通过用户组来管理允许ssh登录的用户。


### 通信内容加密

在服务器上，设置 `/etc/ssh/sshd_config` :

```bash
Ciphers chacha20-poly1305@openssh.com,aes256-gcm@openssh.com,aes128-gcm@openssh.com,aes256-ctr,aes192-ctr,aes128-ctr
```

在服务器上，设置 `/etc/ssh/ssh_config` :

```bash
Host *
    Ciphers chacha20-poly1305@openssh.com,aes256-gcm@openssh.com,aes128-gcm@openssh.com,aes256-ctr,aes192-ctr,aes128-ctr
```


### MACs

在服务器上，设置 `/etc/ssh/sshd_config` :

```bash
MACs hmac-sha2-512-etm@openssh.com,hmac-sha2-256-etm@openssh.com,umac-128-etm@openssh.com,hmac-sha2-512,hmac-sha2-256,umac-128@openssh.com
```

在服务器上，设置 `/etc/ssh/ssh_config` :

```bash
Host *
    MACs hmac-sha2-512-etm@openssh.com,hmac-sha2-256-etm@openssh.com,umac-128-etm@openssh.com,hmac-sha2-512,hmac-sha2-256,umac-128@openssh.com
```
