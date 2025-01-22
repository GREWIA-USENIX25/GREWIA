#!/bin/bash

# tmux new -s RegexNet

# 在主窗口中创建 2 行 3 列的 panes
# 0 2 4
# 1 3 5
tmux split-window -h -l 66%
tmux split-window -h
tmux split-window -v -t 0
tmux split-window -v -t 2
tmux split-window -v -t 4

# tmux split-window -h
# tmux split-window -v -t 0
# tmux split-window -v -t 2

# 在每个 pane 中执行 cd /home/cpuserver/RegexNet
tmux send-keys -t 0 'cd /home/cpuserver/RegexNet && bash scripts/run.sh application' C-m
tmux send-keys -t 1 'cd /home/cpuserver/RegexNet && bash scripts/run.sh backend' C-m
tmux send-keys -t 2 'cd /home/cpuserver/RegexNet && bash scripts/run.sh haproxy' C-m
tmux send-keys -t 3 'cd /home/cpuserver/RegexNet && bash scripts/run.sh collector' C-m
tmux send-keys -t 4 'cd /home/cpuserver/RegexNet && rm -rf build/model.bin build/flag.txt' C-m
tmux send-keys -t 4 'sleep 2 && ab -c 32 -n 10000000 http://127.0.0.1:8080/' C-m
# tmux send-keys -t 4 'ab -c 32 -n 10000000 http://127.0.0.1:8080/'
tmux send-keys -t 5 'cd /home/cpuserver/RegexNet' C-m
tmux send-keys -t 5 'sleep 16 && bash scripts/run.sh attacker fresh http://127.0.0.1:8080/ 60 30000' C-m
# tmux send-keys -t 5 'bash scripts/run.sh attacker fresh http://127.0.0.1:8080/ 60 30000'