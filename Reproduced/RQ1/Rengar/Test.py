import os
import subprocess
import time
import base64
# 导入线程池模块
import concurrent.futures

# 创建AttackString文件夹
if not os.path.exists('AttackString'):
    os.makedirs('AttackString')

# 读取/home/supermaxine/Documents/USENIX24/AttackStringGen/regex_set/regexes下1.txt到736535.txt
path = '/Evaluation/regexes'
count = 0

files = os.listdir(path)   # 读入文件夹
num = len(files)       # 统计文件夹中的文件个数

# 定义一个函数，用于执行任务
def do_task(id):
    start_time = time.time()
    # 读取/Evaluation/regexes/{id}.txt文件内容
    with open(f"/Evaluation/regexes/{id}.txt", "r") as f:
        content = f.read()
    content = content.strip()
    content_b64 = base64.b64encode(content.encode()).decode()
    try:
        process = subprocess.run([
            "timeout", "600s", 
            "/usr/lib/jvm/java-17-openjdk-amd64/bin/java", '--enable-preview',
            '-jar', 'Rengar.jar',
            '-s', f"{content_b64}",
            '-id', f"{id}"
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        print(f"Task {id} failed with error: {e}")
    end_time = time.time()
    print(f"Task {id} completed in {end_time - start_time:.2f} seconds")

with concurrent.futures.ThreadPoolExecutor(max_workers=int(os.cpu_count() * 0.8)) as executor:
    # 使用线程池执行任务
    # 编译文件
    for i in range(1, num):
        count += 1
        # if count <= 0 or count > 100:
        #     continue
        executor.submit(do_task, i)