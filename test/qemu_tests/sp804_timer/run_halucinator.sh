# !/bin/bash

halucinator -c memory_config.yaml \
  -c intercepts.yaml \
  -q \
  -device loader,file=main.elf \
  --semihosting \
  --semihosting-config target=native
  