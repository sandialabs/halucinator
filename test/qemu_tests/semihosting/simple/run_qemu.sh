# !/bin/bash

$HALUCINATOR_QEMU_ARM -machine configurable \
  -avatar-config HALucinator_conf.json \
  -device loader,file=main.elf \
  -nographic -d in_asm,exec -D qemu.log --semihosting \
  --semihosting-config target=native \
  -device virtio-serial-device,id=ty0 -chardev file,id=ty0,path=/tmp/ty0 \
  -device virtio-net-device,id=eth0
