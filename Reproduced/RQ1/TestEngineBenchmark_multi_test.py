import re
import os
import subprocess
import signal
import functools
from concurrent import futures
import time
import subprocess
import shutil
import sqlite3
import threading
from timeit import default_timer as timer
from concurrent.futures import ThreadPoolExecutor,as_completed
from tqdm import tqdm
import base64
import sys

base_path = "/Evaluation/"
AttackStringPath = "/home/hhuang/Engine_Test_out/" + "AttackString/"
AttackStringPath = base_path + "Results/"
OutputPath = base_path + "output/time/"

total_begin = 0
total_end = 736536

thread_num = int(os.cpu_count() * 0.8)


Backtracking_match_command = {
    'boost_match' : '/usr/bin/time timeout 2s cpp/bin/benchmark-boost ',
    'python_match' : '/usr/bin/time timeout 2s python3 python/benchmark.py ',
    'java_match' : 'cd java && /usr/bin/time timeout 2s  java Benchmark ',
    'php_match' : '/usr/bin/time timeout 2s php php/benchmark.php ',
    'perl_match' : '/usr/bin/time timeout 2s perl perl/benchmark.pl ',
    'csharp_backtracking_match' : '/usr/bin/time timeout 2s /Evaluation/dotnet7/dotnet csharp/bin/Release/net7.0/benchmark.dll ',
    'js_match' : '/usr/bin/time timeout 2s node JavaScript/benchmark.js ',
}
match_command = {}
match_command = {k: v for d in [Backtracking_match_command] for k, v in d.items()}


# 获取AttackStringPaths下的所有以"_AttackString"结尾的文件夹
generators = []
for dir in os.listdir(AttackStringPath):
    # if dir.endswith(""):
    # if dir.endswith("_AttackString") and "EvilTextGen_" in dir:
    generators.append(dir)
# 创建输出文件夹
if os.path.exists(OutputPath) == False:
    os.makedirs(OutputPath, exist_ok=True)
# 为每个引擎创建一个输出文件夹
OutputPaths = {}
for generator in generators:
    OutputPaths[generator] = OutputPath + generator + "/"
    if os.path.exists(OutputPaths[generator]) == False:
        os.mkdir(OutputPaths[generator])
    for command in match_command.keys():
        if os.path.exists(OutputPaths[generator] + command) == False:
            os.mkdir(OutputPaths[generator] + command)

pbar = tqdm(total=(total_end - total_begin + 1), desc="real process", position=0)

def verify(line, _OutputPath, _AttackStringPath):
    # 遍历引擎/运行命令
    for command in match_command.keys():
        OutputFilename = _OutputPath + command+ "/" + str(line[0]) + ".txt"
        # 如果已经存在该输出文件，则跳过
        if os.path.exists(OutputFilename):
            continue

        new = _AttackStringPath + "%s.txt" % line[0]

        try:
            start_time = timer()

            if command == "awk_match":
                Command = match_command[command] + ("\"/%s/\" \"%s\"" % (line[1], new))
            else:
                Command = match_command[command] + ("\"%s\" \"%s\"" % (line[1], new))
                # #print(Command)
            # tqdm.write("Command:"+Command)
            completed_process = subprocess.Popen(Command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # 获取输出
            stdout, stderr = completed_process.communicate(timeout=60)
            # tqdm.write("stdout:"+stdout.decode('utf-8'))
            # tqdm.write("stderr:"+stderr.decode('utf-8'))
            # 等待进程结束，并且杀死
            completed_process.wait()
            completed_process.terminate()
            elapsed_time = timer() - start_time
            if (elapsed_time * 1e3) > 9800 and ("user" in stderr.decode('utf-8')):
                # tqdm.write(OutputFilename)
                with open(OutputFilename, 'w') as f:
                    f.write(("%s:%s\n") % (line[0], elapsed_time * 1e3))
                    # 写入stdout
                    f.write(stderr.decode('utf-8'))
        except subprocess.TimeoutExpired:
            # 超时了，终止子进程
            completed_process.kill()
            completed_process.wait()
            # tqdm.write(OutputFilename)
            with open(OutputFilename, 'w') as f:
                f.write(("%s:%s\n") % (line[0], elapsed_time * 1e3))
                # 写入stdout
                f.write(stderr.decode('utf-8'))

def verify_DA(line, _OutputPath, _AttackStringPath):
    # 遍历引擎/运行命令
    for command in match_command.keys():
        OutputFilename = _OutputPath + command+ "/" + str(line[0]) + ".txt"
        # 如果已经存在该输出文件，则跳过
        if os.path.exists(OutputFilename):
            continue

        # 在_AttackStringPath + "%s" % line[0] + "/"目录下新建文件夹real
        if os.path.exists(_AttackStringPath + "%s" % line[0] + "/real") == False:
            os.mkdir(_AttackStringPath + "%s" % line[0] + "/real")

        slwoest_elapsed_time = -1
        slowest_time = -1
        slowest_output = 0
        count = 0
        # 对_AttackStringPath + "%s" % line[0] 文件夹下所有txt文件进行遍历
        for file in os.listdir(_AttackStringPath + "%s" % line[0]):
            count += 1
            if (slowest_time * 1e3) > 10000:
                break
            new_ = _AttackStringPath + "%s" % line[0] + "/" + file
            try:
                start_time = timer()

                if command == "awk_match":
                    Command = match_command[command] + ("\"/%s/\" \"%s\"" % (line[1], new_))
                else:
                    Command = match_command[command] + ("\"%s\" \"%s\"" % (line[1], new_))
                    # #print(Command)
                # tqdm.write("Command:"+Command)
                completed_process = subprocess.Popen(Command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                # 获取输出
                stdout, stderr = completed_process.communicate(timeout=60)
                # tqdm.write("stdout:"+stdout.decode('utf-8'))
                # tqdm.write("stderr:"+stderr.decode('utf-8'))
                # 等待进程结束，并且杀死
                completed_process.wait()
                completed_process.terminate()
                elapsed_time = timer() - start_time
                # if (elapsed_time * 1e3) > 800 and ("user" in stderr.decode('utf-8')):
                #     # with open(OutputFilename, 'w') as f:
                #     #     f.write(("%s:%s\n") % (line[0], elapsed_time * 1e3))
                #     #     # 写入stdout
                #     #     f.write(stderr.decode('utf-8'))
                #     time = re.findall(r'(\d+\.\d+)user (\d+\.\d+)system \d+:\d+\.\d+elapsed ', stderr.decode('utf-8'))[0]
                #     usertime = float(time[0])
                #     if usertime > slowest_time:
                #         slowest_time = usertime
                #         slowest_output = stderr.decode('utf-8')
                #     # tqdm.write(OutputFilename+" count:"+str(count)+" slowest_time:"+str(slowest_time))
                #     # tqdm.write("elapsed_time:"+str(elapsed_time))
                if ("user" in stderr.decode('utf-8')):
                    time = re.findall(r'(\d+\.\d+)user (\d+\.\d+)system \d+:\d+\.\d+elapsed ', stderr.decode('utf-8'))[0]
                    usertime = float(time[0])
                    if usertime > slowest_time:
                        slowest_time = usertime
                        slowest_output = stderr.decode('utf-8')
                    if elapsed_time > slwoest_elapsed_time:
                        slowest_elapsed_time = elapsed_time
            except subprocess.TimeoutExpired:
                # 超时了，终止子进程
                completed_process.kill()
                completed_process.wait()
                tqdm.write(OutputFilename+" subprocess.TimeoutExpired")
                # with open(OutputFilename, 'w') as f:
                #     f.write(("%s:%s\n") % (line[0], elapsed_time * 1e3))
                #     # 写入stdout
                #     f.write(stderr.decode('utf-8'))
                slowest_time = 2.0
                slowest_output = f"{2.0}user 0.0system 0:00.00elapsed 100%CPU (0avgtext+0avgdata 0maxresident)k\n0inputs+0outputs (0major+0minor)pagefaults 0swaps"
        
        if (slowest_elapsed_time * 1e3) > 9800:
            with open(OutputFilename, 'w') as f:
                f.write(("%s:%s\n") % (line[0], slowest_elapsed_time * 1e3))
                # 写入stdout
                f.write(slowest_output)

    # 删除_AttackStringPath + "%s" % line[0] + "/real"文件夹
    shutil.rmtree(_AttackStringPath + "%s" % line[0] + "/real")

def verify_DA_base64(line, _OutputPath, _AttackStringPath):
    # 遍历引擎/运行命令
    for command in match_command.keys():
        OutputFilename = _OutputPath + command+ "/" + str(line[0]) + ".txt"
        # 如果已经存在该输出文件，则跳过
        if os.path.exists(OutputFilename):
            continue

        # 在_AttackStringPath + "%s" % line[0] + "/"目录下新建文件夹real
        if os.path.exists(_AttackStringPath + "%s" % line[0] + "/real") == False:
            os.mkdir(_AttackStringPath + "%s" % line[0] + "/real")

        slwoest_elapsed_time = 0
        slowest_time = 0
        slowest_output = 0
        count = 0
        # 对_AttackStringPath + "%s" % line[0] 文件夹下所有txt文件进行遍历
        for file in os.listdir(_AttackStringPath + "%s" % line[0]):
            count += 1
            if (slowest_time * 1e3) > 1000:
                break
            new = _AttackStringPath + "%s" % line[0] + "/" + file
            new_ = _AttackStringPath + "%s" % line[0] + "/real/" + file
            # 读取文件内容，内容分别是三行base64编码的字符串，将其解码后拼接成一个字符串
            with open(new, 'r', encoding='utf-8') as f:
                # 读取第一行，如果不为空则解码
                prefix = f.readline().strip()
                if prefix != '':
                    prefix = base64.b64decode(prefix)
                # 读取第二行，如果不为空则解码
                infix = f.readline().strip()
                if infix != '':
                    infix = base64.b64decode(infix)
                # 读取第三行，如果不为空则解码
                suffix = f.readline().strip()
                if suffix != '':
                    suffix = base64.b64decode(suffix)
                # 拼接三行字符串，按照prefix+(infix*n)+suffix的模式拼接到100kb
                # 计算n的值
                # n = (100 * 1024 - sys.getsizeof(prefix) - sys.getsizeof(suffix)) // sys.getsizeof(infix)
                n = (100 * 1024 - len(prefix) - len(suffix)) // len(infix)
                attackstring = prefix + infix * n + suffix
                attackstring = attackstring.decode('utf-8')
                # tqdm.write("new_:"+new_+"\tsize"+str(sys.getsizeof(attackstring)/1024))
                # 将拼接后的字符串写入文件new_
                with open(new_, 'w', encoding='utf-8') as f:
                    f.write(attackstring)
            try:
                start_time = timer()

                if command == "awk_match":
                    Command = match_command[command] + ("\"/%s/\" \"%s\"" % (line[1], new_))
                else:
                    Command = match_command[command] + ("\"%s\" \"%s\"" % (line[1], new_))
                    # #print(Command)
                # tqdm.write("Command:"+Command)
                completed_process = subprocess.Popen(Command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                # 获取输出
                stdout, stderr = completed_process.communicate(timeout=60)
                # tqdm.write("stdout:"+stdout.decode('utf-8'))
                # tqdm.write("stderr:"+stderr.decode('utf-8'))
                # 等待进程结束，并且杀死
                completed_process.wait()
                completed_process.terminate()
                elapsed_time = timer() - start_time
                # if (elapsed_time * 1e3) > 800 and ("user" in stderr.decode('utf-8')):
                #     # with open(OutputFilename, 'w') as f:
                #     #     f.write(("%s:%s\n") % (line[0], elapsed_time * 1e3))
                #     #     # 写入stdout
                #     #     f.write(stderr.decode('utf-8'))
                #     time = re.findall(r'(\d+\.\d+)user (\d+\.\d+)system \d+:\d+\.\d+elapsed ', stderr.decode('utf-8'))[0]
                #     usertime = float(time[0])
                #     if usertime > slowest_time:
                #         slowest_time = usertime
                #         slowest_output = stderr.decode('utf-8')
                #     # tqdm.write(OutputFilename+" count:"+str(count)+" slowest_time:"+str(slowest_time))
                #     # tqdm.write("elapsed_time:"+str(elapsed_time))
                if ("user" in stderr.decode('utf-8')):
                    time = re.findall(r'(\d+\.\d+)user (\d+\.\d+)system \d+:\d+\.\d+elapsed ', stderr.decode('utf-8'))[0]
                    usertime = float(time[0])
                    if usertime > slowest_time:
                        slowest_time = usertime
                        slowest_output = stderr.decode('utf-8')
                    if elapsed_time > slwoest_elapsed_time:
                        slowest_elapsed_time = elapsed_time
                else:
                    break
            except subprocess.TimeoutExpired:
                # 超时了，终止子进程
                completed_process.kill()
                completed_process.wait()
                tqdm.write(OutputFilename+" subprocess.TimeoutExpired")
                # with open(OutputFilename, 'w') as f:
                #     f.write(("%s:%s\n") % (line[0], elapsed_time * 1e3))
                #     # 写入stdout
                #     f.write(stderr.decode('utf-8'))
                slowest_time = 2.0
                slowest_output = f"{2.0}user 0.0system 0:00.00elapsed 100%CPU (0avgtext+0avgdata 0maxresident)k\n0inputs+0outputs (0major+0minor)pagefaults 0swaps"
        
        if (slowest_elapsed_time * 1e3) > 800:
            with open(OutputFilename, 'w') as f:
                f.write(("%s:%s\n") % (line[0], slowest_elapsed_time * 1e3))
                # 写入stdout
                f.write(slowest_output)

    # 删除_AttackStringPath + "%s" % line[0] + "/real"文件夹
    shutil.rmtree(_AttackStringPath + "%s" % line[0] + "/real")

def run(line, exist_generators):
    # 遍历所有的生成器/攻击字符串文件夹
    for generator in exist_generators:
        _AttackStringPath = os.path.join(AttackStringPath, generator + "/")

        _OutputPath = OutputPaths[generator]

        if generator == "DetectAmbiguity":
            verify_DA(line, _OutputPath, _AttackStringPath)
        else:
            verify(line, _OutputPath, _AttackStringPath)


    pbar.update(1)


if __name__ == '__main__':
    result = []

    # 文件名来自命令行第一个参数
    import sys
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        raise Exception("Please input the filename")

    with open(filename, 'r', encoding='utf-8') as f:
        count = 0
        for line in f:
            count += 1
            result.append((count, line.strip()))


    # 用所有找到的生成器，打印所有AttackString地址
    #print("AttackStringPath:")
    # for generator in generators:
    #print(os.path.join(AttackStringPath, generator + "_AttackString/"))
    # 打印所有输出文件夹地址
    #print("OutputPath:")
    # for generator in generators:
    #print(OutputPaths[generator])
    # 打印所有引擎
    #print("match_command:")
    # for engine in match_command.keys():
    #print(engine)
    # 等待用户确认
    # input("Press Enter to continue...")

    with ThreadPoolExecutor(max_workers=thread_num) as executor:
        #遍历所有正则表达式
        # for line in tqdm(result, desc="regex", position=1):
        # for line in result:
        # 倒序遍历result
        # for line in reversed(result):
        for line in result:
            # print(line)
            if line == '':
                continue
            elif line[0] < total_begin or line[0] > total_end:
                continue
            # 如果在所有AttackString文件夹下都不存在该正则表达式的AttackString，则跳过
            exist_generators = []
            for generator in generators:
                if os.path.exists(os.path.join(AttackStringPath, generator + "/") + "%s.txt" % line[0]):
                    exist_generators.append(generator)
                elif generator == 'DetectAmbiguity' and os.path.exists(os.path.join(AttackStringPath, generator + "/") + "%s" % line[0]):
                    exist_generators.append(generator)
            if len(exist_generators) == 0:
                pbar.update(1)
                continue
            executor.submit(run, line, exist_generators)
