#!/bin/bash

pkill -f "python3 data_manager.py"
pkill -f "python3 detector.py"
rm -rf /home/gpuserver/RegexNet/build/model.bin /home/gpuserver/RegexNet/build/flag.txt
# 向多个 panes 发送 Ctrl+C 和 exit
for i in {2..0}; do
  tmux send-keys -t $i C-c
  tmux send-keys -t $i 'exit' C-m
done
tmux send-keys -t 0 C-c
tmux send-keys -t 0 'exit' C-m
