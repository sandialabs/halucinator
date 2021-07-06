# Copyright 2021 National Technology & Engineering Solutions of Sandia, LLC 
# (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, 
# the U.S. Government retains certain rights in this software.

all:
	arm-none-eabi-gcc large_parameters_test.c -o large_parameters.elf
	arm-none-eabi-objcopy -O binary large_parameters.elf large_parameters.elf.bin
	python -m halucinator.util.elf_sym_hal_getter -b large_parameters.elf