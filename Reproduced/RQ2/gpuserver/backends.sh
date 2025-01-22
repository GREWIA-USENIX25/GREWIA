tmux new-session -d -s test

rm -rf /home/gpuserver/testlog
mkdir -p /home/gpuserver/testlog

# tmux split-window -h -l 90 -t test
tmux split-window -h -l 60 -t test
tmux split-window -h -t test

# tmux split-window -h -t test

tmux send-keys -t 0 'cd /home/gpuserver/RegexNet && rm -rf build/model.bin build/flag.txt && bash scripts/run.sh data_manager 2>&1 | tee /home/gpuserver/testlog/data_manager.log ' C-m
tmux send-keys -t 1 'cd /home/gpuserver/RegexNet && bash scripts/run.sh detector 2>&1 | tee /home/gpuserver/testlog/detector.log ' C-m
# tmux send-keys -t 2 'sleep 83 && bash /home/gpuserver/end-regexnet.sh &' C-m
# tmux send-keys -t 2 'cd /home/gpuserver/RegexNet' C-m
