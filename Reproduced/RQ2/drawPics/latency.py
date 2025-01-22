import os
import re
import matplotlib.pyplot as plt
import math
import shutil

def calc_avg(lines):
    # 依次遍历数组，元素要么被r"(\d+)m(\d+)\.(\d+) ms"匹配，要么被r"\d+m- ms"匹配，计算其平均值
    total_ms = 0
    count = 0
    for line in lines:
        match = re.search(r"(?:(\d+)m)?(\d+)\.(\d+) ms", line)
        if match:
            minutes = match.group(1)
            minutes_ms = int(minutes) * 60 * 1000 if minutes else 0
            total_ms += minutes_ms + int(match.group(2)) * 1000 + int(match.group(3))
            count += 1
        elif re.search(r"\d+m- ms", line):
            total_ms += 500000
            count += 1
            pass
        else:
            raise Exception("Invalid line: " + line)
    return total_ms / count

def statistic(folders_path):
    success_count = 0
    for idx, folder in enumerate(os.listdir(folders_path)):
        # 读取folder下的haproxy.log文件
        with open(os.path.join(folders_path, folder, "backend.log"), "r") as f:
            lines = f.readlines()

            # 提取所有包含"GET / "的行，跳过不符合规则的行，并组成数组
            get_lines = [line for line in lines if re.search(r"GET / ", line)]
            # print(folder, len(get_lines))

            # 提取数组中前10%的元素
            get_lines_first10 = get_lines[:len(get_lines) // 10]
            # 提取数组中后10%的元素
            get_lines_last10 = get_lines[-len(get_lines) // 10:]

            # 计算前10%和后10%的平均值
            first10_avg = calc_avg(get_lines_first10)
            last10_avg = calc_avg(get_lines_last10)
            # print(folder, first10_avg, last10_avg)

            # 如果last10_avg/first10_avg < 1.5，则认为成功
            if last10_avg / first10_avg > 1.5:
                success_count += 1

    print(f"{folders_path} 成功率：{success_count} / {len(os.listdir(folders_path))} = {success_count / 78}")



statistic("DA_Inc")
statistic("DetectAmbiguity")
statistic("regexstatic")
statistic("regexploit")
statistic("rescue")
statistic("regulator")
statistic("redoshunter")
statistic("Rengar")
