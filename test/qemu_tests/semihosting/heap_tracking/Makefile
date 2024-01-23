
all:
	arm-none-eabi-gcc intvec.s main.c -lc -lrdimon --specs=rdimon.specs -T default_link.ld -o main.elf
	hal_make_addr -b main.elf -o symbols.yaml
clean:
	rm main.elf