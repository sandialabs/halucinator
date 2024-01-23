HALUCINATOR_PATH=$(shell python -c "import halucinator; print(halucinator.__path__[0]);")

LD_SCRIPT=default_link.ld

HAL_SRCS=qemu/char/virtio.c \
		 qemu/char/virtio_serial_console.c


DEFINES=-DLOG_LEVEL=40

SRCS=$(patsubst %, $(HALUCINATOR_PATH)/drivers/src/%, $(HAL_SRCS))
SRCS+= main.c \
	   intvec.s

all: $(LD_SCRIPT) $(SRCS)
	arm-none-eabi-gcc \
	 -I $(HALUCINATOR_PATH)/drivers/include \
	 -I ../include \
	 $(SRCS) \
	 $(DEFINES)\
	 -lc -lrdimon --specs=rdimon.specs -T $(LD_SCRIPT) -o main.elf
	hal_make_addr -b main.elf -o symbols.yaml

clean:
	rm main.elf
