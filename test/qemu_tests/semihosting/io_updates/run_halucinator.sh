# !/bin/bash

# QEMU output will be in <this dir>/tmp/HALucinator/HALucinator_out.txt
make all
halucinator -c memory_config.yaml \
  -c intercepts.yaml \
  -c symbols.yaml \
  --log_blocks \
  -q -device loader,file=main.elf \
  --semihosting-config target=native

