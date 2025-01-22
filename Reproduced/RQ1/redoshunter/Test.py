import os
import subprocess
import concurrent.futures
from tqdm import tqdm


# 创建文件夹regexes
if not os.path.exists('AttackString'):
    os.makedirs('AttackString')

# 读取/home/supermaxine/Documents/USENIX24/AttackStringGen/regex_set/regexes下1.txt到736535.txt
# path = '/Evaluation/redoshunter/regexes'
path = '/Evaluation/regexes'
count = 0
files = os.listdir(path)   # 读入文件夹
num = len(files)       # 统计文件夹中的文件个数

begin = 1
end = num

pbar = tqdm(total=(end-begin))

# 定义一个函数，用于执行任务
# def do_task(id):
#     # print("-"*20, "\nsubmits task {}".format(id), "/", 736535, "\n", "-"*20)
#     # output = os.popen("timeout --preserve-status -k 5 10 python3 main.py {}".format(os.path.join(path, str(id)+'.txt')))
#     output = os.popen("timeout 300 java -jar ReDoSHunter.jar {} {} {}".format(path, str(id)+'.txt', 'AttackString'))
#     # print("-"*20, "\ntask {} is done".format(id),"\n", output.read(), "\n", "-"*20)
#     pbar.update(1)

def do_task(id):
    cmd = f"timeout 600 java -jar ReDoSHunter.jar {path} {str(id)}.txt AttackString"
    try:
        subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=310, check=True)
    except subprocess.TimeoutExpired:
        print(f"Task {id} timeout.")
    except subprocess.CalledProcessError as e:
        print(f"Error in task {id}: {e}")
    finally:
        pbar.update(1)

with concurrent.futures.ThreadPoolExecutor(max_workers=int(os.cpu_count() * 0.8)) as executor:
    # 使用线程池执行任务
    for i in range(begin, end):
        executor.submit(do_task, i)