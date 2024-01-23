# HALucinator IRQ Config


Halucinator has a generic interrupt controller that can be added to a cpu
to enable controlling of IRQs.  It is added to the Avatar configurable machine
in the memories. Config and can take the following properties

Like below
```yaml
  hal_irq: {base_addr: 0x40000000, size: 0x1000, 
                qemu_name: "halucinator-irq", properties: {num_irqs: 64},
                irq: [{dev: "cpu", "irq_num": 0}]}
```

Other devices connect their interrupts to  this device by adding the `irq` key 
with a list of dictionaries describing their interrupt connections to their memory
entry in the halucinator config. 

The `irq` is shown below.  The first entry in the list connects that devices 
first irq line to the irq line specified in the dictionary.  The dictionary
specifies the device name `dev` of the device to connect to.  This should be the key
of another memory specified.  It is likely the halucinator-irq device or can be
`cpu` which is a special case that it should connect to the cpu directly. 
The `irq_name` for named irqs else this key is left out, and the `irq_num` on the
device specified .

The below example create an arm926 processor to which the halucinator-irq controller is connected to its first interrupt source. Which maps to its IRQ interrupts.  
It will then connect an `sp804` timer with its  first irq line connected to its 32nd (0 indexed) irq line with the name `IRQ`. The `sp804's` second interrupt line will
be connected to its 16th irq line with the name `IRQ`.

```yaml

machine: {arch: 'arm', cpu_model: 'arm926', gdb_exe: 'arm-none-eabi-gdb', entry_addr: 0x00000000}
memories:
    hal_irq: {base_addr: 0x40000000, size: 0x1000, 
                qemu_name: "halucinator-irq", properties: {num_irqs: 64},
                irq: [{dev: "cpu", "irq_num": 0}]}
    sp804_timer: {base_addr: 0x40001000, size: 0x1000, 
                qemu_name: "sp804", irq: [{dev: hal_irq, irq_name: IRQ, irq_num: 31},
                {dev: hal_irq, irq_name: IRQ, irq_num: 15}]}
```

This creates the IRQ Controller at base address and specifies (in properties)
that is has 64 irq input links.  It then connects its irq line to the first (0) 
irq line of the cpu in using the `irq` key and list.


## Registers

The Interrupt controller has the following registers starting at the base address

| Offset       | Name        | Description |
| ------------ | ----------- | ----------- |
| 0:3          | config      | Configuration flags for whole interrupt controller   |
| 4:num_irqs+4 | irq_n_reg   | Status and configuration register for each input irq |

### config register

* bit 0:  Interrupts enabled when 1. No interrupts passed on if 0. Default 0
* all other bits reserved

### irq_n_reg

* bit 0:  Irq Asserted when 1, not asserted when 0
* bit 7:  Irq Mask.  Interrupt ignored if 0, can assert irq if 1.

For an interrupt to be triggered to the processor bit 0 of the config register
must be asserted and bits 0 and 7 of the `irq_n_reg`.  Software should set
bit 7 of the irq_n_reg when it is desired to enable the "hardware" to generated
interrupts.

Other devices can be connected to it by setting the qemu name and irq num

```yaml
qemu_name:
irq_parent:
irq_num: 
```

## Memory Layout

Each IRQ is assigned a byte indicating and controlling the state of each IRQ
Each byte is located at base_address[irq_num+4].  Interrupts must be explicitly
cleared.  For QEMU devices clearing the irq line will also clear the interrupt.

|  Offset   |  Desc  |
|---------- | -------- |
| 0:3        | Global Configuration bit:0 Global Enable, 1 interrupts enabled, 0 disabled |
| 4:NUM_IRQS | IRQ[N] Config and Status Reg |

IRQ_N_CFG_STATUS 
Each config and status register is one byte with each bits described below.
Unused bits are assumed to be zero by default, but values should be preserved 
to enable future expandability.

```
bit: Label
7: 1: Enable 0: Disabled 
6: Unused
5: Unused
4: Unused
3: Unused
2: Unused
1: Unused
0: Active 1 if IRQ is active, 0: Otherwise
```