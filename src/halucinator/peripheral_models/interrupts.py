# Copyright 2019 National Technology & Engineering Solutions of Sandia, LLC (NTESS). 
# Under the terms of Contract DE-NA0003525 with NTESS, the U.S. Government retains 
# certain rights in this software.

from . import peripheral_server
from collections import deque, defaultdict
import logging
log = logging.getLogger(__name__)
# log.setLevel(logging.DEBUG)


# Register the pub/sub calls and methods that need mapped
@peripheral_server.peripheral_model
class Interrupts(object):
    '''
        Models and external interrupt controller
        Use when need to trigger and interrupt and need additional state
        about it
    '''
    active = defaultdict(bool)
    enabled = defaultdict(bool)

    @classmethod
    @peripheral_server.reg_rx_handler
    def interrupt_request(cls, msg):
        
        if 'num' in msg and msg['num'] in cls._irq_map_i2n:
            irq_num = msg['num']
        else:
            log.error("Unsupported IRQ %s" %(msg))
        
        cls.set_active_qmp(irq_num)

    @classmethod
    def set_active_qmp(cls, irq_num):
        log.debug("Set Active: %s" % hex(irq_num))
        cls.active[irq_num] = True
        cls._trigger_interrupt_qmp(irq_num)

    @classmethod
    def set_active_bp(cls, irq_num):
        log.debug("Set Active: %s" % hex(irq_num))
        cls.active[irq_num] = True
        cls._trigger_interrupt_bp(irq_num)

    @classmethod
    def clear_active_bp(cls, irq_num):
        log.debug("Clear Active: %i" % irq_num)
        peripheral_server.irq_clear_bp(irq_num)
        cls.active[irq_num] = False

    @classmethod
    def clear_active_qmp(cls, irq_num):
        log.debug("Clear Active: %i" % irq_num)
        peripheral_server.irq_clear_qmp(irq_num)
        cls.active[irq_num] = False
        

    @classmethod
    def is_active(cls, irq_num):
        log.debug("Is Active: %i" % irq_num)
        return cls.active[irq_num]

    @classmethod
    def get_first_irq(cls, highest_first=False):
        '''
            Returns the name and number of the highest priority interrupt
            
            :param highest_first:  highest irq
            :returns irq_num:
        '''
        active_irqs = sorted(cls.get_active_irqs(), reverse=highest_first)
        if len(active_irqs) > 0:
            return active_irqs[0]
        else:
            return None

    @classmethod
    def get_active_irqs(cls):
        active_irqs = set([irq_num for irq_num, state in cls.active.items() if state ])
        enabled_irqs = set([irq_num for irq_num, state in cls.enabled.items() if state ])
        active_irqs = active_irqs.intersection(enabled_irqs)
        log.debug("Get Active ISRs: %s" % active_irqs)
        return active_irqs

    @classmethod
    def _trigger_interrupt_qmp(cls, irq_num):
        '''
            This should be used to trigger an interrupt for everywhere
            except in a bp_handler.
        '''
        if cls.enabled[irq_num] and cls.active[irq_num]:
            log.info("Triggering Interrupt: %i" % (irq_num))
            peripheral_server.irq_set_qmp(irq_num)

    @classmethod
    def _trigger_interrupt_bp(cls, irq_num):
        '''n
            This should be used if need to trigger an interrupt inside a 
            bp_handler.  Not sure this even makes sense to do.
        '''
        if cls.enabled[irq_num] and cls.active[irq_num]:
            log.info("Triggering Interrupt: %i" % irq_num)
            peripheral_server.irq_set_bp(irq_num)

    @classmethod
    def enable_bp(cls, irq_num):
        cls.enabled[irq_num] = True
        cls._trigger_interrupt_bp(irq_num)

    @classmethod
    def enable_qmp(cls, irq_num):
        cls.enabled[irq_num] = True
        cls._trigger_interrupt_qmp(irq_num)

    @classmethod
    def disable_bp(cls, irq_num):
        cls.enabled[irq_num] = False
        peripheral_server.irq_clear_bp(irq_num) #just want to disable it

    @classmethod
    def disable_qmp(cls, irq_num):
        cls.enabled[irq_num] = False
        peripheral_server.irq_clear_qmp(irq_num)