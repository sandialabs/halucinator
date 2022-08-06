# Copyright 2019 National Technology & Engineering Solutions of Sandia, LLC (NTESS).
# Under the terms of Contract DE-NA0003525 with NTESS, the U.S. Government retains
# certain rights in this software.

import logging
import struct

from halucinator.bp_handlers.bp_handler import BPHandler, bp_handler

log = logging.getLogger(__name__)


# This is just a stub to enable getting edbg_eui for use as MAC
# on 6LoWPAN example apps


class EDBG_Stub(BPHandler):
    def __init__(self, model=None):
        BPHandler.__init__(self)
        self.model = model
        self.eui64 = ""

    def register_handler(self, qemu, addr, func_name, eui64=None):
        if eui64 is not None:
            self.eui64 = eui64
        return BPHandler.register_handler(self, qemu, addr, func_name)

    @bp_handler(["i2c_master_init", "i2c_master_enable"])
    def return_void(self, qemu, bp_addr):
        return True, None

    @bp_handler(["i2c_master_write_packet_wait_no_stop"])
    def return_ok(self, qemu, bp_addr):
        return True, 0

    @bp_handler(["i2c_master_read_packet_wait"])
    def get_edbg_eui64(self, qemu, bp_addr):
        packet = qemu.regs.r1
        packet_struct = qemu.read_memory(packet + 2, 1, 6, raw=True)
        (length, data_ptr) = struct.unpack("<HI", packet_struct)
        if length > len(self.eui64):
            eui64 = self.eui64 + "\55" * (length - len(self.eui64))
            qemu.write_memory(data_ptr, 1, eui64, len(eui64), raw=True)
        else:
            qemu.write_memory(data_ptr, 1, self.eui64, length, raw=True)
        return True, 0
