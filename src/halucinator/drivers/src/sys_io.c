
#include <log.h>
#include <sys_io.h>

void sys_write32(uint32_t value, uint32_t addr)
{
    *((volatile uint32_t*)(addr)) = value;
}

void sys_write16(uint16_t value, uint32_t addr)
{
    *((volatile uint16_t*)(addr)) = value;
}

void sys_write8(uint8_t value, uint32_t addr)
{
    *((volatile uint8_t*)(addr)) = value;
}

uint32_t sys_read32(uint32_t addr)
{
    return *((volatile uint32_t*)(addr));
}

uint16_t sys_read16(uint32_t addr)
{
    return *((volatile uint16_t*)(addr));
}

uint8_t sys_read8(uint32_t addr)
{
    return *((volatile uint8_t*)(addr));
}