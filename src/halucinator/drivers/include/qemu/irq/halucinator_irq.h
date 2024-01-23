#ifndef __HAL_IRQ_DRIVER_H__
#define __HAL_IRQ_DRIVER_H__

#include <stdint.h>

#define GLOBAL_IRQ_ENABLED 0x00000001
#define IRQ_N_ACTIVE 0x01
#define IRQ_N_ENABLED 0x80

typedef struct HAL_IRQ_REGS {
    volatile uint32_t status;
    volatile uint8_t irq_regs[];
} HAL_IRQ_REGS_T;

typedef struct hal_irq_config {

    HAL_IRQ_REGS_T* ctrl_addr; // Base address of the IRQ Controller
    uint32_t num_irqs; // Number of IRQS Used
    int low_index_priority; // True of 0 index is highest priority
    void (*(*callbacks))(void*); // * to array of call back functions
    void** callback_params; // * to array of back parameters
} HAL_IRQ_CONFIG_T;

void hal_irq_config_init(HAL_IRQ_CONFIG_T* cfg, HAL_IRQ_REGS_T* base_addr,
    uint32_t num_irqs, void (*(*callback))(void*),
    void*(*callback_params), int priority);

void enable_global_irq();
void disable_global_irq();

/*
* Sets a Callback function for use with the default IRQ controller
*/
void hal_irq_callback(HAL_IRQ_CONFIG_T* cfg, uint32_t irq_num,
    void (*callback)(void*), void* obj);

/*
    Reads from the status register
*/
uint32_t hal_irq_status_read(HAL_IRQ_CONFIG_T* cfg);

/*
    Writes to the status register
*/
void hal_irq_status_write(HAL_IRQ_CONFIG_T* cfg, uint32_t status);

/*
    Sets the enable bit for irq n
*/
void hal_irq_n_enable(HAL_IRQ_CONFIG_T* cfg, uint32_t irq_n);

/*
    Clears the enable bit for irq n
*/
void hal_irq_n_disable(HAL_IRQ_CONFIG_T* cfg, uint32_t irq_n);

/*
    Triggers irq n
*/
void hal_irq_n_trigger(HAL_IRQ_CONFIG_T* cfg, uint32_t irq_n);

/*
    Triggers clears irq n
*/
void hal_irq_n_clear(HAL_IRQ_CONFIG_T* cfg, uint32_t irq_n);

/*
Returns the highest priority active irq
*/
int hal_irq_get_first_active(HAL_IRQ_CONFIG_T* cfg);

#endif
