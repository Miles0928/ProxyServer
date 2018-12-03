# 代理转发

代理手机网络到PC端

## 使用方法

应用场景：PC端能访问IPv6网络，移动端无法访问IPv6网络。通过代理转发，使移动端访问相应资源。

1. PC端运行程序：python ProxyTool.py
2. 移动端连接WIFI，设置代理地址为IP，端口信息。（代理IP为PC端IPv4，端口设置为代理端口，默认为8000）

## 设置项

设置文件位于data目录下，具体说明如下：
1. config.json: 设置代理IP及端口，默认为本机全部可用IP，端口为8000
2. host.json: 设置域名-IP对，可用于程序直接查询IP信息（IPv4、IPv6均可）
3. blocklist.txt: 设置黑名单，通过域名禁止访问
4. proxylist.txt：设置代理名单，转发数据到8087端口，可用于GAE
