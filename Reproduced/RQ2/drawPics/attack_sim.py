import os
import re
import matplotlib.pyplot as plt
import math
import shutil


def statistic(folder_path):
    # 读取folder下的haproxy.log文件
    with open(os.path.join(folder_path, "haproxy.log"), "r") as f:
        lines = f.readlines()
    
    # 提取符合r"Throughput at \d+: (\d+)"的行，跳过不符合规则的行，将数字保存为数组
    throughput_numbers = [int(re.search(r"Throughput at \d+: (\d+)", line).group(1)) for line in lines if re.match(r"Throughput at \d+: (\d+)", line)]

    # Skip first two data points
    throughput_numbers = throughput_numbers[2:]
    # 统计第11-16行数据的平均值
    throughput_numbers_avg = sum(throughput_numbers[10:16]) / 6
    # 统计最后10行数据的平均值
    throughput_numbers_avg_last = sum(throughput_numbers[-10:]) / 10

    return throughput_numbers


# Set style for academic look
plt.style.use('seaborn-paper')
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman']
plt.rcParams['font.size'] = 24  # Increased from 16

# 创建一个图表
plt.figure(figsize=(10, 4), dpi=300)  # Height reduced from 6 to 4

# Color scheme suitable for academic papers
colors = ['#0072B2', '#D55E00']  # Blue and vermillion
line_styles = ['-', '--']

# 为每个文件夹绘制折线图
folders = ["GREWIA", "ReDoSHunter"]
for i, folder in enumerate(folders):
    throughput = statistic(folder)
    plt.plot(throughput, label=folder, color=colors[i], 
             linestyle=line_styles[i], linewidth=4.0)  # Increased linewidth from 1.5 to 4.0

# Add arrow with matching colors
arrow_color = '#666666'  # Neutral gray that works with both blue and vermillion
plt.arrow(15, 500, 0, -50, head_width=1, head_length=10, 
          fc=arrow_color, ec=arrow_color, width=0.5)

plt.arrow(75, 500, 0, -50, head_width=1, head_length=10, 
          fc=arrow_color, ec=arrow_color, width=0.5)

# Add horizontal line segment with matching color
plt.plot([15.05, 74.95], [500, 500], color=arrow_color, linestyle='-', linewidth=5)

# Add text above the line segment
plt.text(45, 510, "Sending malicious requests", ha='center', va='bottom', color=arrow_color, fontsize=24)

# 添加图例
plt.legend(frameon=True, fancybox=False, edgecolor='black', 
          fontsize=18, loc='right', bbox_to_anchor=(1.0, 0.35))  # Reduced from 22
plt.xlabel("Time (s)", fontsize=16, labelpad=10, weight='bold')  # Reduced from 20
plt.ylabel("Throughput (req/s)", fontsize=16, labelpad=10, weight='bold')  # Reduced from 20

# 设置Y轴范围
plt.ylim(-10, 600)

# 设置网格
plt.grid(True, linestyle='--', alpha=0.7)

# 设置坐标轴刻度字体大小
plt.xticks(fontsize=20)
plt.yticks(fontsize=20)

# 调整布局
plt.tight_layout()

# 保存图表
# plt.savefig("throughput_comparison.png", bbox_inches='tight')
# 保存为pdf
plt.savefig("attack_simulation.pdf", bbox_inches='tight')
plt.close()