import os

# 新建regexes文件夹
if not os.path.exists('regexes'):
    os.mkdir('regexes')

with open('qualified_regex_736562.txt', 'r') as f:
    for i, line in enumerate(f):
        if i % 1000 == 0:
            print(i)
        # 将每行正则写入一个新的文件
        with open('regexes/{}.txt'.format(i+1), 'w') as f:
            f.write(line)