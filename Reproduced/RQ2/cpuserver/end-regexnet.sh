#!/bin/bash

# 向多个 panes 发送 Ctrl+C 和 exit
for i in {6..0}; do
  tmux send-keys -t $i C-c
  tmux send-keys -t $i 'exit' C-m
done
tmux send-keys -t 0 C-c
tmux send-keys -t 0 'exit' C-m
# cd /home/cpuserver
# sudo netstat -anp | grep 9003
