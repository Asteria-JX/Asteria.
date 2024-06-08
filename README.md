# UDP Socket Programming

该项目主要实现基于UDP套接字的客户端-服务器通信系统。目标是使用UDP套接字模拟类似TCP的握手和数据传输过程。该项目自定义了应用层报文格式及报文交互过程，并实现了自定义应用层协议。支持数据包的发送与接收、模拟丢包、重传机制以及往返时间(RTT)的计算。

## 概述

该项目使用UDP套接字模拟TCP连接。它包括一个客户端和一个服务器，它们通过网络进行通信。客户端首先与服务器建立握手，一旦连接成功，便开始数据传输。

## 特性

- 使用UDP套接字模拟TCP握手和断开连接。
- 支持在指定的丢包率下的数据传输。
- 在超时情况下自动重传数据包。
- 传输结束后计算往返时间（RTT）和数据摘要。

## 先决条件

确保已安装Python 3和所需的库。您可以使用pip安装所需库：

```python
pip install socket statistics 
```

## 运行环境

- 操作系统：兼容所有主要操作系统，包括 Windows, macOS, 和 Linux。
- Python版本：Python 3，确保您的系统中已安装Python 3及以上版本。
- 环境依赖：安装 `requirements.txt` 文件里的库。
- 网络配置：确保客户端与服务器之间的网络畅通，无防火墙或路由器阻挡UDP端口。

## 使用说明

### 客户端

使用服务器IP和端口作为参数运行客户端脚本：

```python
python client.py <服务器IP> <服务器端口>
```

客户端将发起握手，发送数据包，并等待响应。它将为每个接收到的数据包打印RTT和服务器时间。

### 服务器端

运行服务器脚本：

```python
python server.py
```

服务器将监听传入的连接请求并响应客户端请求。它将根据指定的丢包率模拟丢包。

## 架构

### 客户端(udpclient.py)

- 使用自定义握手协议与服务器建立连接。
- 发送数据包并等待确认。
- 实现超时情况下的数据包重传机制。
- 传输结束后计算并打印RTT和摘要统计数据。

### 服务器端(udpserver.py)

- 监听客户端的握手请求并发送确认。
- 接收数据包并用自定义响应数据包响应或模拟丢包。
- 接收到客户端的断开连接请求后关闭连接。

## 报文格式

#### Client -> Server的报文格式

```bash
| Seq_no   | Ver | Type | Src_Port | Dst_Port | Time  |        content
| 2 Bytes  | 1B  | 16B  |    8B    |    8B    |  32B  |
```

#### Server -> Client的报文格式

```bash
| Seq_no   | Ver | Type | Time  |        content
| 2 Bytes  | 1B  | 16B  |  16B  |
```
