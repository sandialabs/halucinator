# ~/bin/bash

# Build the main file
make all

# Create Temp directory to test results
TEST_TMP=tmp_test_results
rm -rf $TEST_TMP
mkdir -p $TEST_TMP

RESULT_FILE=$TEST_TMP/qemu_exit_code.log
RECEIVED_TEXT=$TEST_TMP/received_data.txt

# Run QEMU and Associated tests
tmux new-session -d bash
tmux split-window -h bash
tmux send -t 0 "workon hal_canaries; ./run_qemu.sh; tmux wait -S qemu_done" Enter
tmux send -t 1 "sleep 5; echo 0123456789012345678901234567890123456789 | socat /tmp/ty0 - >$RECEIVED_TEXT" Enter
tmux wait qemu_done
tmux send -t 0 "echo $? > $RESULT_FILE" Enter

# Check Results
qemu_exit_code=$(<$RESULT_FILE)
received_data=$(<$RECEIVED_TEXT)
echo "$received_data"
if [ "$qemu_exit_code" -eq '0' ] && [[ "$received_data" == "Testing serial" ]];
then
    echo "Test Successful"
    tmux kill-session
    exit 0
else
    echo "Test Failed"
    exit -1
fi
#   split-window -h 'sleep 2; echo 0123456789012345678901234567890123456789 | socat /tmp/ty0 -; sleep 30' \; \
#   detach-client
