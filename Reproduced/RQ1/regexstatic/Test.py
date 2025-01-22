import os
import subprocess
# 导入线程池模块
import concurrent.futures


# 读取/home/supermaxine/Documents/USENIX24/AttackStringGen/regex_set/regexes下1.txt到736535.txt
# path = '/Evaluation/regexstatic/regexes'
path = '/Evaluation/regexes'
count = 0

files = os.listdir(path)   # 读入文件夹
num = len(files)       # 统计文件夹中的文件个数

# 定义一个函数，用于执行任务
def do_task(id):
    print("-"*20, "\nsubmits task {}".format(id), "/", 736535, "\n", "-"*20)
    output = os.popen("timeout --preserve-status -k 5 600 ./run.sh --if='{}' --test-eda-exploit-string=false".format(os.path.join(path, str(id)+'.txt')))
    print("-"*20, "\ntask {} is done".format(id),"\n", output.read(), "\n", "-"*20)

with concurrent.futures.ThreadPoolExecutor(max_workers=int(os.cpu_count() * 0.8)) as executor:
    # 使用线程池执行任务
    for i in range(1, num):
        count += 1
        # if count < 187654 or count > 736535:
        #     continue
        executor.submit(do_task, i)
