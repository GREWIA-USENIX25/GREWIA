import os
import sys
import time
import requests
import random

class Attacker:
    def __init__(self):
        self.count = 0

    def request_http(self, url, path):
        self.count += 1

        with open('/home/cpuserver/RegexNet/regex.txt', 'r') as f:
            regex = f.read().strip()

        try:
            # Use binary mode and ignore decoding errors
            with open(path, 'rb') as f:
                headers_content = f.read().decode('utf-8', errors='ignore').strip()
            # Remove non-printable characters except newlines and tabs
            headers_content = ''.join(char for char in headers_content if char.isprintable() or char in '\n\t')
            
            # Remove null bytes
            headers_content = headers_content.replace('\x00', '')
            
            # Remove any other control characters
            headers_content = ''.join(char for char in headers_content if ord(char) >= 32 or char in '\n\t')
            # Replace newlines and spaces with safe alternatives for HTTP headers
            headers_content = headers_content.replace('\n', '\\n').replace('\r', '\\r').replace(' ', '%20')
            # Print headers_content size in kb
            print(f"headers_content: {sys.getsizeof(headers_content)/1024:.4f} kb")
            
            # Truncate headers_content to 40K if larger
            if sys.getsizeof(headers_content) > 40 * 1024:
                headers_content = headers_content[:40 * 1024]
                print(f"Truncated headers_content to 40K")
            
            # Encode headers_content as utf-8 to handle non-latin1 characters
            headers_content_encoded = headers_content.encode('utf-8').decode('latin1')
            r = requests.get(url, headers = {'regex': regex, 'path': path, 'content': headers_content_encoded, 'X-Server': '192.168.31.38'}, timeout=10)
            print ("attack, reply %d, %d" % (r.status_code, self.count))
        except Exception as e:
            print ("attack error: %s, count: %d" % (str(e), self.count))

def main():
    # url = 'http://127.0.0.1:8080/'
    # # length = 52000 # reply 50kb左右
    # length = 30 # reply 50kb左右
    # attacker = Attacker()
    # attacker.request_http(url, length)

    url = 'http://127.0.0.1:8080/'
    frequency = 60 # number of attacks per minute
    interval = 60.0 / frequency
    time.sleep(1.0)

    attack_dir = '/home/cpuserver/RegexNet/attack_tmp'
    attack_files = [os.path.join(attack_dir, f) for f in os.listdir(attack_dir)]
    index = 0

    attacker = Attacker()
    start_time = time.time()
    while time.time() - start_time < 60:
        send_time = time.time()
        attacker.request_http(url, attack_files[index])
        index = (index + 1) % len(attack_files)
        elapsed = time.time() - send_time
        if elapsed < interval:
            time.sleep(interval - elapsed)

if __name__ == "__main__":
    print ('==========Start %f==========' % time.time())
    main()
    print ('==========End %f==========' % time.time())
