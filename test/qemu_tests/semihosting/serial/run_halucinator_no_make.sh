# !/bin/bash

# QEMU output will be in <this dir>/tmp/HALucinator/HALucinator_out.txt
set -e
halucinator -c memory_config.yaml \
  -c intercepts.yaml \
  -c symbols.yaml \
  --log_blocks \
  -q -device loader,file=main.elf \
  --semihosting-config target=native \
  -device virtio-serial-device,id=uty0 \
  -chardev socket,path=/tmp/ty0,server,wait=on,id=chardevty0 \
  -device virtserialport,chardev=chardevty0,name=uty0

exit_code=$?
stty sane
echo "HALucinator exit code $exit_code"
exit $exit_code