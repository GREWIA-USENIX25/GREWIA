import sys
import re
from timeit import default_timer as timer

if len(sys.argv) != 3:
    print('Usage: python benchmark.py <filename>')
    sys.exit(1)

def measure(data, pattern):
    start_time = timer()
    matches = re.findall(pattern, data)

    elapsed_time = timer() - start_time

    print(str(elapsed_time * 1e3))

# def measure(data, pattern):
#     start_time = timer()
#     match = re.fullmatch("^(" + pattern + ")$", data)

#     elapsed_time = timer() - start_time

#     print(str(elapsed_time * 1e3))

#f1 = open(sys.argv[2], encoding='utf-8')
f1 = open(sys.argv[2], "rb")
Lines = f1.read()
str1 = ""
for c in Lines:
    str1 = str1 + chr(c)
measure(str1, sys.argv[1])