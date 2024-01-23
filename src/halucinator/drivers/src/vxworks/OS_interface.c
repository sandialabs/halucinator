
#include <OS_interface.h>
#include <assert.h>
#include <stddef.h>
#include <target_defs.h>

/*
*  Returns the base address of the virtio ethernet device this
*  interface should use.
*
*  :param name:   Name of the interfaces
*  :param pdata:  Pointer to other data only used by OS functions
*
*  :returns base_addr:
*/
int OS_get_eth_base_addr(char* name, void* pdata)
{
    return 0;
}

int OS_sema_init(OS_SEMA_T* sema, int num, int avail);

int OS_sema_alloc(OS_SEMA_T* sema, int num, int avail)
{
    sema = TRGT_semCCreate(1, avail);
    return 0;
}

/*
* Takes an entry from the sema, blocking/sleeping for time out
*
*/
int OS_sema_take(OS_SEMA_T* sema, int timeout)
{
    return TRGT_semTake(sema, timeout);
}

int OS_sema_give(OS_SEMA_T* sema)
{
    return TRGT_semGive(sema);
}

int OS_irq_lock()
{
    TRGT_intLock();
    return 0;
}

int OS_irq_unlock()
{
    TRGT_intUnlock();
    return 0;
}

int OS_get_mac(char* name, uint32_t* pdata, char* mac_addr)
{
    return 0;
}