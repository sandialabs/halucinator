# Copyright 2019 National Technology & Engineering Solutions of Sandia, LLC (NTESS).
# Under the terms of Contract DE-NA0003525 with NTESS, the U.S. Government retains
# certain rights in this software.

import logging

from halucinator.bp_handlers.bp_handler import BPHandler, bp_handler
from halucinator.peripheral_models.uart import UARTPublisher

log = logging.getLogger(__name__)


class MbedUART(BPHandler):
    def __init__(self, impl=UARTPublisher):
        self.model = impl

    @bp_handler(["_ZN4mbed6Stream4getcEv"])
    def getc(self, qemu, bp_addr):
        param0 = qemu.regs.r0
        # TODO: param0 is the 'this'pointer, use it get hw address of UART
        # just using the this pointer will make this change per firmware
        ret = self.model.read(param0, 1, block=True)[0]
        intercept = True
        return intercept, ord(ret)

    @bp_handler(["_ZN4mbed6Stream4putcEv", "_ZN4mbed6Serial5_putcEi"])
    def putc(self, qemu, bp_addr):
        param0 = qemu.regs.r0
        param1 = qemu.regs.r1
        log.info("Mbed Putc")
        # TODO: param0 is the 'this'pointer, use it to index the UARTs
        chars = chr(param1)

        _ = self.model.write(param0, chars)
        intercept = True
        return intercept, 1

    @bp_handler(["_ZN4mbed6Stream4putsEPKc"])
    def puts(self, qemu, bp_addr):
        log.info("Mbed Puts")
        param0 = qemu.regs.r0
        param1 = qemu.regs.r1
        # TODO: param0 is the 'this'pointer, use it to index the UARTs
        chars = []  # write is expecting an iterable
        chars.append(qemu.read_memory(param1, 1, 1))
        while chars[-1] != "\x00":
            chars.append(qemu.read_memory(param1, 1, 1))
        self.model.write(param0, chars)
        intercept = True
        return intercept, len(chars)
