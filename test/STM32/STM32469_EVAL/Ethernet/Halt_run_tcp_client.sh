#! /bin/bash

source ~/.virtualenvs/halucinator/bin/activate
./halucinator -c=test/STM32/STM32469_EVAL/Halt_config.yaml \
-a=test/STM32/STM32469_EVAL/Ethernet/TCP_Echo_Server_Client--board=STM32469I_EVAL--opt=Os--comp=arm-none-eabi-gcc--comp_version=4.9.3_addrs.yaml \
-m=test/STM32/STM32469_EVAL/Ethernet/Halt_TCP_Echo_Server_Client_Os_memory.yaml --log_blocks -n Halt_TCP_Echo_Client
