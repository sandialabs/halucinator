# Semi Hosting Test


This program builds a configuable machine that can run an elf file for the arm926
cpu while using semihosting to enable using some of libc.  Most importantly
it allows use of printf.


To run use this command

```
$HALUCINATOR_QEMU_ARM -machine configurable \
  -avatar-config HALucinator_conf.json \
  -device loader,file=main.elf \
  -nographic -d in_asm,exec -D qemu.log --semihosting
```

You will then see this in the output

```
(qemu) Insert Call Test Started
Entry Function Executed
Value of a: 11, Value of b: 20
```

You can also run it with GDB using by adding the `-s -S` to your GDB command
then semihosting will direct through gdb.

In terminal 1
```
$HALUCINATOR_QEMU_ARM -machine configurable \
   -avatar-config HALucinator_conf.json \
   -device loader,file=main.elf \
   -nographic -d in_asm,exec -D qemu.log --semihosting -s -S
```

In terminal 2
```
arm-none-eabi-gdb main.elf
(gdb) target remote localhost:1234
(gdb) b main
(gdb) b exit
(gdb) c
(gdb) c
```

You should see
```
Insert Call Test Started
Entry Function Executed
Value of a: 11, Value of b: 20
```

## Running with HALucinator

```
halucinator -c memory_config.yaml -q -device loader,file=main.elf \
  --semihosting-config target=native
```

Run
```
cat tmp\HALucinator\HALucinator_out.log
```

Will show
```txt
...
Insert Call Test Started
Entry Function Executed
Value of a: 11, Value of b: 20
```

If you want to watch the semihosting output use `tail -f tmp\HALucinator\HALucinator_out.log`
