#ifndef __ETHER_END_H__
#define __ETHER_END_H__

#include <stdint.h>
// #include <qemu/irq/halucinator_irq.h>
#include <qemu/net/virtio_net_device.h>

#define END_OBJ_BASEREG_OFFSET 0x2c8
#define END_OBJ_IRQ_NUM 0x2d0

typedef struct eth_map {
    struct eth_device* dev;
    uint32_t reg_addr;
} ETHERNET_INTERFACE_MAP_T;

// void vxworks_ethernet_dev_init(HAL_IRQ_CONFIG_T * irq_cfg);
#endif