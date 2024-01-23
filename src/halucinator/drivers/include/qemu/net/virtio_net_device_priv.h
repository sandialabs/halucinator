
#ifndef ETH_VIRTIO_PRIV_H_
#define ETH_VIRTIO_PRIV_H_

#include "OS_interface.h"

#define VIRTIO_MAGIC 0x74726976

#define DEV_DATA(dev) \
    ((struct eth_virtio_data*)(dev)->data)
#define DEV_CFG(dev) \
    ((const struct eth_virtio_config* const)(dev)->config)
/*
 *  Register mapping
 */
/* Registers for ethernet system, mac_base + offset */
#define REG_MAGIC ((DEV_CFG(dev)->base) + 0x000)
#define REG_VERSION ((DEV_CFG(dev)->base) + 0x004)
#define REG_DEVICE_ID ((DEV_CFG(dev)->base) + 0x008)
#define REG_VENDOR_ID ((DEV_CFG(dev)->base) + 0x00C)
#define REG_DEVICE_FEATURES ((DEV_CFG(dev)->base) + 0x010)
#define REG_DEVICE_FEATURES_SEL ((DEV_CFG(dev)->base) + 0x014)
#define REG_DRIVER_FEATURES ((DEV_CFG(dev)->base) + 0x020)
#define REG_DRIVER_FEATURES_SEL ((DEV_CFG(dev)->base) + 0x024)
#define REG_QUEUE_SEL ((DEV_CFG(dev)->base) + 0x030)
#define REG_QUEUE_NUM_MAX ((DEV_CFG(dev)->base) + 0x034)
#define REG_QUEUE_NUM ((DEV_CFG(dev)->base) + 0x038)
#define REG_QUEUE_READY ((DEV_CFG(dev)->base) + 0x044)
#define REG_QUEUE_NOTIFY ((DEV_CFG(dev)->base) + 0x050)
#define REG_IRQ_STATUS ((DEV_CFG(dev)->base) + 0x060)
#define REG_IRQ_ACK ((DEV_CFG(dev)->base) + 0x064)
#define REG_STATUS ((DEV_CFG(dev)->base) + 0x070)
#define REG_QUEUE_DESC_LOW ((DEV_CFG(dev)->base) + 0x080)
#define REG_QUEUE_DESC_HIGH ((DEV_CFG(dev)->base) + 0x084)
#define REG_QUEUE_AVAIL_LOW ((DEV_CFG(dev)->base) + 0x090)
#define REG_QUEUE_AVAIL_HIGH ((DEV_CFG(dev)->base) + 0x094)
#define REG_QUEUE_USED_LOW ((DEV_CFG(dev)->base) + 0x0A0)
#define REG_QUEUE_USED_HIGH ((DEV_CFG(dev)->base) + 0x0A4)
#define REG_CONFIG_GEN ((DEV_CFG(dev)->base) + 0x0FC)
#define REG_CONFIG ((DEV_CFG(dev)->base) + 0x100)

/* ETH MAC Receive Control bit fields set value */
#define BIT_DEV_STATUS_ACK 0x01
#define BIT_DEV_STATUS_DRV 0x02
#define BIT_DEV_STATUS_DRV_OK 0x04
#define BIT_DEV_STATUS_FEATURES_OK 0x08
#define BIT_DEV_STATUS_FAILED 128
#define BIT_DEV_STATUS_NEEDS_RESET 64

#define QUEUE_SIZE 1 //if change this need to change PAD in virtq so used is on 4 byte boundary

#if (__ARM_ARCH > 5)
#define DSB __asm__ volatile("dsb" :: \
                                 : "memory")
#else
#define DSB

#endif

/* le32 is used here for ids for padding reasons. */
struct virtq_net_used_elem {
    /* Index of start of used descriptor chain. */
    uint32_t id;
    /* Total length of the descriptor chain which was used (written to) */
    uint32_t len;
};

// Not using not defining the descriptors and rings
// Using common header so virtio devices can use diff
// sizes
typedef struct virtq_net_used {
#define VIRTQ_USED_F_NO_NOTIFY 1
    uint16_t flags;
    uint16_t idx;
    struct virtq_net_used_elem ring[QUEUE_SIZE];
    uint16_t avail_event; /* Only if VIRTIO_F_EVENT_IDX */
} virtq_net_used_t __attribute__((aligned(4)));

typedef struct virtq_net_avail {
#define VIRTQ_AVAIL_F_NO_INTERRUPT 1
    uint16_t flags;
    uint16_t idx;
    uint16_t ring[QUEUE_SIZE];
    uint16_t used_event; /* Only if VIRTIO_F_EVENT_IDX */
} virtq_net_avail_t __attribute__((aligned(2)));

typedef struct virtq_net_desc {
    /* Address (guest-physical). */
    uint64_t addr;
    /* Length. */
    uint32_t len;

/* This marks a buffer as continuing via the next field. */
#define VIRTQ_DESC_F_NEXT 1
/* This marks a buffer as device write-only (otherwise device read-only). */
#define VIRTQ_DESC_F_WRITE 2
/* This means the buffer contains a list of buffer descriptors. */
#define VIRTQ_DESC_F_INDIRECT 4
    /* The flags as indicated above. */
    uint16_t flags;
    /* Next field if flags & NEXT */
    uint16_t next;
} virtq_net_desc_t __attribute__((aligned(16)));

typedef struct virtq_net {
    // The actual descriptors (16 bytes each)
    struct virtq_net_desc desc[QUEUE_SIZE];
    struct virtq_net_avail avail; //Size (6+2*QUEUE_SIZE alignment)
    struct virtq_net_used used;
    uint16_t last_seen_used;
} virtq_net_t __attribute__((aligned(16)));

struct virtio_net_hdr {
#define VIRTIO_NET_HDR_F_NEEDS_CSUM 1
    uint8_t flags;
#define VIRTIO_NET_HDR_GSO_NONE 0
#define VIRTIO_NET_HDR_GSO_TCPV4 1
#define VIRTIO_NET_HDR_GSO_UDP 3
#define VIRTIO_NET_HDR_GSO_TCPV6 4
#define VIRTIO_NET_HDR_GSO_ECN 0x80
    uint8_t gso_type;
    uint16_t hdr_len;
    uint16_t gso_size;
    uint16_t csum_start;
    uint16_t csum_offset;
    //uint16_t num_buffers; /* Think Error in QEMU and this is ignored unless negotiate VIRTIO_NET_F_MRG_RXBUF */
    // See http://docs.oasis-open.org/virtio/virtio/v1.0/cs04/virtio-v1.0-cs04.html#x1-1560005
};

#define ETH_FRAME_SIZE 1526 //Ethernet frame + virtio-net header

struct eth_virtio_data {
    uint8_t mac_addr[6];
    OS_SEMA_T* tx_sema;
    virtq_net_t rx_queue;
    virtq_net_t tx_queue;
    int tx_err;
    uint32_t tx_word;
    int tx_pos;
#if defined(CONFIG_NET_STATISTICS_ETHERNET)
    struct net_stats_eth stats;
#endif
    //Hold the buffer used by virt queue descriptors
    uint8_t tx_buff[QUEUE_SIZE][ETH_FRAME_SIZE];
    uint8_t rx_buff[QUEUE_SIZE][ETH_FRAME_SIZE];
};

struct eth_virtio_config {
    uint32_t base;
    uint32_t irq_num;
};

struct eth_device {
    struct eth_virtio_data* data;
    struct eth_virtio_config* config;
};

#endif /* ETH_VIRTIO_PRIV_H_ */
