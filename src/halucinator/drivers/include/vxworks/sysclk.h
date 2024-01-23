#ifndef __VXWORKS_SYSCLK_H__
#define __VXWORKS_SYSCLK_H__

#include <halucinator.h>
#include <qemu/irq/halucinator_irq.h>
#include <qemu/timer/sp804.h>

int vxworks_init_sysClk(volatile Timer_Sp804_T* clk, HAL_IRQ_CONFIG_T* irq_config, int irq_num);

/*
*@intercept sysClkRateSet
* Note rates is ticks persecond
*/
int INTERCEPT sysClkRateSet(int rate);

/*
*@intercept sysClkRateGet
*/
int INTERCEPT sysClkRateGet();

/*
*@intercept sysClkEnable
*/
int INTERCEPT sysClkEnable(int rate);

/*
*@intercept sysClkDisable
*/
int INTERCEPT sysClkDisable(int rate);

#endif