#ifndef ETH_VIRTIO_DEVICE_H_
#define ETH_VIRTIO_DEVICE_H_
#include "virtio_net_device_priv.h"
#include <stdint.h>

enum VIRTIO_NET_ISR_REASON { RING_UPDATE,
    CFG_CHANGE,
    UNKNOWN };

uint32_t virtio_net_ack_irq(struct eth_device* dev);

int virtio_net_init(const struct eth_device* dev, uint32_t baseaddr, uint32_t irq_num);

int virtio_net_enable_irq(struct eth_device* dev);

int virtio_net_disable_irq(struct eth_device* dev);

int virtio_net_discard_rx_data(const struct eth_device* dev);

int virtio_net_set_mac(struct eth_device* dev, uint8_t* mac_addr);

int virtio_net_get_mac(struct eth_device* dev, uint8_t* mac_addr);

int virtio_net_tx_frame(struct eth_device* dev, uint8_t* buf, int len);

int virtio_net_rx_frame(struct eth_device* dev, uint8_t* buf, int len);

void virtio_net_check_tx_done(const struct eth_device* dev);

int virtio_net_check_rx_data(const struct eth_device* dev);

#endif
