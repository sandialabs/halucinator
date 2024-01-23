//File copied from https://github.com/brenns10/sos/blob/master/kernel/virtio.h
// MIT LISCENCE

/**
 * virtio declarations (mmio, queue)
 */

#ifndef __VIRTIO_H_
#define __VIRTIO_H_
#include "virtio_queue.h"
#include <stdbool.h>
#include <stdint.h>

#define DSB ; //__asm__ volatile ("dsb" ::: "memory")
#define VIRTIO_STATUS_ACKNOWLEDGE (1)
#define VIRTIO_STATUS_DRIVER (2)
#define VIRTIO_STATUS_DRIVER_OK (4)
#define VIRTIO_STATUS_FEATURES_OK (8)
#define VIRTIO_STATUS_DEVICE_NEEDS_RESET (64)
#define VIRTIO_STATUS_FAILED (128)

#define VIRTIO_MAGIC 0x74726976
#define VIRTIO_SERIAL_DEV 0x3
#define VIRTIO_NET_DEV 0x1
#define VIRT_OK 0x0
#define VIRT_ERROR 0x1
#define LEGACY_VERSION 0x1
#define VERSION_1 0x2
#define __a4k __attribute__((aligned(4096)))

/*
 * See Section 4.2.2 of VIRTIO 1.0 Spec:
 * http://docs.oasis-open.org/virtio/virtio/v1.0/cs04/virtio-v1.0-cs04.html
 */

#define MAGICVALUE(regs) ((uint32_t*)&regs.REGS[(0x000)]) /*0x000 Read only*/
#define VERSION(regs) ((uint32_t*)&regs.REGS[(0x004)]) /*0x004 Read only*/
#define DEVICEID(regs) ((uint32_t*)&regs.REGS[(0x008)]) /*0x008 Read only*/
#define VENDORID(regs) ((uint32_t*)&regs.REGS[(0x00c)]) /*0x00c Read only*/
#define DEVICEFEATURES(regs) ((uint32_t*)&regs.REGS[(0x010)]) /*0x010 Read only*/
#define DEVICEFEATURESSEL(regs) ((uint32_t*)&regs.REGS[(0x014)]) /*0x014 Write only*/
#define DRIVERFEATURES(regs) ((uint32_t*)&regs.REGS[(0x020)]) /*0x020 Write only*/
#define DRIVERFEATURESSEL(regs) ((uint32_t*)&regs.REGS[(0x024)]) /*0x024 Write only*/
#define QUEUESEL(regs) ((uint32_t*)&regs.REGS[(0x030)]) /*0x030 Write only*/
#define QUEUENUMMAX(regs) ((uint32_t*)&regs.REGS[(0x034)]) /*0x034 Read only*/
#define QUEUENUM(regs) ((uint32_t*)&regs.REGS[(0x038)]) /*0x038 Write only*/
#define QUEUEREADY(regs) ((uint32_t*)&regs.REGS[(0x044)]) /*0x044 Read and Write*/
#define QUEUENOTIFY(regs) ((uint32_t*)&regs.REGS[(0x050)]) /*0x050 Write only*/
#define INTERRUPTSTATUS(regs) ((uint32_t*)&regs.REGS[(0x60)]) /*0x60 Read only*/
#define INTERRUPTACK(regs) ((uint32_t*)&regs.REGS[(0x064)]) /*0x064 Write only*/
#define STATUS(regs) ((uint32_t*)&regs.REGS[(0x070)]) /*0x070 Read and Write*/
#define QUEUEDESCLOW(regs) ((uint32_t*)&regs.REGS[(0x080)]) /*0x080 Write only*/
#define QUEUEDESCHIGH(regs) ((uint32_t*)&regs.REGS[(0x084)]) /*0x084 Write only*/
#define QUEUEAVAILLOW(regs) ((uint32_t*)&regs.REGS[(0x090)]) /*0x090 Write only*/
#define QUEUEAVAILHIGH(regs) ((uint32_t*)&regs.REGS[(0x094)]) /*0x094 Write only*/
#define QUEUEUSEDLOW(regs) ((uint32_t*)&regs.REGS[(0x0a0)]) /*0x0a0 Write only*/
#define QUEUEUSEDHIGH(regs) ((uint32_t*)&regs.REGS[(0x0a4)]) /*0x0a4 Write only*/
#define CONFIGGENERATION(regs) ((uint32_t*)&regs.REGS[(0x0fc)]) /*0x0fc Read Only*/
#define CONFIG(regs) ((uint32_t*)&regs.Config)

typedef volatile struct virtio_regs {
    uint8_t REGS[100]; //use te #defines to index into it
    uint32_t Config[0];
} virtio_regs;

//     uint32_t MagicValue;            /*0x000 Read only
//                                     Magic value
//                                     0x74726976 (a Little Endian equivalent of the “virt” string).*/
//     uint32_t Version;               /*0x004 Read only
//                                     Device version number
//                                     0x2. Note: Legacy devices (see 4.2.4 Legacy interface) used 0x1.*/
//     uint32_t DeviceID;              /*0x008 Read only
//                                     Virtio Subsystem Device ID
//                                     See 5 Device Types for possible values. Value zero (0x0) is used to define a
//                                     system memory map with placeholder devices at static, well known addresses, assigning
//                                     functions to them depending on user’s needs.*/
//     uint32_t VendorID;              /*0x00c Read only
//                                     Virtio Subsystem Vendor ID*/
//     uint32_t DeviceFeatures;        /*0x010 Read only
//                                     Flags representing features the device supports
//                                     Reading from this register returns 32 consecutive flag bits, the least significant bit
//                                     depending on the last value written to DeviceFeaturesSel. Access to this register
//                                     returns bits DeviceFeaturesSel ∗ 32 to (DeviceFeaturesSel ∗ 32) + 31, eg. feature bits
//                                     0 to 31 if DeviceFeaturesSel is set to 0 and features bits 32 to 63 if DeviceFeaturesSel
//                                     is set to 1. Also see 2.2 Feature Bits. */
//     uint32_t DeviceFeaturesSel;     /*0x014 Write only
//                                     Device (host) features word selection.
//                                     Writing to this register selects a set of 32 device feature bits accessible by reading
//                                     from DeviceFeatures.*/
//     uint32_t _reserved0[2];         /*8 bytes padding*/
//     uint32_t DriverFeatures;        /*0x020 Write only
//                                     Flags representing device features understood and activated by the driver
//                                     Writing to this register sets 32 consecutive flag bits, the least significant bit
//                                     depending on the last value written to DriverFeaturesSel. Access to this register
//                                     sets bits DriverFeaturesSel ∗ 32 to (DriverFeaturesSel ∗ 32) + 31, eg. feature bits
//                                     0 to 31 if DriverFeaturesSel is set to 0 and features bits 32 to 63 if DriverFeaturesSel
//                                     is set to 1. Also see 2.2 Feature Bits. */
//     uint32_t DriverFeaturesSel;     /*0x024 Write only
//                                     Activated (guest) features word selection
//                                     Writing to this register selects a set of 32 activated feature bits accessible by
//                                     writing to DriverFeatures.*/
//     uint32_t _reserved1[2];         /*8 bytes padding*/
//     uint32_t QueueSel;              /*0x030 Write only
//                                     Virtual queue index
//                                     Writing to this register selects the virtual queue that the following operations on
//                                     QueueNumMax, QueueNum, QueueReady, QueueDescLow, QueueDescHigh, QueueAvailLow,
//                                     QueueAvailHigh, QueueUsedLow and QueueUsedHigh apply to. The index number of the
//                                     first queue is zero (0x0).*/
//     uint32_t QueueNumMax;           /*0x034 Read only
//                                     Maximum virtual queue size
//                                     Reading from the register returns the maximum size (number of elements) of the queue
//                                     the device is ready to process or zero (0x0) if the queue is not available.
//                                     This applies to the queue selected by writing to QueueSel.*/
//     uint32_t QueueNum;              /*0x038 Write only
//                                     Virtual queue size
//                                     Queue size is the number of elements in the queue, therefore in each of the
//                                     Descriptor Table, the Available Ring and the Used Ring. Writing to this register
//                                     notifies the device what size of the queue the driver will use. This applies to
//                                     the queue selected by writing to QueueSel.*/
//     uint32_t _reserved2[2];         /*8 bytes padding*/
//     uint32_t QueueReady;            /*0x044 Read and Write
//                                     Virtual queue ready bit
//                                     Writing one (0x1) to this register notifies the device that it can execute requests
//                                     from this virtual queue. Reading from this register returns the last value written
//                                     to it. Both read and write accesses apply to the queue selected by writing to QueueSel.*/
//     uint32_t _reserved3[2];         /*8 bytes padding*/
//     uint32_t QueueNotify;           /*0x050 Write only
//                                     Queue notifier
//                                     Writing a queue index to this register notifies the device that there are new
//                                 universal_features    buffers to process in the queue.*/
//     uint32_t _reserved4[3];         /*12 bytes padding*/
//     uint32_t InterruptStatus;       /*0x60 Read only
//                                     Interrupt status
//                                     Reading from this register returns a bit mask of events that caused the device
//                                     interrupt to be asserted. The following events are possible:

//                                     Used Ring Update
//                                     - bit 0 - the interrupt was asserted because the device has updated the Used Ring
//                                     in at least one of the active virtual queues.
//                                     Configuration Change
//                                     - bit 1 - the interrupt was asserted because the configuration of the device has changed.*/
//     uint32_t InterruptACK;          /*0x064 Write only
//                                     Interrupt acknowledge
//                                     Writing a value with bits set as defined in InterruptStatus to this register notifies
//                                     the device that events causing the interrupt have been handled.*/
//     uint32_t _reserved5[2];         /*8 bytes padding*/
//     uint32_t Status;                /*0x070 Read and Write
//                                     Device status
//                                     Reading from this register returns the current device status flags. Writing non-zero
//                                     values to this register sets the status flags, indicating the driver progress. Writing
//                                     zero (0x0) to this register triggers a device reset. See also p. 4.2.3.1 Device Initialization.*/
//     uint32_t _reserved6[3];         /*12 bytes padding*/
//     uint32_t QueueDescLow;          /*0x080 Write only
//                                     Virtual queue’s Descriptor Table 64 bit long physical address
//                                     Writing to these two registers (lower 32 bits of the address to QueueDescLow, higher 32 bits
//                                     to QueueDescHigh) notifies the device about location of the Descriptor Table of the queue
//                                     selected by writing to QueueSel register.*/
//     uint32_t QueueDescHigh;         /*0x084 Write only*/
//     uint32_t _reserved7[2];         /*8 bytes padding*/
//     uint32_t QueueAvailLow;         /*0x090 Write only
//                                     Virtual queue’s Available Ring 64 bit long physical address
//                                     Writing to these two registers (lower 32 bits of the address to QueueAvailLow, higher 32 bits
//                                     to QueueAvailHigh) notifies the device about location of the Available Ring of the queue
//                                     selected by writing to QueueSel.*/
//     uint32_t QueueAvailHigh;        /*0x094 Write only*/
//     uint32_t _reserved8[2];         /*8 bytes padding*/
//     uint32_t QueueUsedLow;          /*0x0a0 Write only
//                                     Virtual queue’s Used Ring 64 bit long physical address
//                                     Writing to these two registers (lower 32 bits of the address to QueueUsedLow, higher 32 bits
//                                     to QueueUsedHigh) notifies the device about location of the Used Ring of the queue selected
//                                     by writing to QueueSel.*/
//     uint32_t QueueUsedHigh;         /*0x0a4 Write only*/
//     uint32_t _reserved9[21];        /*84 bytes padding*/
//     uint32_t ConfigGeneration;      /*0x0fc Read Only
//                                     Configuration atomicity value
//                                     Reading from this register returns a value describing a version of the device-specific
//                                     configuration space (see Config). The driver can then access the configuration space and,
//                                     when finished, read ConfigGeneration again. If no part of the configuration space has changed
//                                     between these two ConfigGeneration reads, the returned values are identical. If the values
//                                     are different, the configuration space accesses were not atomic and the driver has to perform
//                                     the operations again. See also 2.3.*/
//     uint32_t Config[0];             /*0x100+ Read and Write
//                                     Configuration space
//                                     Device-specific configuration space starts at the offset 0x100 and is accessed with byte
//                                     alignment. Its meaning and size depend on the device and the driver.*/

// /*The virtual queue is configured as follows:
// 1. Select the queue writing its index (first queue is 0) to QueueSel.
// 2. Check if the queue is not already in use: read QueuePFN, expecting a returned value of zero (0x0).
// 3. Read maximum queue size (number of virtio_device) from QueueNumMax. If the returned value is zero (0x0) the queue is not available.
// 4. Allocate and zero the queue pages in contiguous virtual memory, aligning the Used Ring to an optimal boundary (usually page size). The driver should choose a queue size smaller than or equal to QueueNumMax.
// 5. Notify the device about the queue size by writing the size to QueueNum.
// 6. Notify the device about the used alignment by writing its value in bytes to QueueAlign.
// 7. Write the physical number of the first page of the queue to the QueuePFN register.*/
// } virtio_device_legacy;

typedef volatile struct {
    virtio_regs regs;
    uint32_t sys_ctrl_base;
    uint32_t irq_num;
} virtio_device;

struct virtio_features {
    char* name;
    uint32_t bit;
    bool support;
    char* help;
};

extern struct virtio_features universal_features[];
extern const int universal_features_sizeof;
const int universal_features_first_sizeof;

void print_v1_info(volatile virtio_device* dev);

volatile uint32_t volatile_read32(volatile uint32_t* base_addr);

void volatile_write32(volatile uint32_t* address, register uint32_t value);

int virtio_check_features(uint32_t* device, uint32_t* request, struct virtio_features* caps, uint32_t n);

uint32_t virtio_mmio_init(volatile virtio_device* dev);

uint32_t virtio_mmio_select_features(volatile virtio_device* dev, uint32_t feat);

uint32_t virtio_mmio_init_queue(volatile virtio_device* dev,
    volatile struct virtq* q,
    uint32_t queue_index,
    uint32_t queue_sz);

uint32_t virtio_mmio_driver_ok(volatile virtio_device* dev);

uint32_t virtio_mmio_write(volatile virtio_device* dev,
    volatile struct virtq* q,
    uint8_t* buf,
    uint32_t len);

uint32_t virtio_mmio_read_one(volatile virtio_device* dev,
    volatile struct virtq* q,
    uint8_t* buf,
    uint32_t len);

// uint32_t virtio_mmio_notify_queue(volatile virtio_device *dev,
//                                   struct virtq *q);

#endif //__VIRTIO_H_
