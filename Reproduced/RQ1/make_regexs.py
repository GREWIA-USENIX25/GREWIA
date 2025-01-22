import sys
import os

# 创建文件夹regexes
if not os.path.exists('regexes'):
    os.makedirs('regexes')
    
with open(sys.argv[1], 'r') as f:
    for i, line in enumerate(f):
        if i % 1000 == 0:
            print(i)
        # 将每行正则写入一个新的文件
        with open('regexes/{}.txt'.format(i+1), 'w') as f:
            f.write(line)