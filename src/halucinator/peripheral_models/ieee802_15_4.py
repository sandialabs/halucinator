# Copyright 2019 National Technology & Engineering Solutions of Sandia, LLC (NTESS).
# Under the terms of Contract DE-NA0003525 with NTESS, the U.S. Government retains
# certain rights in this software.


import binascii
import logging
import time
from collections import deque

from halucinator.peripheral_models import peripheral_server
from halucinator.peripheral_models.interrupts import Interrupts

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


# Register the pub/sub calls and methods that need mapped
@peripheral_server.peripheral_model
class IEEE802_15_4(object):

    IRQ_NAME = "802_15_4_RX_Frame"
    frame_queue = deque()
    calc_crc = True
    rx_frame_isr = None
    rx_isr_enabled = False
    frame_time = deque()  # Used to record reception time

    @classmethod
    def enable_rx_isr(cls, interface_id):
        cls.rx_isr_enabled = True
        if cls.frame_queue and cls.rx_frame_isr is not None:
            Interrupts.trigger_interrupt(cls.rx_frame_isr, cls.IRQ_NAME)

    @classmethod
    def disable_rx_isr(self, interface_id):
        IEEE802_15_4.rx_isr_enabled = False

    @classmethod
    @peripheral_server.tx_msg
    def tx_frame(cls, interface_id, frame):
        """
        Creates the message that Peripheral.tx_msga will send on this
        event
        """
        print("Sending Frame (%i): " % len(frame), binascii.hexlify(frame))
        msg = {"frame": frame}
        return msg

    @classmethod
    @peripheral_server.reg_rx_handler
    def rx_frame(cls, msg):
        """
        Processes reception of this type of message from
        PeripheralServer.rx_frame
        """
        frame = msg["frame"]
        log.info("Received Frame: %s" % binascii.hexlify(frame))

        cls.frame_queue.append(frame)
        cls.frame_time.append(time.time())
        if cls.rx_frame_isr is not None and cls.rx_isr_enabled:
            Interrupts.trigger_interrupt(cls.rx_frame_isr, cls.IRQ_NAME)

    @classmethod
    def get_first_frame(cls, get_time=False):
        frame = None
        rx_time = None
        log.info("Checking for frame")
        if cls.frame_queue > 0:
            log.info("Returning frame")
            frame = cls.frame_queue.popleft()
            rx_time = cls.frame_time.popleft()

        if get_time:
            return frame, rx_time
        else:
            return frame

    @classmethod
    def has_frame(cls):
        return len(cls.frame_queue) > 0

    @classmethod
    def get_frame_info(cls):
        """
        return number of frames and length of first frame
        """
        queue = cls.frame_queue
        if queue:
            return len(queue), len(queue[0])
        return 0, 0
