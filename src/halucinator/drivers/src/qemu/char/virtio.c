#include <qemu/char/virtio.h>
#include <qemu/char/virtio_queue.h>
#include <stdio.h>

struct virtio_features universal_features[] = {
    //Feature bits 24 to 32 reserved for extensions to the queue and feature negotiation mechanisms
    { "VIRTIO_F_NOTIFY_ON_EMPTY", 1 << 24, false,
        "If this feature has been negotiated by driver, the device MUST"
        " issue an interrupt if the device runs out of available descriptors"
        " on a virtqueue, even though interrupts are suppressed using the "
        "VIRTQ_AVAIL_F_NO_INTERRUPT flag or the used_event field." },
    { "VIRTIO_F_ANY_LAYOUT", 1 << 27, false,
        "This feature indicates that the device accepts arbitrary descriptor"
        " layouts, as described in Section 2.4.4.3 Legacy Interface: Message Framing" },
    { "VIRTIO_F_RING_INDIRECT_DESC", 1 << 28, false,
        "Negotiating this feature indicates that the driver can use"
        " descriptors with the VIRTQ_DESC_F_INDIRECT flag set, as"
        " described in 2.4.5.3 Indirect Descriptors." },
    { "VIRTIO_F_RING_EVENT_IDX", 1 << 29, false,
        "This feature enables the used_event and the avail_event fields"
        " as described in 2.4.7 and 2.4.8." },
    { "UNUSED", 1 << 30, false,
        "Bit 30 is used by qemu's implementation to check for experimental early "
        "versions of virtio which did not perform correct feature negotiation, "
        "and SHOULD NOT be negotiated." },
    // This is hardcoded in hex because shifting << 32 gives compiler warning, but it is 1<<32
    { "VIRTIO_F_VERSION_1", 0x80000000, false,
        "This indicates compliance with this specification, giving a"
        " simple way to detect legacy devices or drivers." },
};

const int universal_features_sizeof = sizeof(universal_features);
const int universal_features_first_sizeof = sizeof(universal_features[0]);
// debug print the virtio_device
void print_v1_info(volatile virtio_device* dev)
{
    uint32_t magic_value_int = volatile_read32(MAGICVALUE(dev->regs));
    char magic_value_str[5];
    magic_value_str[0] = (char)(magic_value_int);
    magic_value_str[1] = (char)(magic_value_int >> 8);
    magic_value_str[2] = (char)(magic_value_int >> 16);
    magic_value_str[3] = (char)(magic_value_int >> 24);
    magic_value_str[4] = '\0';
    printf("MagicValue: 0x%x = ascii value: %s\n", magic_value_int, magic_value_str);
    printf("Version: 0x%x\n", volatile_read32(VERSION(dev->regs)));
    printf("DeviceID: 0x%x\n", volatile_read32(DEVICEID(dev->regs)));
    uint32_t vendor_id_int = volatile_read32(VENDORID(dev->regs));
    char vendor_id_str[5];
    vendor_id_str[0] = (char)(vendor_id_int);
    vendor_id_str[1] = (char)(vendor_id_int >> 8);
    vendor_id_str[2] = (char)(vendor_id_int >> 16);
    vendor_id_str[3] = (char)(vendor_id_int >> 24);
    vendor_id_str[4] = '\0';
    printf("VendorID: 0x%x = ascii value: %s\n", vendor_id_int, vendor_id_str);
    printf("DeviceFeatures: 0x%x\n", volatile_read32(DEVICEFEATURES(dev->regs)));
    printf("QueueNumMax: 0x%x\n", volatile_read32(QUEUENUMMAX(dev->regs)));
    printf("QueueReady: 0x%x\n", volatile_read32(QUEUEREADY(dev->regs)));
    printf("InterruptStatus: 0x%x\n", volatile_read32(INTERRUPTSTATUS(dev->regs)));
    printf("Status: 0x%x\n", volatile_read32(STATUS(dev->regs)));
    printf("ConfigGeneration: 0x%x\n", volatile_read32(CONFIGGENERATION(dev->regs)));
}

volatile uint32_t volatile_read32(volatile uint32_t* base_addr)
{
    // printf("Reading from %#010x: %#010x\n", base_addr, *base_addr);
    return *(base_addr);
}

void volatile_write32(volatile uint32_t* address, uint32_t value)
{
    // printf("Writing %#010x to address %#010x\n", value, address);
    *address = value;
}

int virtio_check_features(uint32_t* device, uint32_t* request, struct virtio_features* caps, uint32_t n)
{
    uint32_t i;
    for (i = 0; i < n; i++) {
        if (*device & caps[i].bit) {
            if (caps[i].support) {
                *request |= caps[i].bit;
                printf("QEMU Virtio supports our driver supported option %s (%s)\n\n",
                    caps[i].name, caps[i].help);
            } else {
                printf("QEMU Virtio supports unsupported driver option %s (%s)\n\n",
                    caps[i].name, caps[i].help);
            }
        }
        *device &= ~caps[i].bit;
    }
}

uint32_t virtio_mmio_init(volatile virtio_device* dev)
{
    //Before we get here we should have already checked the magic value
    //Should also have checked the version and the deviceID. All should be valid
    // 3.1.1 Driver Requirements: Device Initialization
    // The driver MUST follow this sequence to initialize a device:
    uint32_t status = 0;

    // Reset the device.
    volatile_write32(STATUS(dev->regs), status);
    // For debug printing
    status = volatile_read32(STATUS(dev->regs));
    printf("New Device Status: %#010x\n", status);
    DSB;
    // Set the ACKNOWLEDGE status bit: the guest OS has notice the device.
    status |= VIRTIO_STATUS_ACKNOWLEDGE;
    printf("status to write: %d\n", status);
    volatile_write32(STATUS(dev->regs), status);
    status = volatile_read32(STATUS(dev->regs));
    printf("New Device Status: %#010x\n", status);
    DSB;
    // Set the DRIVER status bit: the guest OS knows how to drive the device.
    status |= VIRTIO_STATUS_DRIVER;
    printf("status to write: %d\n", status);
    volatile_write32(STATUS(dev->regs), status);
    status = volatile_read32(STATUS(dev->regs));
    printf("New Device Status: %#010x\n", status);
    DSB;

    // We continue with device specific initialization after this, with features
    // negotiated by the host/guest for the device.
    return VIRT_OK;
}

static uint32_t virtio_mmio_get_status(volatile virtio_device* dev)
{
    return volatile_read32(STATUS(dev->regs));
}

uint32_t virtio_mmio_select_features(volatile virtio_device* dev, uint32_t feat)
{
    uint32_t cap = volatile_read32(DEVICEFEATURES(dev->regs));

    if ((cap & feat) != feat) {
        printf("Error selecting feature %x\n", feat);
        return -VIRT_ERROR;
    }
    volatile_write32(DEVICEFEATURES(dev->regs), feat);

    //status is at same offset, don't need to check version
    uint32_t status = volatile_read32(STATUS(dev->regs)) | VIRTIO_STATUS_FEATURES_OK;

    volatile_write32(DEVICEFEATURES(dev->regs), status);
    if ((virtio_mmio_get_status(dev) & VIRTIO_STATUS_FAILED) == VIRTIO_STATUS_FAILED) {
        return -VIRT_ERROR;
    }

    return VIRT_OK;
}

uint32_t virtio_mmio_init_queue(volatile virtio_device* dev,
    volatile struct virtq* q,
    uint32_t queue_index,
    uint32_t queue_sz)
{
    q->queue_index = queue_index;
    q->last_seen_used = 1;
    //QueueSel at same offset, don't need to check version
    // Select the queue writing its index (first queue is 0) to QueueSel.
    volatile_write32(QUEUESEL(dev->regs), queue_index);

    // Check if the queue is not already in use: read QueueReady,
    // and expect a returned value of zero (0x0).
    if (volatile_read32(QUEUEREADY(dev->regs)) != 0) {
        printf("Queue is already in use, cannot reinit\n");
        printf("In virtio_mmio_init_queue function\n");
        return VIRT_ERROR;
    }

    uint32_t q_size = volatile_read32(QUEUENUMMAX(dev->regs));

    if (q_size < queue_sz) {
        return VIRT_ERROR;
    }
    // Allocate and zero the queue memory, making sure the memory is
    // physically contiguous.
    // (This was already done by creating device and virtio_init_queue)

    // Notify the device about the queue size by writing the size to QueueNum.
    volatile_write32(QUEUENUM(dev->regs), queue_sz);

    printf("Virtio Queue %u init: %08x, %08x, %08x\n",
        q->queue_index, (uint32_t)q->desc,
        (uint32_t)q->avail, (uint32_t)q->used);

    // Write physical addresses of the queue’s Descriptor Area,
    // Driver Area and Device Area to (respectively) the QueueDescLow/QueueDescHigh,
    // QueueDriverLow/QueueDriverHigh and QueueDeviceLow/QueueDeviceHigh
    // register pairs.
    volatile_write32(QUEUESEL(dev->regs), queue_index);
    DSB;
    volatile_write32(QUEUENUM(dev->regs), queue_sz);
    volatile_write32(QUEUEDESCLOW(dev->regs), (uint32_t)q->desc);
    volatile_write32(QUEUEDESCHIGH(dev->regs), 0);
    volatile_write32(QUEUEAVAILLOW(dev->regs), (uint32_t)q->avail);
    volatile_write32(QUEUEAVAILHIGH(dev->regs), 0);
    volatile_write32(QUEUEUSEDLOW(dev->regs), (uint32_t)q->used);
    volatile_write32(QUEUEUSEDHIGH(dev->regs), 0);
    DSB;
    // Write 0x1 to QueueReady.
    volatile_write32(QUEUEREADY(dev->regs), 0x1);

    return VIRT_OK;
}

uint32_t virtio_mmio_driver_ok(volatile virtio_device* dev)
{
    uint32_t status = volatile_read32(STATUS(dev->regs));
    status |= VIRTIO_STATUS_DRIVER_OK;
    volatile_write32(STATUS(dev->regs), status);
    return VIRT_OK;
}

uint32_t virtio_mmio_write(volatile virtio_device* dev,
    volatile struct virtq* q,
    uint8_t* buf,
    uint32_t len)
{
    printf("\n\n\nWriting to mmio. Device %#010x, with buffer: '%.*s'\n\n\n\n", dev, len, buf);
    uint16_t idx = (q->avail->idx % q->num);
    uint32_t bytes_to_transfer = len;
    uint32_t pos = 0;
    uint32_t descriptor_count = 0;
    uint32_t chunk;

    while (bytes_to_transfer) {
        if (bytes_to_transfer > PG_SIZE)
            chunk = PG_SIZE;
        else
            chunk = bytes_to_transfer;

        bytes_to_transfer -= chunk;

        q->desc[idx].addr = (uint32_t)(uintptr_t)&buf[pos];
        q->desc[idx].len = chunk;

        if (bytes_to_transfer == 0) {
            q->desc[idx].flags = 0;
            q->desc[idx].next = 0;
        } else {
            q->desc[idx].flags = VIRTQ_DESC_F_NEXT;
            q->desc[idx].next = (idx + 1) % q->num;
        }
        idx = ((idx + 1) % q->num);
        pos += chunk;
        descriptor_count++;
    }

    q->avail->ring[idx] = idx;
    //data synch variable
    //dsb asm instruction
    DSB;
    q->avail->idx += descriptor_count;
    volatile_write32(QUEUENOTIFY(dev->regs), q->queue_index);
    DSB;
    return len;
}

uint32_t virtio_mmio_read_one(volatile virtio_device* dev,
    volatile struct virtq* q,
    uint8_t* buf,
    uint32_t len)
{
    uint16_t idx = (q->avail->idx % q->num);
    uint16_t idx_old = idx;
    uint32_t bytes_to_transfer = len;
    uint32_t pos = 0;
    uint32_t descriptor_count = 0;
    uint32_t chunk;
    printf("idx: %d\nidx_old: %d\nbytes_to_transfer: %d\npos: %d\n",
        idx, idx_old, bytes_to_transfer, pos);
    // print_v1_info(dev);
    /// note here that we are saying no to chaining descriptors by setting next to 0
    while (bytes_to_transfer) {
        if (bytes_to_transfer > PG_SIZE)
            chunk = PG_SIZE;
        else
            chunk = bytes_to_transfer;
        bytes_to_transfer -= chunk;
        printf("Addr 0x%x", (uint32_t)&buf[pos]);
        q->desc[idx].addr = ((uint32_t)&buf[pos]);
        q->desc[idx].len = chunk;
        q->desc[idx].flags = VIRTQ_DESC_F_WRITE;
        q->desc[idx].next = 0;
        DSB;
        q->avail->ring[idx] = idx;
        q->avail->idx += 1;

        idx = ((idx + 1) % q->num);
        pos += chunk;
        descriptor_count++;
        DSB;
        //offset for QueueNotify is same for all versions, no version check
        volatile_write32(QUEUENOTIFY(dev->regs), q->queue_index);
    }

    //Block until data available
    while (q->last_seen_used != q->used->idx) {
        //printf("Last Seen Used %i, Last_Used %i\n", q->last_seen_used, q->used->idx);
        ; //printf(".");
    }

    printf("Last Seen Used %i, Last_Used %i\n", q->last_seen_used, q->used->idx);
    //Read as many as possible breaking when no data is available
    // while (true) {
    //     printf("\nLast Seen Used %i, Last_Used %i\n", q->last_seen_used, q->used->idx);
    //     if (q->last_seen_used != q->used->idx) {
    //         DSB;
    //         if (q->last_seen_used != q->used->idx){
    //             break;
    //         }
    //     }

    struct virtq_used_elem* e = &q->used->ring[(q->last_seen_used - 1) % q->num];
    struct virtq_desc* vdesc = (struct virtq_desc*)e->id;

    printf("Ring 0x%x\n", q->used->ring);
    printf("Processing buffer ring:0x%x, id:0x%x e->len: %d\n", q->used->ring, e->id, e->len);
    printf("Vdesc addr:0x%x, len: %d, flags 0x%x\n", vdesc->addr, vdesc->len, vdesc->flags);
    // process_buffer(e);
    q->last_seen_used++;
    // }
    DSB;
    printf("Returning %i", q->used->ring[idx_old].len);
    return (q->used->ring[idx_old].len);
}

// uint32_t virtio_mmio_notify_queue(volatile virtio_device *dev,
//                                   struct virtq *q){
//     volatile_write32(QUEUENOTIFY(dev->regs), (q->queue_index));
//     return VIRT_OK;
// }
