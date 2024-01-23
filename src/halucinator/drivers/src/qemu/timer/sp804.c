#include <halucinator.h>
#include <qemu/timer/sp804.h>

#define LOG_LEVEL INFO_LEVEL

void sp804_enable(volatile Timer_Sp804_T* timer)
{
    LOG_DEBUG("In %s\n", __PRETTY_FUNCTION__);
    timer->ctrl |= SP804_TIMER_EN;
}

void sp804_disable(volatile Timer_Sp804_T* timer)
{
    LOG_DEBUG("In %s\n", __PRETTY_FUNCTION__);
    timer->ctrl = timer->ctrl & (~SP804_TIMER_EN);
}

uint32_t sp804_get_timer_value(volatile Timer_Sp804_T* timer)
{
    LOG_DEBUG("In %s\n", __PRETTY_FUNCTION__);
    return timer->value;
}

void sp804_set_prescaler(volatile Timer_Sp804_T* timer, uint32_t prescaler)
{
    LOG_DEBUG("In %s\n", __PRETTY_FUNCTION__);
    int timer_enabled = 0;
    if (timer->ctrl & SP804_TIMER_EN) {
        timer_enabled = 1;
        sp804_disable(timer);
    }
    switch (prescaler) {
    case 0:
    case 1:
    case 2:
        timer->ctrl = (timer->ctrl & (~SP804_TIMER_PRE)) | prescaler << 2;
        break;
    }

    if (timer_enabled) {
        sp804_enable(timer);
    }
}

void sp804_set_to_hertz(volatile Timer_Sp804_T* timer, int ticks_per_sec)
{
    LOG_DEBUG("In %s\n", __PRETTY_FUNCTION__);
    sp804_set_prescaler(timer, 1);
    LOG_INFO("Desired Ticks %i\n", ticks_per_sec);
    int tick_count = 0x2000;
    sp804_set_periodic(timer, tick_count);
}

void sp804_set_periodic(volatile Timer_Sp804_T* timer, uint32_t value)
{
    LOG_DEBUG("In %s\n", __PRETTY_FUNCTION__);
    int timer_enabled = 0;
    LOG_DEBUG("Timer CTRL 0x%02x\n", timer->ctrl);
    if (timer->ctrl & SP804_TIMER_EN) {
        timer_enabled = 1;
        sp804_disable(timer);
    }
    timer->ctrl |= SP804_TIMER_MODE; // Make periodic
    timer->ctrl |= SP804_TIMER_SIZE; // Make 32 bit counter
    timer->ctrl &= (~SP804_TIMER_ONE_SHOT); // Make Periodic bit counter
    timer->load = value;
    timer->BGLoad = value;

    if (timer_enabled) {
        LOG_DEBUG("In %s Enabling Timer\n", __PRETTY_FUNCTION__);
        sp804_enable(timer);
    }
}

void sp804_enable_irq(volatile Timer_Sp804_T* timer)
{
    LOG_DEBUG("In %s\n", __PRETTY_FUNCTION__);
    timer->ctrl |= SP804_TIMER_INT_ENABLE;
}

void sp804_disable_irq(volatile Timer_Sp804_T* timer)
{
    LOG_DEBUG("In %s\n", __PRETTY_FUNCTION__);
    timer->ctrl &= ~SP804_TIMER_INT_ENABLE;
}

void sp804_clear_irq(volatile Timer_Sp804_T* timer)
{
    LOG_DEBUG("In %s\n", __PRETTY_FUNCTION__);
    timer->int_clear |= 0xff;
}

uint32_t sp804_get_irq_status(volatile Timer_Sp804_T* timer)
{
    LOG_DEBUG("In %s\n", __PRETTY_FUNCTION__);
    return timer->MIS & 0x01;
}