#ifndef __VXWORKS_IRQ_H__
#define __VXWORKS_IRQ_H__

#include <halucinator.h>
#include <qemu/irq/halucinator_irq.h>

void vxworks_irq_init(HAL_IRQ_CONFIG_T* irq_controller, uint32_t level);

/*
* @intercept intLvlVecChk
*/
int INTERCEPT intLvlVecChk(int* level, int* irq_num);

//// Below are logging only, which is hard todo in C due to rewriting
/*
*@ intercept intConnect
*/
// void INTERCEPT intConnect(uint32_t irq_num, uint32_t * callback, uint32_t *param);

/*
*@ intercept intEnable
*/
void INTERCEPT intEnable(uint32_t irq_num);

/*
* @intercept intDisable
*/
void INTERCEPT intDisable(uint32_t irq_num);

#endif