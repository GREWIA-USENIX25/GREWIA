import os
import shutil
import sqlite3
from concurrent.futures import ThreadPoolExecutor
import subprocess

# 连接数据库
conn = sqlite3.connect('regexlib.db')
cursor = conn.cursor()
# 查找regexes表中的id和regex_base64字段
cursor.execute('SELECT id, regex_base64 FROM regexes')
rows = cursor.fetchall()


# 创建一个文件夹rengar_out，用于存放临时文件
if os.path.exists('rengar_out'):
    shutil.rmtree('rengar_out')
os.mkdir('rengar_out')


def run(row):
    # 解码regex_base64字段
    regex_id, regex_base64 = row
    # 使用subprocess调用Java程序
    with subprocess.Popen(['java', '--enable-preview', '-jar', 'Rengar.jar', '-s', regex_base64], stdout=subprocess.PIPE, text=True) as proc:
        out = proc.stdout.read()
    # 将结果写入文件
    with open(f'rengar_out/{regex_id}.txt', 'w', encoding='utf-8') as f:
        f.write(out)

executor = ThreadPoolExecutor(max_workers=250)
for row in rows:
    executor.submit(run, row)

executor.shutdown()

# 如果数据库中已经存在rengar_results表，则删除
cursor.execute('DROP TABLE IF EXISTS rengar_results')
# 在数据库中创建新表rengar_results，包含id、vulnerable、output三个字段
cursor.execute('CREATE TABLE IF NOT EXISTS rengar_results (id INTEGER PRIMARY KEY, vulnerable INTEGER, output TEXT)')

# 读取rengar_out文件夹中的所有文件
for file in os.listdir('rengar_out'):
    with open(f'rengar_out/{file}', 'r', encoding='utf-8') as f:
        # 读取文件内容
        content = f.read()
        # 如果文件中包含"\"Status\":\"Safe\""字段
        if content.find("\"Status\":\"Safe\"") != -1:
            # 将vulnerable字段设置为0
            vulnerable = 0
        else:
            # 否则设置为1
            vulnerable = 1
        # 插入数据
        cursor.execute('INSERT INTO rengar_results (id, vulnerable, output) VALUES (?, ?, ?)', (int(file[:-4]), vulnerable, content))

# 提交事务
conn.commit()