tmux new-session -d -s test
# tmux attach-session -t test

rm -rf /home/cpuserver/testlog
mkdir -p /home/cpuserver/testlog

tmux split-window -h -l 66% -t test
tmux split-window -h -t test
tmux split-window -f -t test
tmux split-window -h -l 66% -t test
tmux split-window -h -t test



# 在每个 pane 中执行 cd /home/cpuserver/RegexNet
tmux send-keys -t 0 'cd /home/cpuserver/RegexNet && bash scripts/run.sh application 2>&1 | tee /home/cpuserver/testlog/application.log ' C-m
tmux send-keys -t 1 'cd /home/cpuserver/RegexNet && bash scripts/run.sh backend 2>&1 | tee /home/cpuserver/testlog/backend.log ' C-m
tmux send-keys -t 2 'cd /home/cpuserver/RegexNet && bash scripts/run.sh haproxy 2>&1 | tee /home/cpuserver/testlog/haproxy.log ' C-m
tmux send-keys -t 3 'cd /home/cpuserver/RegexNet && bash scripts/run.sh collector 2>&1 | tee /home/cpuserver/testlog/collector.log ' C-m
tmux send-keys -t 4 'cd /home/cpuserver/RegexNet && rm -rf build/model.bin build/flag.txt' C-m
tmux send-keys -t 4 'sleep 2 && ab -c 32 -n 10000000 http://127.0.0.1:8080/ 2>&1 | tee /home/cpuserver/testlog/ab.log ' C-m
# tmux send-keys -t 4 'ab -c 32 -n 10000000 http://127.0.0.1:8080/'
tmux send-keys -t 5 'cd /home/cpuserver/RegexNet' C-m
# tmux send-keys -t 5 'sleep 78 && bash /home/cpuserver/end-regexnet.sh &' C-m
# tmux send-keys -t 5 'bash scripts/run.sh attacker fresh http://127.0.0.1:8080/ 60 30000'
# tmux send-keys -t 5 'sleep 17 && python /home/cpuserver/RegexNet/build/attacker/attacker_fresh.py http://127.0.0.1:8080/ 60 30000 > /home/cpuserver/testlog/attacker.log ' C-m
# tmux send-keys -t 5 'sleep 17 && python /home/cpuserver/RegexNet/test.py > /home/cpuserver/testlog/attacker.log ' C-m
tmux send-keys -t 5 'sleep 17 && python /home/cpuserver/RegexNet/attack.py > /home/cpuserver/testlog/attacker.log ' C-m
# tmux attach-session -t test

