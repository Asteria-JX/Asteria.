import socket
import random
import datetime
import json

# 服务器设置
SERVER_PORT = 4216  # 服务器端口
BUFFER_SIZE = 1024  # 缓冲区大小
DROP_RATE = 0.3  # 丢包率

# 创建 UDP 套接字
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('', SERVER_PORT))

# 握手状态标志
HANDSHAKE_COMPLETE = False


def handle_client_request(data, addr):
    global HANDSHAKE_COMPLETE
    try:
        # 尝试解析JSON数据
        packet = json.loads(data.decode('utf-8'))
        if not HANDSHAKE_COMPLETE:
            # 握手阶段
            if packet.get("Type") == "Connect":
                print("Handshake initiated by client. Sending ACK...")
                response = {"Ver": 2, "Type": "Connect_ACK",
                            "Time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                server_socket.sendto(json.dumps(response).encode('utf-8'), addr)
                HANDSHAKE_COMPLETE = True
                return True
            else:
                print("Invalid handshake message received.")
                return False
        else:
            # 数据传输阶段
            if packet.get("Type") == "Disconnect":
                response = {"Ver": 2, "Type": "Disconnect_ACK",
                            "Time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                server_socket.sendto(json.dumps(response).encode('utf-8'), addr)
                HANDSHAKE_COMPLETE = False
                server_socket.close()
                print("Server socket closed.")
                return False
            elif packet.get("Ver") == 2:
                # 随机决定丢包
                print(f"Request from {addr} for sequence {packet['Seq']}")
                if random.random() > DROP_RATE:
                    # 构造响应数据包
                    server_time = datetime.datetime.now().strftime("%H:%M:%S")  # 正确使用 datetime 模块
                    response = {
                        "Seq": packet["Seq"],
                        "Ver": 2,
                        "Type": "Reply",
                        "Time": server_time
                    }
                    server_socket.sendto(json.dumps(response).encode('utf-8'), addr)
                    print(f"Response sent to {addr} for sequence {packet['Seq']}")
                else:
                    print(f"Sequence {packet['Seq']} is dropped!No response!")
            return True
    except json.JSONDecodeError:
        print("Received invalid JSON data")


print(f"UDP server if listening on Port : {SERVER_PORT}")

try:
    while True:
        # 接收客户端数据
        data, addr = server_socket.recvfrom(BUFFER_SIZE)
        if not handle_client_request(data,addr):
            break
except KeyboardInterrupt:
    print("Server is shutting down gracefully.")
# finally:
#     server_socket.close()
#     print("Server socket closed.")
