#ifndef SYS_IO_H
#define SYS_IO_H

#include <stdint.h>

void sys_write32(uint32_t value, uint32_t addr);
void sys_write16(uint16_t value, uint32_t addr);
void sys_write8(uint8_t value, uint32_t addr);

uint32_t sys_read32(uint32_t addr);
uint16_t sys_read16(uint32_t addr);
uint8_t sys_read8(uint32_t addr);

#endif