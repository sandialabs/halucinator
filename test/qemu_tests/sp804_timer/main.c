#include <stdio.h>
#include "hal_irq_driver.h"
#include <timer_sp804.h>

/*

*/


#define NUM_IRQS 64
#define HAL_IRQ_BASE_ADDR 0x40000000

volatile Timer_Sp804_T * timer1 = (Timer_Sp804_T *) 0x40001000;
volatile Timer_Sp804_T * timer2 = (Timer_Sp804_T *) (0x40001000 + 0x20);

void (* irq_callbacks[NUM_IRQS])(void *);
void * irq_callback_params[NUM_IRQS];
HAL_IRQ_CONFIG_T irq_cfg;


void timer1_isr(void * param){
    Timer_Sp804_T * timer = (Timer_Sp804_T *) param;
    static uint32_t count = 0;  // Use of static makes so will want a unique isr
                                // per timer
    count++;
    sp804_clear_irq(timer);
    printf("Timer ISR %i\n", count);
}

int main(){

    int active_irq;

    hal_irq_config_init(&irq_cfg,(HAL_IRQ_REGS_T *) HAL_IRQ_BASE_ADDR, NUM_IRQS, 
                        irq_callbacks, irq_callback_params, 1);

    
    hal_irq_callback(&irq_cfg, 0, timer1_isr, (void *)timer1);
    hal_irq_status_write(&irq_cfg, GLOBAL_IRQ_ENABLED);
    hal_irq_n_enable(&irq_cfg, 0);
    

    active_irq = hal_irq_get_first_active(&irq_cfg);

    printf("Timer Value 0x%08x\n", sp804_get_timer_value(timer1));
    enable_global_irq();
    sp804_set_periodic(timer1, 0x00100000);
    sp804_enable_irq(timer1);
    sp804_enable(timer1);
    
    for(int j=0; j < 100; j++){
        printf("Timer Value 0x%08x\n", sp804_get_timer_value(timer1));
        for(int i = 0; i < 0xFF; i++);
    }

}

void exit(int __status){
    while(1);
}