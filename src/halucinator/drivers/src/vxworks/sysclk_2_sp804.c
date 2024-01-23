#include <assert.h>
#include <stddef.h>

#include <log.h>
#include <qemu/timer/sp804.h>
#include <vxworks/defines.h>
#include <vxworks/sysclk.h>

static int l_sysClkRate = 0;

struct systick_config {
    volatile Timer_Sp804_T* timer;
    HAL_IRQ_CONFIG_T* irq_cfg;
    int rate;
    int irq_num;
};

static struct systick_config l_clk_cfg;

int vxworks_init_sysClk(volatile Timer_Sp804_T* clk, HAL_IRQ_CONFIG_T* irq_config, int irq_num)
{
    LOG_DEBUG("In %s\n", __PRETTY_FUNCTION__);
    l_clk_cfg.timer = clk;
    l_clk_cfg.irq_cfg = irq_config;
    l_clk_cfg.rate = 0;
    l_clk_cfg.irq_num = irq_num;
}
/*
*@intercept sysClkRateSet
* Note rates is ticks persecond
*/
int INTERCEPT sysClkRateSet(int rate)
{
    LOG_DEBUG("In %s\n", __PRETTY_FUNCTION__);
    assert(l_clk_cfg.timer != NULL);
    l_clk_cfg.rate = rate;
    sp804_set_to_hertz(l_clk_cfg.timer, rate);
    return VXWORKS_OK;
}

/*
*@intercept sysClkRateGet
*/
int INTERCEPT sysClkRateGet()
{
    LOG_DEBUG("In %s\n", __PRETTY_FUNCTION__);
    return l_clk_cfg.rate;
    ;
}

/*
*@intercept sysClkEnable
*/
int INTERCEPT sysClkEnable(int rate)
{
    LOG_DEBUG("In %s\n", __PRETTY_FUNCTION__);
    assert(l_clk_cfg.timer != NULL);

    sp804_enable_irq(l_clk_cfg.timer);
    sp804_enable(l_clk_cfg.timer);
    hal_irq_n_enable(l_clk_cfg.irq_cfg, l_clk_cfg.irq_num);
    return VXWORKS_OK;
}

/*
*@intercept sysClkDisable
*/
int INTERCEPT sysClkDisable(int rate)
{
    LOG_DEBUG("In %s\n", __PRETTY_FUNCTION__);
    assert(l_clk_cfg.timer != NULL);
    sp804_disable(l_clk_cfg.timer);
    return VXWORKS_OK;
}