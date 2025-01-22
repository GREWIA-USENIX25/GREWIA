This directory contains files dealing with extracting bytecode from the nodejs regexp interpreter.


Building:
First, build the fuzzer.
Run `copy_headers.py`.
Run `ln -s ../fuzzer/build/node_libs deps`
Run `make`

