# !/bin/bash
set -e

$HALUCINATOR_QEMU_ARM -machine configurable \
  -avatar-config HALucinator_conf.json \
  -device loader,file=main.elf \
  -nographic --semihosting \
  --semihosting-config target=native \
  -device virtio-serial-device,id=uty0 \
  -chardev socket,path=/tmp/ty0,server,wait=on,id=chardevty0 \
  -device virtserialport,chardev=chardevty0,name=uty0

#--trace "virtio_*"
stty sane
#Then in another terminal: `socat /tmp/ty0 -` then this should print received messages and you should be able to type to send messages.