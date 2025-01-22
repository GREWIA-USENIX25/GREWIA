import socket
import time
import os

# 监控的文件路径
file_path = '/home/gpuserver/testlog/data_manager.log'
# 文件中需要出现的特定内容
trigger_content = 'Sleep'

def monitor_file_for_content(file_path, trigger_content):
    print(f"开始监控文件: {file_path}")
    while True:
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                content = file.read()
                if trigger_content in content:
                    print(f"发现特定内容: {trigger_content}")
                    return True
        time.sleep(1)  # 每秒检查一次文件变化

def a_round_exp(client_socket):
    # 等待启动信号
    while True:
        data = client_socket.recv(1024).decode()
        if data == "START":
            print("收到启动信号，执行命令并开始监控文件")
            
            # 执行命令（示例：创建或更新文件）
            os.system("bash backends.sh")
            print("命令执行完毕，开始监控文件内容变化")
            
            # 监控文件直到发现特定内容
            if monitor_file_for_content(file_path, trigger_content):
                # 向服务端发送完毕信号
                client_socket.send("COMPLETED".encode())
                print("完毕信号已发送到服务端")
                break
        else:
            print(f"等待启动信号，当前收到: {data}")
            time.sleep(1)
      
    # 等待结束信号
    while True:
        data = client_socket.recv(1024).decode()
        if data == "END":
            print("收到结束信号，结束实验")
            os.system("bash /home/gpuserver/end-regexnet.sh")
            break

    # 将/home/cpuserver/testlog移动到/home/cpuserver/logs/testlog_[timestamp]
    timestamp = time.strftime("%Y%m%d_%H%M%S", time.localtime())
    os.system(f"mv /home/gpuserver/testlog /home/gpuserver/logs/testlog_{timestamp}")
    
    # 向服务端发送结束信号
    client_socket.send("END_FINISHED".encode())

def start_client(host='192.168.31.38', port=12345):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    print("已连接到服务端")
    
    while True:
        a_round_exp(client_socket)
        time.sleep(6)
    client_socket.close()

    
    # 将/home/cpuserver/testlog移动到/home/cpuserver/logs/testlog_[timestamp]
    timestamp = time.strftime("%Y%m%d_%H%M%S", time.localtime())
    os.system(f"mv /home/gpuserver/testlog /home/gpuserver/logs/testlog_{timestamp}")

if __name__ == "__main__":
    os.system("bash /home/gpuserver/end-regexnet.sh")
    time.sleep(2)

    timestamp = time.strftime("%Y%m%d_%H%M%S", time.localtime())
    os.system(f"mv /home/gpuserver/logs /home/gpuserver/logs_bak/logs_{timestamp}")
    os.system(f"mkdir /home/gpuserver/logs")
    start_client()
