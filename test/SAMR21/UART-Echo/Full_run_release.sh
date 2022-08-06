#! /bin/bash

source ~/.virtualenvs/halucinator/bin/activate
./halucinator  -c=test/SAMR21/UART-Echo/Full_SAMR21_config.yaml \
               -m=test/SAMR21/UART-Echo/Memories_Release_USART.yaml \
               -a=test/SAMR21/UART-Echo/Release_USART_QUICK_START1_addrs.yaml \
               --log_blocks -n Full_UART-Echo
