# DNS Relay 编程作业

姓名：施楚峰

学号：PB18000335

## 实验要求
---
设计一个程序，使得它能从配置文件中读取“主机名—— IP 地址”的列表，并且能够解决如下高并发的 DNS 请求。
- 拦截：在读取的文件中能找到所请求的主机名，并且与其关联的IP地址为 “0.0.0.0” 则组成相应报文返回 0.0.0.0；
- 本地解析：在读取的文件中能找到所请求的主机名，并且关联有一个有意义的 IP 地址，组成相应报文返回相应的 IP 地址；
- 中继：如果找不到所请求的主机名，则将客户端的请求转发至远程 DNS 服务器，并同样的将从远程 DNS 服务器取得的 DNS 响应报文返回客户端。

对于每一个请求，程序还应输出：
- 被请求的主机名；
- 请求是怎样处理的（拦截/本地解析/中继）；
- 处理请求所花费的时间。

## 设计思路
---
每一个 DNS 请求到来后，创建一个线程来处理这个请求。先在本地 DNS 库中查找所请求的主机名，尝试拦截或者本地解析，如果找不到，那么往消息队列中添加一个向远程 DNS 服务器请求解析的任务。另有两类线程，分别用对应相同的 TCP Socket 向远程 DNS 服务器发送和接收信息，在接收线程接收到 DNS 响应报文后，向客户端返回，并输出相应信息。

## 文件及依赖关系
---
本次编程作业我选择的是 python 语言进行编写。项目共包含七个文件，五份 python 代码文件如下图所示，一个 hosts 的地址配置文件以及一个 conf.ini 的程序配置文件。
各文件具体用途及 python 代码间的相互依赖关系见下。

| 名称        | 主要用途                                                                                                        |
| :---------- | :-------------------------------------------------------------------------------------------------------------- |
| localdns.py | 读取本地 hosts 信息，并提供本地 DNS 解析服务                                                                  |
| server.py   | 程序入口，创建程序所需的套接字及线程，接收 DNS 请求报文并创建一个调用 threads.py 中处理程序的线程处理相关请求 |
| settings.py | 从 conf.ini 读取程序配置信息                                                                                  |
| threads.py  | 实现了 DNS relay 中线程安全的拦截、本地解析、中继的逻辑。                                                       |
| utility.py  | 提供了一个可以解析 DNS 报文的类                                                                                 |
| hosts       | 本地 DNS 地址库                                                                                                 |
| conf.ini    | 程序配置文件，配置了远程 DNS 服务器等信息                                                                       |

<table>
    <tr>
        <td width="20%" style="border-style:none">
            <img src="http://home.ustc.edu.cn/~cfshi/ftp/picture_bed/dnsrelay/file_list.png" alt="file_list" />
        </td>
        <td width="47%" style="border-style:none">
            <img src="http://home.ustc.edu.cn/~cfshi/ftp/picture_bed/dnsrelay/main_rely.png" alt="main_rely" />
        </td>
    </tr>
</table>

![settings_rely](http://home.ustc.edu.cn/~cfshi/ftp/picture_bed/dnsrelay/settings_rely.png)
![threads_rely](http://home.ustc.edu.cn/~cfshi/ftp/picture_bed/dnsrelay/threads_rely.png)
![localdns_rely](http://home.ustc.edu.cn/~cfshi/ftp/picture_bed/dnsrelay/localdns_rely.png)
![utility_rely](http://home.ustc.edu.cn/~cfshi/ftp/picture_bed/dnsrelay/utility_rely.png)


## 程序解释
---
### settings.py
settings.py 实现了两个类 `LOG_LEVEL` 和 `conf`，`LOG_LEVEL` 继承自枚举类，在 `conf.log_level` 中使用。最后 `settings` 为 `conf` 类的实例。

`conf` 类从 conf.ini 读取相应的配置信息后保存以供其他程序使用。`show_info()` 函数用于在标准输出打印保存的配置信息。

<img src="http://home.ustc.edu.cn/~cfshi/ftp/picture_bed/dnsrelay/settings_file.png" alt="settings_file" width = "45%"/>


### utility.py
`sys_pause()` 为使调试方便而实现的程序暂停函数。

`parser` 类通过一个 DNS 报文实现初始化，并且解析出 DNS 报文的各个字段，以便其他程序中对 DNS 报文进行分析。其中 `parse_HEADER()`、`parse_QUESTION(pos)` 和 `parse_RESPONSE(pos)` （实际未用）分别解析报文的首部区域、问题区域及回答区域，并利用 `parse_domain(pos)` 来解析所请求或返回的主机名。

<img src="http://home.ustc.edu.cn/~cfshi/ftp/picture_bed/dnsrelay/utility_file.png" alt="utility_file" width = "65%"/>

### localdns.py
localdns.py 实现了两个类，`file` 和 `dns`，其中 `dns` 继承自 `file`，最后 `localdns` 为 `dns` 类的实例。

`file` 从 hosts 文件（默认）读取配置的域名记录，以字典方式保存在 `addr_dict` 中；`lookup(domain)` 函数接受一个域名，在字典中查询该域名并返回一个二元组，查找成功为 `(True, IP address)` 失败为 `(False, None)`。

`dns` 在 `file` 基础上实现 `nslookup(request)` 函数，它接受一个 DNS 请求报文，利用 utility.py 中的 `parser` 模块对报文进行解析，提取出所查询的域名并调用 `lookup(domain)` 函数进行查找。如果查找成功，则根据 `lookup(domain)` 返回得到的 IP 地址组装成相应的 DNS 响应报文（根据返回 IP 地址不同，可分类为拦截或本地解析）并返回 `(True, response)`，若查找失败则返回 `(False, None)`。

<img src="http://home.ustc.edu.cn/~cfshi/ftp/picture_bed/dnsrelay/localdns_file.png" alt="localdns_file" width = "65%"/>

### threads.py
`worker` 类中包含的对象比较多，下面列表说明各自的作用及内部逻辑。

| 名称                                   | 用途及简要实现方法                                                                                                                                                                                                                                                              |
| :------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| queue                                  | 消息队列，Python Queue 模块所提供同步的、线程安全的队列类实例                                                                                                                                                                                                                   |
| ID_to_addr                             | 字典，建立 DNS 报文首部 ID 记录与发送该报文的地址及处理该报文起始时间（便于输出解析 DNS 所花费时间）之间的映射                                                                                                                                                                  |
| dict_lock                              | `threading.Lock` 实例，保证对 `ID_to_addr` 的读写线程安全                                                                                                                                                                                                                       |
| print_lock                             | `threading.Lock` 实例，保证 `print()` 线程安全                                                                                                                                                                                                                                  |
| max_buffer_size                        | queue 最大大小                                                                                                                                                                                                                                                                  |
| log_level                              | 日志级别                                                                                                                                                                                                                                                                        |
| th_print(message)                      | 对 `print()` 函数进行包装，保证线程安全                                                                                                                                                                                                                                         |
| producer(request, addr, server_socket) | 接受一个 DNS 请求 `request`，客户端地址 `addr` 及服务端套接字 `server_socket`。先尝试利用 localdns.py 中的 `localdns` 实例在本地解析该 DNS 请求，如果可以解析，则用服务端套接字向客户端返回响应报文，如果无法解析，则向字典 `ID_to_addr` 添加相应信息并向消息队列中插入该请求 |
| consumer(post_socket)                  | 接受一个传输套接字 `post_socket`。内部无限循环，每次从消息队列中获取一个报文，获取报文后向远程 DNS 服务器发送该 DNS 请求                                                                                                                                                        |
| receiver(post_socket, server_socket)   | 接受一个传输套接字 `post_socket` 和一个服务端套接字 `server_socket`。内部无限循环，尝试从远程 DNS 服务器获取之前所发的某个 DNS 请求的响应报文，在获取到响应报文后根据响应报文 ID 字段在 `ID_to_addr` 中获得应返回的客户端地址，再用服务端套接字向客户端返回相应响应报文       |


<img src="http://home.ustc.edu.cn/~cfshi/ftp/picture_bed/dnsrelay/threads_file.png" alt="threads_file" width = "65%"/>

### server.py

在 `main()` 函数中创建了一个在 "localhost" 53 号端口上的服务端套接字和数个传输套接字，并用多个传输套接字分别对应创建了多个 `threadings.consumer(post_socket)` 和 `threadings.receiver(post_socket, server_socket)` 线程。再进入无限循环，尝试从服务器套接字取得 DNS 请求，一旦获得一个 DNS 请求就立即创建一个 `threadings.producer(request, addr, server_socket)` 线程以处理该请求。

## DNS 请求及响应报文的处理方式
---

### DNS 请求报文处理
1. 当 main.py 中的 `post_socket` 接收到一个 DNS 请求报文后，创建一个新的线程运行 `worker.producer(request, addr, server_socket)`；
2. 在该函数中先利用 `localdns.nslookup(request)` 尝试本地解析。如果解析成功，则直接用 `server_socket` 向客户端返回响应报文，否则调用 `worker.queue.put(request)` 将请求加入消息队列同时在 `worker.ID_to_addr` 中建立相应映射，等待后续发送至远程 DNS 服务器进行解析；
3. main.py 中创建的线程在 `worker.consumer(post_socket)` 被 `worker.queue.get()` 阻塞，当获取到一个请求时，线程被唤醒，利用 `post_socket` 向远程 DNS 服务器请求解析刚刚获取到的请求；
4. main.py 中创建的线程另一些线程不停在 `worker.receiver(post_socket, server_socket)` 中从远程 DNS 服务器获取响应报文，一旦获取响应报文，根据 `worker.ID_to_addr` 可以获取发送该 DNS 请求的客户端地址，再用 `server_socket` 向客户端传回获取的 DNS 响应报文，就完成了中继功能。

### DNS 响应报文处理
DNS 响应报文有两种获取方式：

1. 若 DNS 请求能在本地完成拦截/解析功能，则需要根据得到的 IP 地址及 DNS 报文规范生成相应的响应报文，具体方法如下
   - 记 DNS 请求报文为 request ，用数组的方式索引 request 的每一个字节，如 request[1] 表示 request 报文的第二个字节；
   - 先将 QR 字段设为 1,即 `response[2] |= 0x80`；
   - 如果获得 IP 地址为 "0.0.0.0"，即要实现拦截，则将报文 QRCODE 设置为 3，这时就构建好了响应报文；
   - 如 IP 地址有意义，则实现本地解析功能，根据 RFC1035 标准，将 RNAME,RTYPE 等字段设置好后就构建好了响应报文；
2. 本地无法解析时，则将请求报文发往远程 DNS 服务器进行解析，远程 DNS 服务器解析完毕后会返回 DNS 响应报文，可以直接将此响应报文传回客户端。

## 程序运行结果
---
### 拦截
![intercept](http://home.ustc.edu.cn/~cfshi/ftp/picture_bed/dnsrelay/intercept.png)
![zhihu](http://home.ustc.edu.cn/~cfshi/ftp/picture_bed/dnsrelay/zhihu.png)

### 本地解析
![resolve](http://home.ustc.edu.cn/~cfshi/ftp/picture_bed/dnsrelay/resolve.png)
![baidu](http://home.ustc.edu.cn/~cfshi/ftp/picture_bed/dnsrelay/baidu.png)

### 中继
<img src="http://home.ustc.edu.cn/~cfshi/ftp/picture_bed/dnsrelay/relay.png" alt="relay" width = "95%"/>

### 服务端运行结果
<img src="http://home.ustc.edu.cn/~cfshi/ftp/picture_bed/dnsrelay/cmd.png" alt="cmd" width = "95%"/>

## 其他
---
绘图使用 [Sourcetrail](https://github.com/CoatiSoftware/Sourcetrail) 工具。