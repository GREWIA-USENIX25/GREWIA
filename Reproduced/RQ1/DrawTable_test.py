import sqlite3
import os
import shutil
import tqdm
import re
import numpy as np
import matplotlib.pyplot as plt


# 读取OutputE/Output文件夹下的所有文件夹
engines = os.listdir("output/time")

# 创建字典
result_dict = {}

# 遍历每个引擎文件夹
# for engine in engines:
for engine in engines:
    # 遍历从0到736536的所有id
    # for id in range(0, 736537):
    # print("Result of " + engine + ":")
    Engine_Result = os.listdir("output/time/"+engine)
    result_dict[engine] = {}
    for EngineT in Engine_Result:
        result_dict[engine][EngineT] = 0
        # 判断是否存在该id的文件夹
        # 读取文件内容
        Text_Result = os.listdir("output/time/" +engine + "/" + EngineT)
        # RedosN = 0
        for id in Text_Result:
            with open("output/time/" + engine + "/" + EngineT + "/" + id, "r") as f:
                # 以"\n"分割，找到格式为r'\d+\.\d+n\d+\.\d+n\d+\.\d+n\d+n\d+'的行
                cc = f.read()
                if cc == '':
                    continue
                time = re.findall(r'(\d+\.\d+)user (\d+\.\d+)system \d+:\d+\.\d+elapsed ', cc)
                # 如果匹配不成功，打印文件名和内容
                # print(time)
                if time == []:
                    print("Error: " + engine + "/" + EngineT + "/" + id)
                    print(cc)
                    # 抛出异常
                    # raise Exception("Error: " + engine + "/" + EngineT + "/" + id)
                    continue
                time = time[0]
                usertime = float(time[0])
                systemtime = float(time[1])
                # realtime = float(time.split("n")[2])
                if usertime >= 1:
                    # RedosN = RedosN + 1
                    result_dict[engine][EngineT] = result_dict[engine][EngineT] + 1
                # 插入数据库
        # print(EngineT + ": " + str(RedosN), end = ' ')
    # print()    

print(result_dict)

data = [
    ['Java', 'JavaScript', 'Perl', 'php', 'Python', 'Boost', 'C#B'],
    ['GREWIA_INC', result_dict['GREWIA_INC']['java_match'], result_dict['GREWIA_INC']['js_match'], result_dict['GREWIA_INC']['perl_match'], result_dict['GREWIA_INC']['php_match'], result_dict['GREWIA_INC']['python_match'], result_dict['GREWIA_INC']['boost_match'], result_dict['GREWIA_INC']['csharp_backtracking_match']],
    ['GREWIA_DEC', result_dict['GREWIA_DEC']['java_match'], result_dict['GREWIA_DEC']['js_match'], result_dict['GREWIA_DEC']['perl_match'], result_dict['GREWIA_DEC']['php_match'], result_dict['GREWIA_DEC']['python_match'], result_dict['GREWIA_DEC']['boost_match'], result_dict['GREWIA_DEC']['csharp_backtracking_match']],
    ['RegexStatic', result_dict['regexstatic']['java_match'], result_dict['regexstatic']['js_match'], result_dict['regexstatic']['perl_match'], result_dict['regexstatic']['php_match'], result_dict['regexstatic']['python_match'], result_dict['regexstatic']['boost_match'], result_dict['regexstatic']['csharp_backtracking_match']],
    ['Regexploit', result_dict['regexploit']['java_match'], result_dict['regexploit']['js_match'], result_dict['regexploit']['perl_match'], result_dict['regexploit']['php_match'], result_dict['regexploit']['python_match'], result_dict['regexploit']['boost_match'], result_dict['regexploit']['csharp_backtracking_match']],
    ['ReScue', result_dict['rescue']['java_match'], result_dict['rescue']['js_match'], result_dict['rescue']['perl_match'], result_dict['rescue']['php_match'], result_dict['rescue']['python_match'], result_dict['rescue']['boost_match'], result_dict['rescue']['csharp_backtracking_match']],
    ['Regulator', result_dict['regulator']['java_match'], result_dict['regulator']['js_match'], result_dict['regulator']['perl_match'], result_dict['regulator']['php_match'], result_dict['regulator']['python_match'], result_dict['regulator']['boost_match'], result_dict['regulator']['csharp_backtracking_match']],
    ['ReDoSHunter', result_dict['redoshunter']['java_match'], result_dict['redoshunter']['js_match'], result_dict['redoshunter']['perl_match'], result_dict['redoshunter']['php_match'], result_dict['redoshunter']['python_match'], result_dict['redoshunter']['boost_match'], result_dict['redoshunter']['csharp_backtracking_match']],
    ['Rengar', result_dict['Rengar']['java_match'], result_dict['Rengar']['js_match'], result_dict['Rengar']['perl_match'], result_dict['Rengar']['php_match'], result_dict['Rengar']['python_match'], result_dict['Rengar']['boost_match'], result_dict['Rengar']['csharp_backtracking_match']],
]

# 修改数据
for row in data[1:]:  # 跳过标题行
    for i in range(1, len(row)):  # 遍历每个匹配数值
        original_value = int(row[i])
        # 计算值除以 356251 的四舍五入结果
        calculated_value = round(original_value / 36251 * 100)
        # 创建新的字符串
        row[i] = f"{original_value}-{calculated_value}%"

# 提取列标题和行标题
column_headers = data.pop(0)
row_headers = [x.pop(0) for x in data]

# 格式化数据
cell_text = []
for row in data:
    # cell_text.append([f'{x/1000:1.1f}' for x in row])
    cell_text.append([f'{x}' for x in row])

# 创建图表
fig, ax = plt.subplots()
ax.axis('tight')
ax.axis('off')
table = ax.table(cellText=cell_text, rowLabels=row_headers, colLabels=column_headers, loc='center')

# 保存为图片
plt.savefig('TablesAndGraphs/table5or7.pdf', bbox_inches='tight', dpi=550)
# plt.savefig('table_5.pdf')
plt.show()