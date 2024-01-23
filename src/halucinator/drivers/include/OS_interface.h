/*

File defines interface needed for Ethernet to be interact with the host OS

To port Ethernet driver to a new OS implement this interface
*/
#ifndef __OS_INTERFACE_H
#define __OS_INTERFACE_H

#include <stdint.h>
#include <target_defs.h>

#ifndef OS_SEMA_FOREVER
#define OS_SEMA_FOREVER -1
#endif

/* OS_sema_alloc
*  Allocates and initializes a semaphore with `num` of slots available
*  and `avail` available.
*  
* :param sema:   Un-allocated pointer to a sema.  OS needs to alloc
* :param num:    Number of slots the semaphore should have 
* :param avail:  Num slots that should be available
* :returns:   0 on success, negative number on failure
*/
int OS_sema_alloc(OS_SEMA_T* sema, int num, int avail);

/*
* Takes `num` slots from semaphore, blocking/sleeping until taken
*
*
*/
int OS_sema_take(OS_SEMA_T* sema, int timeout);

int OS_sema_give(OS_SEMA_T* sema);

int OS_irq_lock();
int OS_irq_unlock();

int OS_get_mac(char* name, uint32_t* pdata, char* mac_addr);

/*
*  Returns the base address of the virtio ethernet device this 
*  interface should use.
*  
*  :param name:   Name of the interfaces
*  :param pdata:  Pointer to other data only used by OS functions
*  
*  :returns base_addr:
*/
int OS_get_eth_base_addr(char* name, void* pdata);

#endif
