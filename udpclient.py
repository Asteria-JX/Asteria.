import socket
import random
import statistics
import sys
import json
from datetime import datetime
import select
import string

# 客户端设置
SERVER_IP = sys.argv[1]  # 服务器IP
SERVER_PORT = int(sys.argv[2])  # 服务器端口
BUFFER_SIZE = 1024  # 缓冲区大小
TIMEOUT = 0.1  # 超时时间，100ms
MAX_RETRIES = 2  # 最大重传次数

addr = (SERVER_IP, SERVER_PORT)

# 创建 UDP 套接字
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# 请求和响应统计信息
total_requests = 0  # 共发出的包
received_packets = 0  # 收到的包
rtt_values = []  # 每个包的RTT
server_response_times = []  # 客户端回复时间
unreceived_packets = []  # 未收到回复
current_expected_seq_no = 0  # 当前期待的序列号



# 建立连接
def initiate_handshake():
    packet = {
        "Ver": 2,
        "Type": "Connect",
        "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    }
    packet_json = json.dumps(packet).encode('utf-8')
    client_socket.sendto(packet_json, addr)
    print(f"Sending request of connecting to {addr}...")
    try:
        data, _ = client_socket.recvfrom(BUFFER_SIZE)
        response = json.loads(data.decode('utf-8'))
        if response.get("Type") == "Connect_ACK":
            print(f"Handshake complete. Starting data transfer...\n")
        else:
            print("Handshake failed.\n")
    except (ConnectionResetError, socket.timeout) as e:
        print(f"Error during handshake: {e}")


# 关闭连接
def close_wave():
    packet = {
        "Ver": 2,
        "Type": "Disconnect",
        "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    packet_json = json.dumps(packet).encode('utf-8')
    client_socket.sendto(packet_json, addr)
    print(f"Sending disconnect request to {addr}")
    try:
        data, _ = client_socket.recvfrom(BUFFER_SIZE)
        response = json.loads(data.decode('utf-8'))
        if response.get("Type") == "Disconnect_ACK":
            print(f"wave complete. Client Socket closing...\n")
        else:
            print("wave failed.\n")
    except (ConnectionResetError, socket.timeout) as e:
        print(f"Error during wave: {e}")


# 发送数据包
def send_packet(seq_no):
    global current_expected_seq_no
    current_expected_seq_no = seq_no
    CLIENT_PORT = client_socket.getsockname()[1]
    # 随机生成信息
    random_message_from = list(string.ascii_letters + string.digits)

    packet = {
        "Seq": seq_no,
        "Ver": 2,
        "Type": "Request",
        "Src_Port": CLIENT_PORT,
        "Dst_Port": SERVER_PORT,
        "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Content": ''.join(random.sample(random_message_from, seq_no))
    }
    packet_json = json.dumps(packet).encode('utf-8')
    client_socket.sendto(packet_json, addr)
    print(
        f"Send_Sequence {seq_no}:from {CLIENT_PORT} to {SERVER_PORT}---Time: {packet['Time']}---Content: {packet['Content']}")


# 接收响应
def receive_packet(seq_no):
    global current_expected_seq_no, server_response_times
    #                读列表、写列表、异常列表、超时时间
    r = select.select([client_socket], [], [], TIMEOUT)
    if r[0]:
        data, addr = client_socket.recvfrom(BUFFER_SIZE)
        try:
            recv_data = json.loads(data.decode('utf-8'))
            # 仅处理当前期待的序列号的响应
            # print(recv_data["Seq"]," ",seq_no," ",current_expected_seq_no)
            # if recv_data["Ver"] == 2 and recv_data["Seq"] == seq_no:
            if recv_data["Ver"] == 2 and current_expected_seq_no == seq_no:
                server_response_times.append(datetime.now())
                rtt = (server_response_times[-1] - server_response_times[-2]).total_seconds() * 1000
                rtt_values.append(rtt)
                print(
                    f"Receive_Sequence {current_expected_seq_no}, {SERVER_IP}:{SERVER_PORT}, RTT: {rtt:.2f} ms, Server Time: {recv_data['Time']}\n")
                return True
        except json.JSONDecodeError:
            print("Received invalid JSON data")
    return False


# main
def main():
    global total_requests, received_packets, server_response_times, current_expected_seq_no

    initiate_handshake()
    server_response_times.append(datetime.now())  # 记录开始时间

    for seq_no in range(1, 13):
        send_packet(seq_no)
        total_requests += 1
        # 重传机制
        for i in range(MAX_RETRIES + 1):
            if receive_packet(seq_no):
                received_packets += 1
                break
            else:
                if i == MAX_RETRIES:
                    unreceived_packets.append(seq_no)
                    print(f"Sequence {seq_no}, request timeout")
                    print(f"Two retries failed, packet {seq_no} discarded\n")
                else:
                    print(f"Sequence {seq_no}, request timeout")
                    send_packet(seq_no)
                    total_requests += 1

    close_wave()

    print_summary()


# 打印汇总信息
def print_summary():
    global total_requests, received_packets, rtt_values,server_response_times
    packet_loss_rate = (1 - received_packets / total_requests) * 100
    max_rtt = max(rtt_values) if rtt_values else 0
    min_rtt = min(rtt_values) if rtt_values else 0
    avg_rtt = statistics.mean(rtt_values) if rtt_values else 0
    std_dev_rtt = statistics.stdev(rtt_values) if rtt_values else 0
    overall_response_time = (server_response_times[-1] - server_response_times[0]).total_seconds()

    print(f"\nSummary:")
    print(f"Total requests: {total_requests}")
    print(f"Received packets: {received_packets}")
    print(f"Discarded packets'No: {unreceived_packets}")
    print(f"Packet loss rate: {packet_loss_rate:.2f}%")
    print(f"Max RTT: {max_rtt:.2f} ms")  # 最大RTT
    print(f"Min RTT: {min_rtt:.2f} ms")  # 最小RTT
    print(f"Avg RTT: {avg_rtt:.2f} ms")  # 标准差
    print(f"Std Dev RTT: {std_dev_rtt:.2f} ms")
    print(f"Server overall response time: {overall_response_time:.2f} seconds")


if __name__ == '__main__':
    main()
