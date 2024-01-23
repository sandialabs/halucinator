# !/bin/bash

# QEMU output will be in <this dir>/tmp/HALucinator/HALucinator_out.txt

halucinator -c memory_config.yaml \
  -c intercepts.yaml \
  --log_blocks \
  -q -device loader,file=main.elf \
  --semihosting-config target=native \
  # Below not needed but shows how to add other devices
  -device virtio-serial-device,id=ty0 -chardev file,id=ty0,path=/tmp/ty0
  
