import socket
import time
import os

attack_string_dir = '/home/cpuserver/AttackingString/cve_alltools_40k_random_timeout600_partial/Results'
# 如果attack_string_dir末尾有/，则去掉
if attack_string_dir.endswith('/'):
    attack_string_dir = attack_string_dir[:-1]

# 监控的文件路径
file_path = '/home/cpuserver/testlog/attacker.log'
# 文件中需要出现的特定内容
trigger_content = '==========End'
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

def a_round_exp(tool, folder_num, client_socket):
    print(f"开始实验: {tool} {folder_num}")
    # 发送启动信号到客户端
    start_signal = "START"
    print(f"发送启动信号到客户端: {start_signal}")
    client_socket.send(start_signal.encode())

    # 等待完毕信号
    while True:
        data = client_socket.recv(1024).decode()
        if data == "COMPLETED":
            print("收到客户端backend启动完毕信号")
            break
        else:
            print(f"等待backend启动完毕信号，当前收到: {data}")
            time.sleep(1)

    
    # 启动backend
    print("启动backend，开始实验")
    os.system("bash backends.sh")

    monitor_file_for_content(file_path, trigger_content)

    # 关闭backend
    print("实验结束，停止试验")
    os.system("bash /home/cpuserver/end-regexnet.sh")

    # 通知客户端实验结束
    print("实验结束，通知客户端")
    client_socket.send("END".encode())

    # 等待客户端关闭
    print("等待客户端关闭")
    while True:
        data = client_socket.recv(1024).decode()
        if data == "END_FINISHED":
            print("客户端已关闭")
            break
        else:
            print(f"等待客户端关闭，当前收到: {data}")
            time.sleep(1)

    # 将/home/cpuserver/testlog移动到/home/cpuserver/logs/testlog_[timestamp]
    timestamp = time.strftime("%Y%m%d_%H%M%S", time.localtime())
    os.system(f"mv /home/cpuserver/testlog /home/cpuserver/logs/{tool}/{folder_num}_{timestamp}")

def start_server(host='192.168.31.38', port=12345):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(1)
    print(f"服务端已启动，等待客户端连接...")

    # 等待客户端连接
    client_socket, client_address = server_socket.accept()
    print(f"客户端连接: {client_address}")

    try:
        # while True:
        #     a_round_exp(client_socket)
        #     time.sleep(4)

        # 逐行读取/home/cpuserver/Benchmarks/cve.txt中的文件内容，将每行内容作为regex，保存到regex_list
        with open('/home/cpuserver/Benchmarks/cve.txt', 'r') as file:
            regex_list = file.readlines()
            
        tool_list = os.listdir(attack_string_dir)
        for tool in tool_list:
            if tool != 'redoshunter':
                continue

            # 判断/home/cpuserver/logs/tool目录是否存在，不存在则创建
            if not os.path.exists(f'/home/cpuserver/logs/{tool}'):
                os.system(f"mkdir /home/cpuserver/logs/{tool}")
            # 读取/home/cpuserver/AttackingString/cve_alltools_40k_random_timeout600_partial/Results/DetectAmbiguity目录下所有以数字命名的文件夹
            folder_list = os.listdir(f'{attack_string_dir}/{tool}')
            
            if tool == 'DetectAmbiguity':
                for folder in folder_list:
                    # 获取文件夹的数字
                    folder_num = int(folder)
                    # 根据数字获取regex_list中的regex
                    regex = regex_list[folder_num-1]
                    # 将regex写入/home/cpuserver/RegexNet/regex.txt
                    with open('/home/cpuserver/RegexNet/regex.txt', 'w') as file:
                        file.write(regex)
                    # 将每个文件夹下的所有txt文件复制到/home/cpuserver/RegexNet/attack_tmp目录下
                    os.system("rm -rf /home/cpuserver/RegexNet/attack_tmp/*")
                    os.system(f"cp {attack_string_dir}/{tool}/{folder}/*.txt /home/cpuserver/RegexNet/attack_tmp/")
                    
                    a_round_exp(tool, folder_num, client_socket)
                    time.sleep(4)
            else:
                txt_list = os.listdir(f'{attack_string_dir}/{tool}')
                for txt in txt_list:
                    txt_num = int(txt.split('.')[0])
                    regex = regex_list[txt_num-1]
                    # 将regex写入/home/cpuserver/RegexNet/regex.txt
                    with open('/home/cpuserver/RegexNet/regex.txt', 'w') as file:
                        file.write(regex)
                    # 将txt文件复制到/home/cpuserver/RegexNet/attack_tmp目录下
                    os.system("rm -rf /home/cpuserver/RegexNet/attack_tmp/*")
                    os.system(f"cp {attack_string_dir}/{tool}/{txt} /home/cpuserver/RegexNet/attack_tmp/")
                    a_round_exp(tool, txt_num, client_socket)
                    time.sleep(4)
        
    finally:
        client_socket.close()
        server_socket.close()

if __name__ == "__main__":
    os.system("bash /home/cpuserver/end-regexnet.sh")
    time.sleep(2)

    timestamp = time.strftime("%Y%m%d_%H%M%S", time.localtime())
    os.system(f"mv /home/cpuserver/logs /home/cpuserver/logs_bak/logs_{timestamp}")
    os.system(f"mkdir /home/cpuserver/logs")
    start_server()
