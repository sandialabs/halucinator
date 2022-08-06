
all:
	arm-none-eabi-gcc call_test.c -o call_test.elf
	arm-none-eabi-objcopy -O binary call_test.elf call_test.elf.bin
	python -m halucinator.util.elf_sym_hal_getter -b call_test.elf
