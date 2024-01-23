#include <assert.h>
#include <halucinator.h>
#include <qemu/irq/halucinator_irq.h>
#include <vxworks/irq.h>

static HAL_IRQ_CONFIG_T* l_irq_controller;
static uint32_t l_irq_level;

#define LOG_LEVEL INFO_LEVEL

void vxworks_irq_init(HAL_IRQ_CONFIG_T* irq_controller, uint32_t level)
{
    LOG_DEBUG("In %s\n", __PRETTY_FUNCTION__);
    l_irq_level = level;
    l_irq_controller = irq_controller;
}

/*
* @intercept IntLvlVecChk
*
*   This determine what interrupt is enabled and disable the interrupt controller interrupt
*   In reality, should implement multiple priorities in interrupt controller and this should
*   Change the level so only higher priority interrupts will be generated
*/
int INTERCEPT intLvlVecChk(int* level, int* irq_num)
{
    int active_irq;
    uint32_t status_reg;
    void (*callback)(void*);
    LOG_DEBUG("In %s\n", __PRETTY_FUNCTION__);
    active_irq = hal_irq_get_first_active(l_irq_controller);

    LOG_DEBUG("Active IRQ %i\n", active_irq);

    if (active_irq != -1) {
        *(irq_num) = active_irq;
        *(level) = l_irq_level;

        assert(active_irq < l_irq_controller->num_irqs);
        callback = l_irq_controller->callbacks[active_irq];
        if (callback != NULL) {
            LOG_DEBUG("Calling Callback\n");
            (*callback)(l_irq_controller->callback_params[active_irq]);
        }
        LOG_DEBUG("Leaving %s IRQ %i, Level %i\n", __PRETTY_FUNCTION__, *irq_num, *level);
        status_reg = hal_irq_status_read(l_irq_controller);
        hal_irq_status_write(l_irq_controller, status_reg & (~GLOBAL_IRQ_ENABLED));
        return 0;
    } else {
        LOG_ERROR("IRQ with no source occurred\n");
        return -1;
    }
}

/*
    Intercepts intLvlVecAckRtn
    This re-enables the global interrupt.  In reality it should restore previous irq level
    With our interrupt controller all interrupts have same priority, and we don't support
    preemption of interrupts.
*/
int INTERCEPT intLvlVecAckRtn(int* level, int* irq_num)
{
    uint32_t status_reg;
    LOG_DEBUG("In %s\n", __PRETTY_FUNCTION__);
    status_reg = hal_irq_status_read(l_irq_controller);
    hal_irq_status_write(l_irq_controller, status_reg | GLOBAL_IRQ_ENABLED);
}

/*
*@ intercept intEnable
*/
void INTERCEPT intEnable(uint32_t irq_num)
{
    LOG_DEBUG("In %s enable 0x%02x\n", __PRETTY_FUNCTION__, irq_num);
    hal_irq_n_enable(l_irq_controller, irq_num);
}

/*
* @intercept intDisable
*/
void INTERCEPT intDisable(uint32_t irq_num)
{
    LOG_DEBUG("In %s disable 0x%02x\n", __PRETTY_FUNCTION__, irq_num);
    hal_irq_n_disable(l_irq_controller, irq_num);
}
