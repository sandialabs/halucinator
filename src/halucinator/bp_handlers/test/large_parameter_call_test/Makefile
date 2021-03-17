
all:
	arm-none-eabi-gcc large_parameters_test.c -o large_parameters.elf
	arm-none-eabi-objcopy -O binary large_parameters.elf large_parameters.elf.bin
	python -m halucinator.util.elf_sym_hal_getter -b large_parameters.elf