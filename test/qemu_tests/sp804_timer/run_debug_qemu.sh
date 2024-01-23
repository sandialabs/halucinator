# !/bin/bash

$HALUCINATOR_QEMU_ARM -machine configurable \
  -avatar-config tmp/HALucinator/HALucinator_conf.json \
  -device loader,file=main.elf \
  -nographic --trace *irq* -d in_asm,exec -D qemu.log --semihosting \
  --semihosting-config target=native -S -s 