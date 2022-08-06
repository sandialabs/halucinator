# Copyright 2019 National Technology & Engineering Solutions of Sandia, LLC (NTESS).
# Under the terms of Contract DE-NA0003525 with NTESS, the U.S. Government retains
# certain rights in this software.


import logging
import time

from halucinator.bp_handlers.bp_handler import BPHandler, bp_handler
from halucinator.peripheral_models.ethernet import EthernetModel

log = logging.getLogger(__name__)


class EthernetSmartConnect(BPHandler):
    def __init__(self, model=EthernetModel):
        BPHandler.__init__(self)
        log.debug("Ethernet Smart Connect Init")
        self.model = model
        self.last_rx_time = time.time()
        self.last_exec_time = time.time()
        self.dev_ptr = None
        self.netif_ptr = None

    def get_id(self, qemu):
        return "ksz8851"

    # This is custom written from binary as ksz8851snl_read got inlined
    @bp_handler(["addr_15882"])
    def eth_process(self, qemu, bp_addr):
        now = time.time()
        log.info("In addr_15882: %f" % (now - self.last_exec_time))
        self.last_exec_time = time.time()

        (num_frames, size_1st_frame) = self.model.get_frame_info(self.get_id(qemu))
        if num_frames > 0:
            # If frame, get global buffer, write frame to it can call function to process
            # the frame
            log.info("Reading in frame")
            buf_ptr = qemu.read_memory(0x200000E8, 1, 4)  # ip_packet_bufer
            frame = self.model.get_rx_frame(self.get_id(qemu))
            frame_len = len(frame)
            qemu.write_memory(buf_ptr, 1, frame, frame_len)
            qemu.regs.r0 = buf_ptr
            qemu.regs.r1 = frame_len
            qemu.regs.lr = qemu.regs.pc | 1  # set thumb bit, lr already save to stack
            qemu.regs.pc = qemu.avatar.callables["ip64_eth_interface_input"] | 1
            return True, None

        return False, None

    @bp_handler(["ksz8851snl_read", "input"])
    def read(self, qemu, bp_addr):
        # 1. See if there are frames
        now = time.time()
        log.info("In ETHERNET_INPUT: %f" % (now - self.last_exec_time))
        self.last_exec_time = time.time()

        (num_frames, size_1st_frame) = self.model.get_frame_info(self.get_id(qemu))
        if num_frames > 0:
            data_ptr = qemu.regs.r0
            max_len = qemu.regs.r1
            frame, rx_time = self.model.get_rx_frame(self.get_id(qemu), True)
            frame_length = len(frame)
            if max_len >= frame_length:
                log.info("Frame Read w len %i", frame_length)
                qemu.write_memory(data_ptr, 1, frame, len(frame))
                return True, frame_length

        return True, 0

    @bp_handler(["ksz8851snl_send", "output"])
    def send(self, qemu, bp_addr):
        data_ptr = qemu.regs.r0
        length = qemu.regs.r1
        frame = qemu.read_memory(data_ptr, 1, length, raw=True)
        log.info("Send Called w frame length: %i", length)
        self.model.tx_frame(self.get_id(qemu), frame)
        return True, length

    @bp_handler(["ksz8851snl_init"])
    def return_ok(self, qemu, bp_addr):
        log.info("Init Called")
        return True, 0
