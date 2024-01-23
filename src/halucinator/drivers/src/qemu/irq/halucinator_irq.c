#include <assert.h>
#include <halucinator.h>
#include <log.h>
#include <qemu/irq/halucinator_irq.h>
#include <stddef.h>
#include <stdio.h>

static HAL_IRQ_CONFIG_T* default_irq_cfg;

void enable_global_irq()
{
    asm volatile(
        "mrs r0, cpsr \n\t"
        "bic r0, r0, #0x80\n\t"
        "msr cpsr, r0"
        :
        :
        : "r0", "cc");
}

void enable_global_firq()
{
    asm volatile(
        "mrs r0, cpsr \n\t"
        "bic r0, r0, #0x40\n\t"
        "msr cpsr, r0"
        :
        :
        : "r0", "cc");
}

void disable_global_irq()
{

    asm volatile(
        "mrs r0, cpsr \n\t"
        "orr r0, r0, #0x80\n\t"
        "msr cpsr, r0"
        :
        :
        : "r0", "cc");
}

void disable_global_firq()
{

    asm volatile(
        "mrs r0, cpsr \n\t"
        "orr r0, r0, #0x40\n\t"
        "msr cpsr, r0"
        :
        :
        : "r0", "cc");
}

void irq_handler()
{
    int irq_num;
    void (*callback)(void*);
    if (default_irq_cfg != NULL) {
        irq_num = hal_irq_get_first_active(default_irq_cfg);
        if (irq_num != -1) {
            printf("IRQ %i active \n", irq_num);
            assert(irq_num < default_irq_cfg->num_irqs);
            callback = default_irq_cfg->callbacks[irq_num];
            if (callback != NULL) {
                printf("Calling Callback\n");
                (*callback)(default_irq_cfg->callback_params[irq_num]);
            }
        }
    }
}

void hal_irq_config_init(HAL_IRQ_CONFIG_T* cfg, HAL_IRQ_REGS_T* base_addr,
    uint32_t num_irqs, void (*(*callbacks))(void*),
    void*(*callback_params),
    int priority)
{

    default_irq_cfg = cfg;
    cfg->ctrl_addr = base_addr;
    cfg->num_irqs = num_irqs;
    cfg->callbacks = callbacks;
    cfg->callback_params = callback_params;
    cfg->low_index_priority = priority;

    int i;
    if (cfg->callbacks != NULL && cfg->callback_params != NULL) {
        for (i = 0; i < cfg->num_irqs; i++) {
            cfg->callbacks[i] = NULL;
            cfg->callback_params[i] = NULL;
        }
    } else {
        cfg->callbacks = NULL;
        cfg->callback_params = NULL;
    }
}

/*
* Sets a Callback function for use with the default IRQ controller
*/
void hal_irq_callback(HAL_IRQ_CONFIG_T* cfg, uint32_t irq_num,
    void (*callback)(void*),
    void* params)
{

    assert(irq_num < cfg->num_irqs);
    assert(cfg->callbacks != NULL);
    assert(cfg->callback_params != NULL);

    cfg->callbacks[irq_num] = callback;
    cfg->callback_params[irq_num] = params;
}

/*
    Reads from the status register
*/
uint32_t hal_irq_status_read(HAL_IRQ_CONFIG_T* cfg)
{
    return cfg->ctrl_addr->status;
}

/*
    Writes to the status register
*/
void hal_irq_status_write(HAL_IRQ_CONFIG_T* cfg, uint32_t status)
{
    cfg->ctrl_addr->status = status;
}

/*
    Sets the enable bit for irq n
*/
void hal_irq_n_enable(HAL_IRQ_CONFIG_T* cfg, uint32_t irq_n)
{
    LOG_DEBUG("In %s %i\n", __PRETTY_FUNCTION__, irq_n);
    LOG_DEBUG("IRQ Controller is %p\n", cfg);
    assert(irq_n < cfg->num_irqs);

    cfg->ctrl_addr->irq_regs[irq_n] |= IRQ_N_ENABLED;
}

/*
    Clears the enable bit for irq n
*/
void hal_irq_n_disable(HAL_IRQ_CONFIG_T* cfg, uint32_t irq_n)
{
    LOG_DEBUG("In %s\n %i", __PRETTY_FUNCTION__, irq_n);
    assert(irq_n < cfg->num_irqs);
    cfg->ctrl_addr->irq_regs[irq_n] &= ~IRQ_N_ENABLED;
}

/*
    Triggers irq n
*/
void hal_irq_n_trigger(HAL_IRQ_CONFIG_T* cfg, uint32_t irq_n)
{
    assert(irq_n < cfg->num_irqs);
    cfg->ctrl_addr->irq_regs[irq_n] |= IRQ_N_ACTIVE;
}

/*
    Triggers clears irq n
*/
void hal_irq_n_clear(HAL_IRQ_CONFIG_T* cfg, uint32_t irq_n)
{
    assert(irq_n < cfg->num_irqs);
    cfg->ctrl_addr->irq_regs[irq_n] &= ~IRQ_N_ACTIVE;
}

/*
Returns the highest priority active irq
*/
int hal_irq_get_first_active(HAL_IRQ_CONFIG_T* cfg)
{
    int i;
    uint32_t irq_reg;
    if (cfg->low_index_priority) {
        for (i = 0; i < cfg->num_irqs; i++) {
            irq_reg = cfg->ctrl_addr->irq_regs[i];
            if (irq_reg & IRQ_N_ACTIVE && irq_reg & IRQ_N_ENABLED) {
                return i;
            }
        }
    } else {
        for (i = cfg->num_irqs - 1; i >= 0; --i) {
            irq_reg = cfg->ctrl_addr->irq_regs[i];
            if (irq_reg & IRQ_N_ACTIVE && irq_reg & IRQ_N_ENABLED) {
                return i;
            }
        }
    }
    return -1;
}
