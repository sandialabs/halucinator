#! /bin/bash

source ~/.virtualenvs/halucinator/bin/activate
./halucinator -c=test/STM32/STM32469_EVAL/Halt_config.yaml \
-a=test/STM32/STM32469_EVAL/Ethernet/UDP-echo-client--board=STM32469I_Eval--opt=Os--comp=arm-none-eabi-gcc--comp_version=4.9.3_addrs.yaml \
-m=test/STM32/STM32469_EVAL/Ethernet/Halt_UDP-echo-client_Os_memory.yaml --log_blocks -n Halt_UDP_Echo_Client_no_intercepts
