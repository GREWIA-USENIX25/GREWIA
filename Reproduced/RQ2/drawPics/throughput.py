import os
import re
import matplotlib.pyplot as plt
import math
import shutil

success_list = {}

# folders_path = "redoshunter"
# folders_path = "DetectAmbiguity"

def statistic(folders_path):

    success_count = 0
    total_count = 0


    # 获取文件夹数量
    folder_count = len(os.listdir(folders_path))
    # 计算需要的行数和列数，每行10张图
    cols = 10
    rows = math.ceil(folder_count / cols)

    # 创建子图网格
    fig, axes = plt.subplots(rows, cols, figsize=(20, 4*rows))
    axes = axes.ravel()  # 将二维数组展平为一维

    for idx, folder in enumerate(os.listdir(folders_path)):
        # 读取folder下的haproxy.log文件
        with open(os.path.join(folders_path, folder, "haproxy.log"), "r") as f:
            lines = f.readlines()
        
        # 提取符合r"Throughput at \d+: (\d+)"的行，跳过不符合规则的行，将数字保存为数组
        throughput_numbers = [int(re.search(r"Throughput at \d+: (\d+)", line).group(1)) for line in lines if re.match(r"Throughput at \d+: (\d+)", line)]

        # 统计第11-16行数据的平均值
        throughput_numbers_avg = sum(throughput_numbers[10:16]) / 6
        # print(folder, throughput_numbers_avg)
        # 统计最后10行数据的平均值
        throughput_numbers_avg_last = sum(throughput_numbers[-10:]) / 10
        # print(folder, throughput_numbers_avg_last)

        total_count += 1
        # 如果throughput_numbers_avg_last/throughput_numbers_avg < 0.5，则认为成功
        if throughput_numbers_avg_last / throughput_numbers_avg < 0.5:
            success_count += 1
            # success_list.add(folder.split("_")[0])
            success_list[folder.split("_")[0]] = folder
            axes[idx].set_facecolor('#e6ffe6')  # Light green color

        # 在对应的子图位置绘制折线图
        axes[idx].plot(throughput_numbers)
        # axes[idx].set_title(folder)
        # 隐藏坐标轴
        axes[idx].set_xticks([])
        axes[idx].set_yticks([])
        
        # 在右上角添加folder.split("_")[0]的标注
        axes[idx].text(0.95, 0.95, folder.split("_")[0], 
                      transform=axes[idx].transAxes,
                      fontsize=6,
                      horizontalalignment='right',
                      verticalalignment='top')

    # 隐藏多余的子图
    for idx in range(folder_count, rows * cols):
        axes[idx].set_visible(False)

    
    # # 将success_list的key转化为int从小到大排序并逐行打印success_list
    # for folder in sorted(success_list.keys(), key=lambda x: int(x), reverse=False):
    #     print(folder)   

    print(f"{folders_path} 成功率：{success_count} / {total_count} = {success_count / total_count}")

    # plt.tight_layout()
    # plt.show()

    # 设置图片大小
    plt.gcf().set_size_inches(40, 1*rows)
    # 将图片保存到当前文件夹下
    plt.savefig(f"{folders_path}.png")




statistic("DA_Inc")
statistic("DetectAmbiguity")
statistic("regexstatic")
statistic("regexploit")
statistic("rescue")
statistic("regulator")
statistic("redoshunter")
statistic("Rengar")