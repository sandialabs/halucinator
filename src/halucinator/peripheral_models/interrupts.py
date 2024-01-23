# Copyright 2019 National Technology & Engineering Solutions of Sandia, LLC (NTESS).
# Under the terms of Contract DE-NA0003525 with NTESS, the U.S. Government retains
# certain rights in this software.
"""
Peripheral Model for interrupts, exposes interfaces that can be used over both
ZMQ and BP Handlers
"""

from collections import defaultdict
import logging
from . import peripheral_server

log = logging.getLogger(__name__)
# log.setLevel(logging.DEBUG)


# Register the pub/sub calls and methods that need mapped
@peripheral_server.peripheral_model
class Interrupts:
    """
    Models and external interrupt controller
    Use when need to trigger and interrupt and need additional state
    about it
    """

    active = defaultdict(bool)
    enabled = defaultdict(bool)

    @classmethod
    @peripheral_server.reg_rx_handler
    def interrupt_request(cls, msg):
        """
        Creates ZMQ interface to trigger an interrupt
        """
        if "num" in msg:
            irq_num = msg["num"]
        else:
            log.error("Unsupported IRQ %s", msg)

        cls.set_active_qmp(irq_num)

    @classmethod
    def set_active_qmp(cls, irq_num):
        """
        Sets an interrupt using QMP Interface
        DO NOT use when executing from context of a BP Handler
        """
        log.debug("Set Active QMP: %s", hex(irq_num))
        peripheral_server.irq_set_qmp(irq_num)

    @classmethod
    def set_active_bp(cls, irq_num):
        """
        Sets an interrupt using GDB interface can be used in BP Handlers
        """
        log.debug("Set Active BP: %s", hex(irq_num))
        peripheral_server.irq_set_bp(irq_num)

    @classmethod
    def clear_active_bp(cls, irq_num):
        """
        Clears active interrupt.  Safe for use in BP Handler context
        """
        log.debug("Clear Active BP: %i", irq_num)
        peripheral_server.irq_clear_bp(irq_num)

    @classmethod
    def clear_active_qmp(cls, irq_num):
        """
        Clears an active interrupt using QMP interface
        DO NOT use from context of BP Handler
        """
        log.debug("Clear Active: %i", irq_num)
        peripheral_server.irq_clear_qmp(irq_num)

    @classmethod
    def enable_bp(cls, irq_num):
        """
        Enables an interrupt so it can be triggered
        Safe for use from BP Handler context
        """
        peripheral_server.irq_enable_bp(irq_num)

    @classmethod
    def enable_qmp(cls, irq_num):
        """
        Enables an interrupt using QMP interface
        DO NOT use from BP Handler context
        """
        peripheral_server.irq_enable_qmp(irq_num)

    @classmethod
    def disable_bp(cls, irq_num):
        """
        Disables an interrupt so it can be triggered
        Safe for use from BP Handler context
        """
        peripheral_server.irq_disable_bp(irq_num)

    @classmethod
    def disable_qmp(cls, irq_num):
        """
        Disables an interrupt using QMP interface
        DO NOT use from BP Handler context
        """
        peripheral_server.irq_disable_qmp(irq_num)
