#ifndef __TIMER_SP804_H__
#define __TIMER_SP804_H__
#include <stdint.h>

// Driver for ARM SP804 Dual Timer.  Reference manual
// https://documentation-service.arm.com/static/5e8e2102fd977155116a4aef

typedef struct Timer_Sp804 {
    uint32_t load; // Value from which timer is decremented
    uint32_t value; // C
    uint32_t ctrl; // Only lowest 8 bits used
    uint32_t int_clear;
    uint32_t RIS; // Raw Interrupt Status
    uint32_t MIS; // Masked Interrupt Status
    uint32_t BGLoad;
} Timer_Sp804_T;

// Note there are two timers timer 1 is at offset 0, and timer 2 is at offset
// 0x20.  Declare like this
// volatile Timer_Sp804_T * timer1 = 0x40001000;
// volatile Timer_Sp804_T * timer2 = 0x40001000 + 0x20;

#define SP804_TIMER_EN 0x80
#define SP804_TIMER_MODE 0x40
#define SP804_TIMER_INT_ENABLE 0x20
#define SP804_TIMER_PRE 0x0C
#define SP804_TIMER_SIZE 0x02
#define SP804_TIMER_ONE_SHOT 0x01
#define SP804_TIMER_ENABLED 0x80

void sp804_enable(volatile Timer_Sp804_T* timer);

void sp804_disable(volatile Timer_Sp804_T* timer);

void sp804_set_prescaler(volatile Timer_Sp804_T* timer, uint32_t prescaler);

void sp804_set_periodic(volatile Timer_Sp804_T* timer, uint32_t value);

void sp804_enable_irq(volatile Timer_Sp804_T* timer);

void sp804_clear_irq(volatile Timer_Sp804_T* timer);

void sp804_set_to_hertz(volatile Timer_Sp804_T* timer, int tickspersec);

uint32_t sp804_get_irq_status(volatile Timer_Sp804_T* timer);

uint32_t sp804_get_timer_value(volatile Timer_Sp804_T* timer);

#endif