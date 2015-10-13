# obtainfo
欧泊影视网站数据

# 知识库
## git sock5 proxy
1. 
gang@debian:~$ sudo apt-get install netcat-openbsd

gang@debian:~$ cat /usr/local/bin/git-proxy-wrapper
```#!/bin/bash
nc -xlocalhost:1080 -X5 $*
```
gang@debian:~$ export GIT_PROXY_COMMAND=/usr/local/bin/git-proxy-wrapper

2. 配置 ~/.gitconfig

[core]
gitproxy = /PATH/TO/socks5proxywrapper
或者直接设置 GIT_PROXY_COMMAND 环境变量

export GIT_PROXY_COMMAND=”/PATH/TO/socks5proxywrapper”
