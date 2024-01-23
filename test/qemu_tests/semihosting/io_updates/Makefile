
all:
	arm-none-eabi-gcc main.c intvec.s -lc -lrdimon --specs=rdimon.specs -T default_link.ld -o main.elf
	hal_make_addr -b main.elf -o symbols.yaml
clean:
	rm main.elf