
all:
	arm-none-eabi-gcc intvec.s -I ../../../src/halucinator/drivers/include \
	 ../../../src/halucinator/drivers/src/hal_irq_driver.c \
	 ../../../src/halucinator/drivers/src/timer_sp804.c \
	 main.c -lc -lrdimon --specs=rdimon.specs -T default_link.ld -o main.elf 
clean:
	rm main.elf