import os
import sys
import shutil
import random
import string
import requests
import argparse

URL = '192.168.31.38:8080'
HEADER_FIELDS = ['If-None-Match', 'X-Server', 'X-Unique-ID']
POLLUTION_PROPORTION = 1 / 8
POLLUTION_THRESHOLD = 20000
ATTACK_THRESHOLD = 20000

parser = argparse.ArgumentParser(description='Process some parameters.')
parser.add_argument(
    '--dataset_folder',
    required=True
)
parser.add_argument(
    '--length_limit',
    type=int,
    required=True
)
parser.add_argument(
    '--num_malicious',
    type=int,
    required=True
)
parser.add_argument(
    '--num_benign',
    type=int,
    required=True
)

def random_string(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_content_normal(header, length_limit):
    if header == 'If-None-Match':
        return random_string(length_limit)
    elif header == 'X-Server':
        select = random.randint(0, 10)
        return 'localhost:%d' % (8000 + select)
    elif header == 'X-Unique-ID':
        return str(random.randint(0, 2147483647))
    else:
        print ('Error: Unregistered header field %s' % header)
        exit (1)

def generate_content_pollution(header, length_limit):
    if header == 'If-None-Match':
        length_content = random.randint(int(POLLUTION_THRESHOLD / 2), POLLUTION_THRESHOLD)
        length_prefix = random.randint(1, length_limit - length_content)
        length_postfix = length_limit - length_prefix - length_content
        return random_string(length_prefix) + ' ' * length_content + random_string(length_postfix)
    elif header == 'X-Server':
        select = random.randint(0, 1000)
        return 'localhost:%d' % (8000 + select)
    elif header == 'X-Unique-ID':
        return str(random.randint(0, 2147483647))
    else:
        print ('Error: Header field %s cannot be attacked' % header)
        exit (1)

def generate_content_attack(header, length_limit):
    if header == 'If-None-Match':
        length_content = random.randint(ATTACK_THRESHOLD, length_limit)
        length_prefix = random.randint(1, length_limit - length_content)
        length_postfix = length_limit - length_content - length_prefix
        return random_string(length_prefix) + ' ' * length_content + random_string(length_postfix)
    elif header == 'X-Server':
        select = random.randint(0, 1000)
        return 'localhost:%d' % (8000 + select)
    elif header == 'X-Unique-ID':
        return str(random.randint(0, 2147483647))
    else:
        print ('Error: Header field %s cannot be attacked' % header)
        exit (1)

def generate_headers_benign(length_limit):
    headers = {}
    for header in HEADER_FIELDS:
        content = generate_content_normal(header, length_limit)
        headers[header] = content
    return headers

def generate_headers_pollution(length_limit):
    headers = generate_headers_benign(length_limit)
    for header in HEADER_FIELDS:
        content = generate_content_pollution(header, length_limit)
        headers[header] = content
    return headers

def generate_headers_malicious(length_limit):
    headers = generate_headers_benign(length_limit)
    for header in HEADER_FIELDS:
        content = generate_content_attack(header, length_limit)
        headers[header] = content
    return headers

def create_request(headers):
    req = requests.Request('GET', URL, headers = headers)
    prepared = req.prepare()
    req_str = 'GET / HTTP/1.1\r\nHost: %s\r\n%s\r\n\r\n' % (prepared.url, '\r\n'.join('%s: %s' % (k, v) for k, v in prepared.headers.items()))
    return req_str

def generate_sample_malicious(folder, index, length_limit):
    path = '%s/%d-1.txt' % (folder, index)
    headers = generate_headers_malicious(length_limit)
    req_str = create_request(headers)

    with open(path, 'w') as f:
        f.write(req_str)

def generate_sample_pollution(folder, index, length_limit):
    path = '%s/%d-0.txt' % (folder, index)
    headers = generate_headers_pollution(length_limit)
    req_str = create_request(headers)

    with open(path, 'w') as f:
        f.write(req_str)

def generate_sample_benign(folder, index, length_limit):
    path = '%s/%d-0.txt' % (folder, index)
    headers = generate_headers_benign(length_limit)
    req_str = create_request(headers)

    with open(path, 'w') as f:
        f.write(req_str)

def main():
    # Parse parameters
    args = parser.parse_args()
    dataset_folder = args.dataset_folder
    length_limit = args.length_limit
    num_malicious = args.num_malicious
    num_benign = args.num_benign

    index_base = 0

    # Generate malicious samples
    for i in range(num_malicious):
        generate_sample_malicious(dataset_folder, index_base + i, length_limit)
    index_base += num_malicious
    
    # Generate pollution samples
    if 'test' not in dataset_folder:
        num_pollution = int(num_benign * POLLUTION_PROPORTION)
        num_benign -= num_pollution
        for i in range(num_pollution):
            generate_sample_pollution(dataset_folder, index_base + i, length_limit)
        index_base += num_pollution
    
    # Generate pollution samples
    for i in range(num_benign):
        generate_sample_benign(dataset_folder, index_base + i, length_limit)
    index_base += num_benign

if __name__ == "__main__":
    main()