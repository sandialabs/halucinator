/* Virtio Ethernet Controller
 *
 */

#include <log.h>
#include <qemu/net/virtio_net_device.h>
#include <string.h>
#include <sys_io.h>

#include <malloc.h>
#include <stdint.h>

/**
 * @Sets the Mac Address
 *
 * @param dev           Ethernet device structure
 * @param mac_addr      The mac address to set, must be array of 6 bytes
 * @return              Status
 */
int virtio_net_set_mac(struct eth_device* dev, uint8_t* mac_addr)
{

    LOG_DEBUG("In Setting MAC Addr:");
    for (int i = 0; i < 6; ++i) {
        LOG_DEBUG("%02x:", mac_addr[i]);
        sys_write8(mac_addr[i], REG_CONFIG + i);
    }
    LOG_DEBUG("\n");
    return 0;
}

/**
 * @brief Gets MAC address from the interface
 *
 * @param dev           Ethernet device structure
 * @param mac_addr      Buffer of len 6 in which the MAC address is written
 * @return              Status
 */
int virtio_net_get_mac(struct eth_device* dev, uint8_t* mac_addr)
{

    LOG_DEBUG("Getting MAC: ");
    for (int i = 0; i < 6; ++i) {
        mac_addr[i] = sys_read8(REG_CONFIG + i);
        LOG_DEBUG("%02x:", mac_addr[i]);
    }
    LOG_DEBUG("\n");
    return 0;
}

// static void eth_virtio_flush(const struct device *dev)
// {
//     // struct eth_virtio_runtime *dev_data = DEV_DATA(dev);

//     LOG_DEBUG("In eth_virtio_flush\n");
//     // if (dev_data->tx_pos != 0) {
//     // 	sys_write32(dev_data->tx_word, REG_MACDATA);
//     // 	dev_data->tx_pos = 0;
//     // 	dev_data->tx_word = 0U;
//     // }
// }

/**
 * @brief  Transmits a frame on the interface
 *
 * @param dev       Ethernet device structure for interface
 * @param frame     The ethernet frame
 * @param len       Lenght of frame to transmit
 * @return int      Status 0 ok, anything else error
 */

#define LOG_LEVEL INFO_LEVEL

int virtio_net_tx_frame(struct eth_device* dev, uint8_t* frame, int len)
{
    struct eth_virtio_data* dev_data = DEV_DATA(dev);
    struct net_buf* frag;
    uint16_t i;
    virtq_net_desc_t* vq_desc;
    virtq_net_avail_t* vq_avail;
    // virtq_net_used_t *vq_used;
    struct virtio_net_hdr* net_hdr;
    uint32_t idx;

    LOG_DEBUG("In eth_virtio_send\n");
    LOG_DEBUG("Getting tx_sem\n");

    OS_sema_take(dev_data->tx_sema, OS_SEMA_FOREVER);
    vq_desc = &(dev_data->tx_queue.desc[0]);
    vq_avail = &(dev_data->tx_queue.avail);

    if (len > ETH_FRAME_SIZE - sizeof(struct virtio_net_hdr)) {
        LOG_DEBUG("ERROR: ETH Data too long for TX Buffer %i", len);
        OS_sema_give(dev_data->tx_sema);
        return -1;
    }

    net_hdr = (struct virtio_net_hdr*)dev_data->tx_buff[0];
    net_hdr->flags = (VIRTIO_NET_HDR_F_NEEDS_CSUM);
    net_hdr->gso_type = VIRTIO_NET_HDR_GSO_NONE;
    net_hdr->hdr_len = 0; //Size of Ethernet header don't think it is used for ethernet
    net_hdr->gso_size = 0;
    net_hdr->csum_start = 0;
    net_hdr->csum_offset = len - 2;
    //net_hdr->num_buffers = 0;
    /* Copy the payload */
    idx = sizeof(struct virtio_net_hdr);
    for (i = 0; i < len; ++i) {
        dev_data->tx_buff[0][idx] = frame[i];
        ++idx;
    }

    len += sizeof(struct virtio_net_hdr);
    LOG_DEBUG("Sending Buffer (%i): ", len);
    // for(int i=0 ; i < len; i++){
    //     LOG_DEBUG("%02x", dev_data->tx_buff[0][i]);
    // }
    LOG_DEBUG("\n");
    vq_desc->addr = (uintptr_t) & (dev_data->tx_buff[0][0]);
    LOG_DEBUG("vq_desc->addr 0x%016llx\n", vq_desc->addr);

    vq_desc->len = len;
    vq_desc->next = 0; //Packet fragmenting not allowed
    vq_desc->flags = 0;

    vq_avail->flags = 0;
    vq_avail->ring[0] = 0;
    vq_avail->used_event = 0;

    LOG_DEBUG("TX tx_queue.used.idx = %i\n", dev_data->tx_queue.used.idx);
    LOG_DEBUG("TX tx_queue.last_seen = %i\n", dev_data->tx_queue.last_seen_used);

    //Memory Barrier
    DSB;
    //Notifies Device data is available and may start using it
    vq_avail->idx += 1;

    sys_write32(1, REG_QUEUE_SEL);
    sys_write32(1, REG_QUEUE_NOTIFY);
    LOG_DEBUG("pkt sent %p len %d\n", frame, len);

    return 0;
}

static void eth_return_desc_to_queue(virtq_net_t* vq, uint16_t idx)
{

    LOG_DEBUG("Giving VQ Desc to device 0x%08x %i\n", vq, idx);
    vq->desc[idx].flags = VIRTQ_DESC_F_WRITE; //Device write_only, no next, not indirect
    vq->desc[idx].next = 0;

    vq->avail.flags = 0;
    vq->avail.ring[vq->avail.idx % QUEUE_SIZE] = idx;
    vq->avail.used_event = 0;
    DSB;
    vq->avail.idx += 1;
}

static int _net_virtio_rx_frame(const struct eth_device* dev,
    uint8_t* buf,
    int max_len,
    struct virtq_net_used_elem* elem)
{
    struct eth_virtio_data* dev_data = DEV_DATA(dev);
    virtq_net_t* rx_q = &(dev_data->rx_queue);
    int frame_len;
    int frame_idx;

    uint8_t* data;
    struct virtio_net_hdr net_hdr;
    uint32_t bytes_to_read;
    uint16_t next;
    uint16_t curr_desc_idx = elem->id;

    LOG_DEBUG("In eth_virtio_rx_pkt\n");

    if (curr_desc_idx > QUEUE_SIZE) {
        LOG_ERROR("Used QUEUE number too large\n");
        goto error;
    }
    frame_len = elem->len;

    if (frame_len < sizeof(struct virtio_net_hdr)) {
        LOG_ERROR("Frame does not have net header\n");
        goto error;
    }

    int curr_desc_buff_idx = 0;

    int bytes_read = 0;
    data = (uint8_t*)((uint32_t)(rx_q->desc[curr_desc_idx].addr & 0xFFFFFFFF));
    /* Read the header */
    LOG_DEBUG("HDR Len %i\n", sizeof(struct virtio_net_hdr));
    for (bytes_read = 0; bytes_read < sizeof(struct virtio_net_hdr); ++bytes_read) {
        if (curr_desc_buff_idx >= rx_q->desc[curr_desc_idx].len) {
            if (rx_q->desc[curr_desc_idx].flags & VIRTQ_DESC_F_NEXT) {
                LOG_DEBUG("Getting next descriptor\n");
                next = rx_q->desc[curr_desc_idx].next;
                eth_return_desc_to_queue(rx_q, curr_desc_idx);
                curr_desc_idx = next;
                curr_desc_buff_idx = 0;
                data = (uint8_t*)((uint32_t)(rx_q->desc[curr_desc_idx].addr & 0xFFFFFFFF));
            } else {
                LOG_ERROR("Need Next in virtio descriptor table, but on present");
                goto error;
            }
        }
        ((uint8_t*)(&net_hdr))[bytes_read] = data[curr_desc_buff_idx];
        ++curr_desc_buff_idx;
    }

#if LOG_LEVEL >= DEBUG_LEVEL
    LOG_DEBUG("RX Buff: ");
    for (int i = 0; i < frame_len; i++) {
        printf("%02x:", dev_data->rx_buff[0][i]);
    }
    LOG_DEBUG("\n");
    LOG_DEBUG("Bytes Read %i\n", bytes_read);

    LOG_DEBUG("Header: ");
    for (int i = 0; i < sizeof(struct virtio_net_hdr); i++) {
        printf("%02x:", ((uint8_t*)(&net_hdr))[i]);
    }
    LOG_DEBUG("\n");

    LOG_DEBUG("net_hdr: flags:0x%02x, hdr_len:0x%02x csum_start:%i, csum_offset %i\n",
        net_hdr.flags, net_hdr.hdr_len, net_hdr.csum_start, net_hdr.csum_offset);
#endif

    // Read Frame
    frame_idx = 0;
    while (bytes_read < frame_len) {
        if (curr_desc_buff_idx >= rx_q->desc[curr_desc_idx].len) {
            if (rx_q->desc[curr_desc_idx].flags & VIRTQ_DESC_F_NEXT) {
                LOG_DEBUG("Getting next descriptor\n");
                next = rx_q->desc[curr_desc_idx].next;
                eth_return_desc_to_queue(rx_q, curr_desc_idx);
                curr_desc_idx = next;
                curr_desc_buff_idx = 0;
                data = (uint8_t*)((uint32_t)(rx_q->desc[curr_desc_idx].addr & 0xFFFFFFFF));
            } else {
                LOG_ERROR("Need next in virtio descriptor table, but none present");
                goto error;
            }
        }

        bytes_to_read = frame_len - bytes_read;

        if (bytes_to_read > rx_q->desc[curr_desc_idx].len - curr_desc_buff_idx) {
            // Only some of the frame is in this QUEUE
            bytes_to_read = rx_q->desc[curr_desc_idx].len - curr_desc_buff_idx;
        }

        if (frame_idx + bytes_to_read < max_len) {
            memcpy(&buf[frame_idx], &data[curr_desc_buff_idx], bytes_to_read);
        } else {
            LOG_ERROR("Buffer too small\n");
            goto error;
        }
        curr_desc_buff_idx += bytes_to_read;
        bytes_read += bytes_to_read;
        frame_idx += bytes_to_read;
    }

    eth_return_desc_to_queue(rx_q, curr_desc_idx);

#if LOG_LEVEL >= DEBUG_LEVEL
    LOG_DEBUG("Buffer: ");
    for (int i = 0; i < frame_len - sizeof(struct virtio_net_hdr); ++i) {
        printf("%02x:", buf[i]);
    }
    printf("\n");
#endif
    return frame_len - sizeof(struct virtio_net_hdr);

error:
    eth_return_desc_to_queue(rx_q, curr_desc_idx);
    return -1;
}

int virtio_net_rx_frame(struct eth_device* dev, uint8_t* buf, int len)
{
    //Will only work with a single frame.
    struct eth_virtio_data* dev_data = DEV_DATA(dev);
    int num_bytes_rx;

    LOG_DEBUG("In net_virtio_rx_frame\n");
    virtq_net_t* rx_queue = &(dev_data->rx_queue);

    LOG_DEBUG("RX USED Flags 0x%0x, IDX: %i, Avail 0x%0x\n", rx_queue->used.flags,
        rx_queue->used.idx,
        rx_queue->used.avail_event);
    LOG_DEBUG("RX Ring %i %i\n", rx_queue->used.ring[0].id,
        rx_queue->used.ring[0].len);

    OS_irq_lock();
    LOG_DEBUG("FW: In Lock taken\n");

    LOG_DEBUG("FW: Processing\n");
    struct virtq_net_used_elem* e = &rx_queue->used.ring[rx_queue->last_seen_used % QUEUE_SIZE];
    LOG_DEBUG("FW: processing packet\n");
    num_bytes_rx = _net_virtio_rx_frame(dev, buf, len, e);
    rx_queue->last_seen_used++;
    OS_irq_unlock();
    return num_bytes_rx;
}

int virtio_net_discard_rx_data(const struct eth_device* dev)
{
    struct eth_virtio_data* dev_data = DEV_DATA(dev);
    int num_bytes_rx;

    LOG_DEBUG("In virtio discard_rx_data\n");
    virtq_net_t* rx_queue = &(dev_data->rx_queue);

    eth_return_desc_to_queue(rx_queue, rx_queue->last_seen_used);
    rx_queue->last_seen_used++;
}

int virtio_net_check_rx_data(const struct eth_device* dev)
{

    int has_data = 0;
    uint32_t lock;
    struct eth_virtio_data* dev_data = DEV_DATA(dev);
    virtq_net_t* rx_queue = &(dev_data->rx_queue);

    LOG_DEBUG("RX USED Flags 0x%0x, IDX: %i, Avail 0x%0x\n", rx_queue->used.flags,
        rx_queue->used.idx,
        rx_queue->used.avail_event);
    LOG_DEBUG("RX Ring %i %i\n", rx_queue->used.ring[0].id,
        rx_queue->used.ring[0].len);

    lock = OS_irq_lock();
    if (rx_queue->last_seen_used <= rx_queue->used.idx) {
        has_data = 1;
    }
    OS_irq_unlock(lock);
    return has_data;
}

void virtio_net_check_tx_done(const struct eth_device* dev)
{
    // struct eth_virtio_runtime *dev_data = DEV_DATA(dev);
    struct eth_virtio_data* dev_data = DEV_DATA(dev);
    LOG_DEBUG("In eth_virtio_check_tx_done\n");
    virtq_net_t* tx_queue = &(dev_data->tx_queue);
    //TODO check used ring is not empty if not empty
    LOG_DEBUG("ISR tx_queue.used.idx = %i\n", tx_queue->used.idx);
    LOG_DEBUG("ISR tx_queue.last_seen = %i\n", tx_queue->last_seen_used);
    if (tx_queue->used.idx != tx_queue->last_seen_used) {
        LOG_DEBUG("TX Done\n");
        tx_queue->last_seen_used++;
        OS_sema_give(dev_data->tx_sema);
    }
}

// static void eth_virtio_isr(const struct device *dev)
// {
//     struct eth_virtio_runtime *dev_data = DEV_DATA(dev);
//     // int isr_val = sys_read32(REG_MACRIS);
//     uint32_t status;

//     virtq_net_t * rx_queue;
//     virtq_net_t * tx_queue;
//     rx_queue = &(dev_data->rx_queue);
//     tx_queue = &(dev_data->tx_queue);

//     LOG_DEBUG("In eth_virtio_isr\n");

//     status = sys_read32(REG_IRQ_STATUS);
//     LOG_DEBUG("IRQ_STATUS 0x%08x\n", status);
//     if (status & 0x01){ // Ring update
//         eth_virtio_check_tx_done(dev);
//         eth_virtio_rx(dev);
//     }
//     if(status & 0x2){ //Configuration change
//         LOG_WRN("Virtio-net configuration changed");
//     }
//     sys_write32(status, REG_IRQ_ACK);
//     // irq_unlock(lock);
// }

uint32_t virtio_net_ack_irq(struct eth_device* dev)
{
    uint32_t status;
    status = sys_read32(REG_IRQ_STATUS);
    sys_write32(status, REG_IRQ_ACK);
    return status;
}

/**
 * @brief           Internal Device Initialization
 *
 * @param dev       Ethernet device structure
 * @return int      Status 0 OK, anything else error
 */
static int _virtio_net_device_init(const struct eth_device* dev)
{
    uint32_t value;
    uint32_t dev_features_low, dev_features_high;
    struct eth_virtio_data* dev_data = DEV_DATA(dev);

    LOG_DEBUG("In eth_virtio_dev_init\n");

    value = sys_read32(REG_MAGIC);
    LOG_DEBUG("Magic is 0x%08x\n", value);
    if (value != VIRTIO_MAGIC) {
        LOG_ERROR("Magic Value not found for VirtIO");
        return -1;
    }

    LOG_DEBUG("Version %i\n", sys_read32(REG_VERSION));
    LOG_DEBUG("Device ID %i\n", sys_read32(REG_DEVICE_ID));
    LOG_DEBUG("Vendor ID 0x%08x\n", sys_read32(REG_VENDOR_ID));
    // Check versions
    value = sys_read32(REG_VERSION);
    if (value != 0x2) {
        LOG_ERROR("Unsupported Driver Version\n");
        return -1;
    }

    value = sys_read32(REG_DEVICE_ID);
    if (value != 0x1) {
        LOG_ERROR("Not a Virtio Network Device\n");
        return -1;
    }

    // Reset Device
    value = sys_read32(REG_STATUS);
    LOG_DEBUG("Dev Status 0x%08x\n", value);
    LOG_DEBUG("Reseting Device\n");
    sys_write32(0, REG_STATUS);
    LOG_DEBUG("Done\n");
    // Acknowledge the Device

    value = sys_read32(REG_STATUS);
    LOG_DEBUG("Acknowledging the Device 0x%08x\n", value);
    value = value | BIT_DEV_STATUS_ACK;
    sys_write32(value, REG_STATUS);
    LOG_DEBUG("Done\n");

    //Set the Driver Status bit
    value = sys_read32(REG_STATUS);
    LOG_DEBUG("Setting Driver Status 0x%08x\n", value);
    value = value | BIT_DEV_STATUS_DRV;
    sys_write32(value, REG_STATUS);
    LOG_DEBUG("Done\n");

    // Read feature bits
    value = sys_read32(REG_STATUS);
    LOG_DEBUG("Negotiating Features Status:0x%08x\n", value);
    sys_write32(0, REG_DEVICE_FEATURES_SEL);
    LOG_DEBUG("Features Sel Written\n");
    dev_features_low = sys_read32(REG_DEVICE_FEATURES);
    LOG_DEBUG("Device Features L:0x%08x\n", dev_features_low);
    sys_write32(1, REG_DEVICE_FEATURES_SEL);
    dev_features_high = sys_read32(REG_DEVICE_FEATURES);
    LOG_DEBUG("Device Features H:0x%08x\n", dev_features_high);

    //Write supported feature bits
    // Bit 0 let device handle checksum
    //
    value = 0x11; // Let device handle checksum and use its MAC
    sys_write32(0, REG_DRIVER_FEATURES_SEL);
    sys_write32(value, REG_DRIVER_FEATURES);
    sys_write32(1, REG_DRIVER_FEATURES_SEL);
    sys_write32(0, REG_DRIVER_FEATURES);
    sys_write32(1, REG_QUEUE_READY);

    //Set FEATURES_OK
    sys_write32(BIT_DEV_STATUS_FEATURES_OK, REG_STATUS);

    //Re-read DEV_STATUS FEATURES_OK to ensure still set
    //(otherwise device doesn't support our feature set)

    value = sys_read32(REG_STATUS);
    LOG_DEBUG("Dev Status 0x%08x\n", value);
    if (!(value & BIT_DEV_STATUS_FEATURES_OK)) {
        LOG_ERROR("Virtio-net doesn't support our feature set\n");
        return -1;
    }

    // Perform device specific init, setup/discover virt queues

    // Setup RX VirtQ
    dev_data->rx_queue.avail.idx = 0;
    dev_data->rx_queue.last_seen_used = 1;
    for (int i = 0; i < QUEUE_SIZE; i++) {
        dev_data->rx_queue.desc[i].addr = (uint64_t)(0x0 | (uint32_t)dev_data->rx_buff[i]);
        dev_data->rx_queue.desc[i].len = ETH_FRAME_SIZE;
        dev_data->rx_queue.desc[i].flags = VIRTQ_DESC_F_WRITE; //Device write_only, no next, not indirect
        dev_data->rx_queue.desc[i].next = 0;

        dev_data->rx_queue.avail.flags = 0;
        dev_data->rx_queue.avail.idx += 1;
        dev_data->rx_queue.avail.ring[i] = i;
        dev_data->rx_queue.avail.used_event = 0;
    }
    sys_write32(0, REG_QUEUE_SEL);
    sys_write32(QUEUE_SIZE, REG_QUEUE_NUM);
    sys_write32((uint32_t)(&(dev_data->rx_queue.desc)), REG_QUEUE_DESC_LOW);
    sys_write32(0, REG_QUEUE_DESC_HIGH);
    sys_write32((uint32_t)(&(dev_data->rx_queue.avail)), REG_QUEUE_AVAIL_LOW);
    sys_write32(0, REG_QUEUE_AVAIL_HIGH);
    sys_write32((uint32_t)(&(dev_data->rx_queue.used)), REG_QUEUE_USED_LOW);
    sys_write32(0, REG_QUEUE_USED_HIGH);
    sys_write32(1, REG_QUEUE_READY);

    // Setup TX VirtQ
    dev_data->tx_queue.avail.idx = 0;
    for (int i = 0; i < QUEUE_SIZE; i++) {
        dev_data->tx_queue.desc[i].addr = (uint64_t)(0x0) | (uint32_t)(dev_data->tx_buff[i]);
        dev_data->tx_queue.desc[i].len = ETH_FRAME_SIZE;
        dev_data->tx_queue.desc[i].flags = 0; //Device read_only
        dev_data->tx_queue.desc[i].next = 0;
    }
    sys_write32(1, REG_QUEUE_SEL);
    sys_write32(QUEUE_SIZE, REG_QUEUE_NUM);
    sys_write32((uint32_t)(&(dev_data->tx_queue.desc)), REG_QUEUE_DESC_LOW);
    sys_write32(0x0, REG_QUEUE_DESC_HIGH);
    sys_write32((uint32_t)(&(dev_data->tx_queue.avail)), REG_QUEUE_AVAIL_LOW);
    sys_write32(0x0, REG_QUEUE_AVAIL_HIGH);
    sys_write32((uint32_t)(&(dev_data->tx_queue.used)), REG_QUEUE_USED_LOW);
    sys_write32(0x0, REG_QUEUE_USED_HIGH);
    sys_write32(1, REG_QUEUE_READY);
    // Setup Virt Queues
    // Set DRIVER_OK

    value = sys_read32(REG_STATUS);
    sys_write32(value | BIT_DEV_STATUS_DRV_OK, REG_STATUS);

    LOG_DEBUG("Driver Init Done\n");
    return 0;
}

/**
 * @brief   Initializes the virtio network device
 *
 * @param dev           Ethernet device structure
 * @param baseaddr      Base address for the virtio device
 * @param irq_num       IRQ number for the interface
 * @return int
 */
int virtio_net_init(const struct eth_device* dev, uint32_t baseaddr, uint32_t irq_num)
{

    dev->config->base = baseaddr;
    dev->config->irq_num = irq_num;
    return _virtio_net_device_init(dev);
}
