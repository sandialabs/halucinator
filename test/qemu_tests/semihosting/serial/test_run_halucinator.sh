# ~/bin/bash
#  usage ./test_run_halucinator.sh [keep_tmux_session]
#  if any second arg is provided the tmux session will be kept, useful for debugging

# Create Temp directory to test results
TEST_TMP=tmp_test_results
rm -rf $TEST_TMP
mkdir -p $TEST_TMP

RESULT_FILE=$TEST_TMP/halucinator_exit_code.log
RECEIVED_TEXT=$TEST_TMP/halucinator_received_data.txt


# Build Binary and run in HALucinator
echo "Starting Build"
tmux new-session -d bash
tmux split-window -h bash
tmux send -t 0 "workon hal_canaries; make all; tmux wait -S make_done" Enter
tmux wait make_done
echo "Build Done"
echo "Starting Halucinator and socat"
tmux send -t 0 "./run_halucinator_no_make.sh; tmux wait -S hal_done" Enter
tmux send -t 1 "sleep 1; echo 0123456789012345678901234567890123456789 | socat /tmp/ty0 - >$RECEIVED_TEXT" Enter
tmux wait hal_done
tmux send -t 0 "echo $? > $RESULT_FILE" Enter

if [ $1 ];
then
    echo "Use tmux attach to see output"
else
    echo "Killing tmux session"
    tmux kill-session
fi

# Check Results
qemu_exit_code=$(<$RESULT_FILE)
received_data=$(<$RECEIVED_TEXT)
echo "$received_data"
if [ "$qemu_exit_code" -eq '0' ] && [[ "$received_data" == "Testing serial" ]];
then
    echo "Test Successful"

    exit 0
else
    echo "Test Failed"
    exit -1
fi
