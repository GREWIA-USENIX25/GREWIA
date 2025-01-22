import os
import sys
import time
import requests
import random

class Attacker:
    def __init__(self):
        self.count = 0

    def request_http(self, url, length):
        self.count += 1
        print("length: %d" % length)
        try:
            # temp_length = length
            temp_length = length
            headers_content = 'a' * temp_length + 'c'
            # 打印headers_content有多少kb
            print(f"headers_content: {sys.getsizeof(headers_content)/1024:.4f} kb")
            r = requests.get(url, headers = {'content': headers_content, 'X-Server': '192.168.31.38'}, timeout=10)
            print ("attack, reply %d, %d" % (r.status_code, self.count))
        except:
            print ("attack, no reply, %d" % self.count)

def main():
    # url = 'http://127.0.0.1:8080/'
    # # length = 52000 # reply 50kb左右
    # length = 30 # reply 50kb左右
    # attacker = Attacker()
    # attacker.request_http(url, length)

    
    url = 'http://127.0.0.1:8080/'
    frequency = 60 # number of attacks per minute
    length = 25
    interval = 60.0 / frequency
    time.sleep(1.0)

    attacker = Attacker()
    start_time = time.time()
    while time.time() - start_time < 60:
        send_time = time.time()
        attacker.request_http(url, length)
        elapsed = time.time() - send_time
        if elapsed < interval:
            time.sleep(interval - elapsed)

if __name__ == "__main__":
    print ('==========Start %f==========' % time.time())
    main()
    print ('==========End %f==========' % time.time())
