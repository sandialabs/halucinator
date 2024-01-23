#include <assert.h>
#include <halucinator.h>
#include <qemu/net/virtio_net_device.h>
#include <stdint.h>
#include <target_defs.h>
#include <vxworks/defines.h>
#include <vxworks/ether_end.h>

// # Move to Target_Defs
#define NET_POOL_OFFSET 100
#define CL_POOL_ID_OFFSET 200
#define END_OBJ_INTERFACE_NAME_OFFSET 0x08 // Param 3 in endObjInit copied to this offset
#define MAX_FRAME_LENGTH 0x5f0

int net_job_callback(END_INTERFACE_T* p_dev, uint32_t param2, uint32_t param3,
    uint32_t param4, uint32_t param5);

// static HAL_IRQ_CONFIG_T* g_irq_cfg;

// void vxworks_ethernet_dev_init(HAL_IRQ_CONFIG_T * irq_cfg){
//     g_irq_cfg = irq_cfg;
// }

// Needs to be defined externally and populated
extern ETHERNET_INTERFACE_MAP_T g_ethernet_interface_list[];

/*
*   This method is used to map interface to the device
*   It uses the register address to id the interface.  This can be found in the
*   Configuration string passed to muxDevLoad usually value before first :
*/
struct eth_device* _get_interface(END_INTERFACE_T* p_end_obj)
{
    ETHERNET_INTERFACE_MAP_T entry;
    uint32_t base_addr = (uint32_t)p_end_obj->base_addr;
    // LOG_DEBUG("Looking for reg 0x%08x\n", base_addr);
    entry = g_ethernet_interface_list[0];
    for (int i = 0; entry.dev != NULL; ++i) {
        if (entry.reg_addr == base_addr) {
            // LOG_DEBUG("Match found\n");
            return entry.dev;
        }
        entry = g_ethernet_interface_list[i];
    }
    LOG_ERROR("Match NOT for Etherent Interfaces at 0x%0x\n", (uint32_t)p_end_obj);
    return NULL;
}

//   Intercept to handle the ethernet receive.
//   This is the function passed to intConnect for the ethernet device
int INTERCEPT ethernet_isr(END_INTERFACE_T* p_dev)
{
    struct eth_device* dev;
    uint32_t status;
    int has_data;
    uint32_t sp;
    int ret_value;

    LOG_DEBUG("In ethernet_isr\n");
    dev = _get_interface(p_dev);
    assert(dev != NULL);
    status = virtio_net_ack_irq(dev); //Get the status and clears interrupt
    asm("mov %[ret_addr], sp"
        : [ ret_addr ] "=r"(sp)
        :
        : "memory");
    LOG_DEBUG("SP Before Call to netJobAdd 0x%08x\n", sp);
    LOG_DEBUG("IRQ_STATUS 0x%08x\n", status);
    if (status & 0x01) { // Ring update
        LOG_DEBUG("Virtio Buffer Update\n");
        virtio_net_check_tx_done(dev);
        has_data = virtio_net_check_rx_data(dev);
        if (has_data) {
            LOG_DEBUG("Has Data Calling netJobAdd\n");

            ret_value = TRGT_netJobAdd((pointer)(&net_job_callback), (uint32_t)p_dev, 0, 0, 0, 0);
            if (ret_value != 0) {
                LOG_ERROR("Call to netJobAdd Failed\n");
                virtio_net_discard_rx_data(dev);
            }
        }
    }
    if (status & 0x2) { //Configuration change
        LOG_WARNING("Virtio-net configuration changed");
    }
}

//
//
//  This is the method that netJobAdd will call.  If want original look
//  in ethernet_isr for call to netJobAdd
//
int net_job_callback(END_INTERFACE_T* p_dev, uint32_t param2, uint32_t param3,
    uint32_t param4, uint32_t param5)
{

    LOG_DEBUG("In netJobCallback\n");
    struct eth_device* dev;
    dev = _get_interface(p_dev);
    int num_bytes_rx;
    M_BLK_ID_T* m_blk;
    assert(dev != NULL);

    NET_POOL_T* p_net_pool = p_dev->p_net_pool;

    LOG_DEBUG("Net Pool %p\n", p_net_pool);
    m_blk = (M_BLK_ID_T*)TRGT_netTupleGet(p_net_pool, MAX_FRAME_LENGTH, 1, 1, 1);

    if (m_blk == NULL) {
        LOG_ERROR("No MBlk Allocated\n");
        return VXWORKS_ERROR;
    }

    num_bytes_rx = virtio_net_rx_frame(dev, m_blk->data, MAX_FRAME_LENGTH);
    if (num_bytes_rx > 0) {
        m_blk->len = num_bytes_rx;
        m_blk->pktLen = num_bytes_rx;
        m_blk->flags |= 2;
        LOG_DEBUG("Num Bytes Received %i\n", num_bytes_rx);
        TRGT_muxReceive(p_dev, m_blk);
        return VXWORKS_OK;
    }
    TRGT_netMblkClChainFree(m_blk);

    return VXWORKS_ERROR;
}

int INTERCEPT eth_send(END_INTERFACE_T* p_end_obj, M_BLK_ID_T* mblk)
{
    LOG_DEBUG("In Eth Send\n");
    int result;
    struct eth_device* dev;
    dev = _get_interface(p_end_obj);
    assert(dev != NULL);

    result = virtio_net_tx_frame(dev, mblk->data, mblk->len);

    return result;
}

int INTERCEPT eth_start(END_INTERFACE_T* p_end_obj)
{
    struct eth_device* dev;
    struct eth_virtio_data* dev_data;
    int is_ok;
    LOG_DEBUG("In Eth Start %p\n", p_end_obj);

    dev = _get_interface(p_end_obj);
    assert(dev != NULL);
    dev_data = DEV_DATA(dev);
    LOG_DEBUG("Got Interface\n");

    // Could initialize the interface here
    TRGT_intLock();
    OS_sema_alloc(dev_data->tx_sema, QUEUE_SIZE, QUEUE_SIZE);
    if (dev_data->tx_sema == NULL) {
        LOG_ERROR("Failed to Alloc TX Sema\n");
        assert(dev_data->tx_sema == NULL);
    }
    TRGT_endFlagsSet(p_end_obj, 0x41);
    is_ok = TRGT_intConnect(p_end_obj->irq_num, (void*)ethernet_isr, (int)p_end_obj);
    TRGT_intEnable(p_end_obj->irq_num);
    TRGT_intUnlock();

    // assert(is_ok == VXWORKS_OK);
    LOG_DEBUG("INT Connected\n");
    return 0;
}

int INTERCEPT eth_ioctl(END_INTERFACE_T* p_end_obj, uint32_t func_code, uint32_t* data)
{
    uint32_t ret_addr;
    asm("mov %[ret_addr], lr"
        : [ ret_addr ] "=r"(ret_addr)
        :
        : "memory");
    LOG_DEBUG("In Eth Ioctl\n");
    struct eth_device* dev = _get_interface(p_end_obj);

    // 0x4004651b PollStatsInit
    // 0x40046905  called in ipAttach
    // 0x80046904  //called from ifioctl
    // 0x80046904
    switch (func_code) {
    case 0x40046912: // This is not get MAC
        if (data != NULL) {
            LOG_DEBUG("Getting MAC %p, %p\n", dev, (uint8_t*)data);
            *data = 0xe;
            return 0;
        }
        break;
    case 0x40046907: // SET_MAC,
        if (data != NULL) {
            TRGT_bcopy(&p_end_obj->mac_addr, data, p_end_obj->mac_addr_len);
            LOG_DEBUG("Setting MAC %p, %p\n", dev, (uint8_t*)data);
            return 0;
        }
        break;
    case 0x40046905: // e_io_cs_flags, # "EIOCSFLAGS",
        LOG_DEBUG("IOCTL: EIOCGFLAGS?\n");
        *data = TRGT_endFlagsGet(p_end_obj);
        return 0;

    case 0x40046910:
        if (data != NULL) {
            LOG_DEBUG("IOCTL: GET M2_interface_data\n");
            TRGT_bcopy(&p_end_obj->M2_interface, data, 0x204);
            return 0;
        }
        break;
    case 0x80046906:

        if (data != NULL) {
            LOG_DEBUG("IOCTL: GET offset 0x1a8\n");
            TRGT_bcopy(data, &p_end_obj->mac_addr, p_end_obj->mac_addr_len);
            return 0;
        }
        break;
    case 0x80046904: //   'EIOCPOLLSTOP',
        if ((int)data < 0) {
            TRGT_endFlagsClr(p_end_obj, ~(uint)data);
        } else {
            TRGT_endFlagsSet(p_end_obj, (uint)data);
        }
        // TRGT_FUN_02002950(p_end_obj); May need this
        return 0;
        break;
    case 0x8004690e: //   'EIOCGMIB2',
        TRGT_intLock();
        p_end_obj->offset_0x2ec |= 1;
        TRGT_intUnlock();
        return 0;
        break;
    case 0x8004690f: //  'EIOCGHDRLEN',)
        LOG_DEBUG("IOCTL: EIOCGHDRLEN\n");
        TRGT_intLock();
        p_end_obj->offset_0x2ec &= 0xFFFFFFFe;
        TRGT_intUnlock();
        return 0;
        break;
    default:
        LOG_WARNING("Unknown IOCTL(0x%08x, 0x%08x)\n", func_code, data);
    }

    LOG_WARNING("Unimplemented IOCTL returning to 0x%08x\n", ret_addr);
    return 0x16;
}
