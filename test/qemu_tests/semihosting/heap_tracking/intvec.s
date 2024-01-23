
.section .isr_vector


_isr_vector:
    b reset_handler             ; @ 0x00
    b undef_handler             ; @ 0x04
    b swi_handler               ; @ 0x08
    b prefetch_abort_handler    ; @ 0x0c
    b data_abort_handler        ; @ 0x10
    b .                         ; @ 0x14 Reserved Vector  
    b _irq_handler              ; @ 0x18
    b fiq_handler               ; @ 0x20

reset_handler:
    mrs r0, cpsr
    bic r1, r0, #0x7
    orr r1, r1, #0x2
    msr cpsr, r1  ; @ Switched to IRQ Mode
    ldr sp, =_irq_stack  
    msr cpsr, r0 ;  @ Switch back to previous mode
    b _start

undef_handler:
    b undef_handler

swi_handler:
    b swi_handler

prefetch_abort_handler:
    b prefetch_abort_handler

data_abort_handler:
    b data_abort_handler

_irq_handler:
    subs lr, lr, #4  ; @ return address is ahead by 4 bytes
    stmfd sp!, {lr}
    mrs lr, SPSR
    stmfd sp!, {r0-r3, r12, lr}
    bl irq_handler
    ldmfd sp!, {r0-r3, r12, lr}
    msr SPSR_csxf, lr
    ldmfd sp!, {pc}^

fiq_handler:
    b fiq_handler

.weak irq_handler
irq_handler:
    mov pc, lr 
