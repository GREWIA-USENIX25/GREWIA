#!/usr/bin/python3
"""
copy_headers.py

Author: Robert McLaughlin <robert349@ucsb.edu>

Copies relevant headers from a node install to
deps/
"""

import argparse
import sys
import os
import os.path
import shutil


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--node-src',
        help="The root directory of a nodejs source repository",
        default='../fuzzer/build/node',
    )

    args = parser.parse_args()
    if not os.path.isdir(args.node_src):
        print('not a directory:', args.node_src)
        exit(1)
    
    path = os.path.abspath(args.node_src)

    print('copying v8 headers from', path)

    # paths to search recursively for headers
    src_v8_paths = [
        (os.path.join(path, 'deps', 'v8', 'include'), os.path.join('v8', 'include')),
        (os.path.join(path, 'deps', 'v8', 'src'), os.path.join('v8', 'src')),
        (os.path.join(path, 'deps', 'v8', 'base'), os.path.join('v8', 'base')),
        (os.path.join(path, 'deps/v8/testing'), 'v8/testing'),
        (os.path.join(path, 'deps/v8/third_party'), 'v8/third_party'),
        (os.path.join(path, 'out/Debug/obj/gen/generate-bytecode-output-root/builtins-generated'), os.path.join('v8', 'builtins-generated')),
        (os.path.join(path, 'out/Debug/obj/gen/torque-output-root/torque-generated'), os.path.join('v8', 'torque-generated')),
        (os.path.join(path, 'deps/icu-small/source/common/'), 'icu-small'),
    ]
    dst_v8_path = os.path.join(os.path.dirname(__file__), 'include')

    for src_v8_path, dst_stub in src_v8_paths:
        print(src_v8_path)
        dst_base = dst_v8_path
        if dst_stub:
            dst_base = os.path.join(dst_v8_path, dst_stub)
        for dirpath, dirnames, fnames in os.walk(src_v8_path):
            for fname in fnames:
                if fname.endswith('.h') or fname.endswith('.inc'):
                    src_path = os.path.join(dirpath, fname)
                    rel_path = os.path.relpath(src_path, src_v8_path)
                    dst_path = os.path.join(dst_base, rel_path)
                    dst_dir = os.path.dirname(dst_path)
                    print(src_path, '->', dst_path)
                    os.makedirs(dst_dir, exist_ok=True)
                    shutil.copy(src_path, dst_path)


if __name__ == '__main__':
    main()
