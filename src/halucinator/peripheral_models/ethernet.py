# Copyright 2019 National Technology & Engineering Solutions of Sandia, LLC (NTESS). 
# Under the terms of Contract DE-NA0003525 with NTESS, the U.S. Government retains 
# certain rights in this software.


from . import peripheral_server
# from peripheral_server import PeripheralServer, peripheral_model
from collections import deque, defaultdict
from .interrupts import Interrupts
import binascii
import struct
import logging
import time
log = logging.getLogger(__name__)
# log.setLevel(logging.DEBUG)



class EthernetInterface:

    def __init__(self, interface_id, enabled=True,
                 calc_crc=True, irq_num=None):
        self.interface_id = interface_id
        self.rx_queue = deque()
        self.frame_times = deque()
        self.calc_crc = calc_crc
        self.irq_num = irq_num
        self.enabled = enabled

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

    def flush(self):
        self.rx_queue.clear()

    def disable_irq(self):
        self.irq_enabled = False

    def enable_irq_bp(self):
        Interrupts.clear_active_bp(self.irq_num)

    def _fire_interrupt_bp(self):
        if self.rx_queue and self.irq_num:
            Interrupts.set_active_bp(self.irq_num)

    def _fire_interrupt_qmp(self):
        if self.rx_queue and self.irq_num:
            log.debug("Sending Interupt for %s: %#x" %(self.interface_id, self.irq_num))
            Interrupts.set_active_qmp(self.irq_num)

    def buffer_frame_qmp(self, frame): 
        '''
        This method buffer the frame so it can be read into the firmware
        later using the get_frame method
        '''
        if self.enabled:
            self.rx_queue.append(frame)
            self.frame_times.append(time.time())
            log.info("Adding Frame to: %s" % self.interface_id)
            self._fire_interrupt_qmp()
        else:
            return

    def get_frame(self, get_time=False):
        frame = None
        rx_time = None
        
        if self.rx_queue:
            frame = self.rx_queue.popleft()
            rx_time = self.frame_times.popleft()

        if get_time:
            return frame, rx_time
        else:
            return frame

    def get_frame_info(self):
        '''
            Returns the number of frames in the Queue and number of 
            len of first frame
        '''
        if self.rx_queue:   
            return len(self.rx_queue), len(self.rx_queue[0])
        return 0, 0

# Register the pub/sub calls and methods that need mapped
@peripheral_server.peripheral_model
class EthernetModel(object):

    # frame_queues = defaultdict(deque)
    # calc_crc = True
    # rx_frame_irq = None
    # rx_irq_enabled = False
    # frame_times = defaultdict(deque)  # Used to record reception time
    interfaces = dict()

    @classmethod
    def add_interface(cls, interface_id, enabled=True, calc_crc=True, irq_num=None):
        '''
            Used to add an interface to the model.

            interface_id:   The id used for the interface
            enable:         Interface is enabled
            calc_crc:       Should calculate and append CRC to sent frames 
                            (used if HW would normally do this)
            irq_num:        The irq number to trigger on received frames for this 
                            interfaces
        '''
        interface = EthernetInterface(interface_id, enabled=True, calc_crc=calc_crc, 
                                       irq_num=irq_num)
        cls.interfaces[interface_id] = interface

    @classmethod    
    def enable_rx_isr_bp(cls, interface_id):
        cls.interfaces[interface_id].enable_irq_bp()

    @classmethod
    def disable_rx_isr_bp(cls, interface_id):
        cls.interfaces[interface_id].disable_irq()


    @classmethod
    def enable(cls, interface_id):
        cls.interfaces[interface_id].enable()

    @classmethod
    def flush(cls, interface_id):
        cls.interfaces[interface_id].flush()

    @classmethod
    def disable(cls, interface_id):
        cls.interfaces[interface_id].disable()

    @classmethod
    @peripheral_server.tx_msg
    def tx_frame(cls, interface_id, frame):
        '''
            Creates the message that Peripheral.tx_msga will send on this 
            event
        '''
        # TODO append CRC if needed for the interface
        print("Sending Frame (%i): " % len(frame), binascii.hexlify(frame))
        # print ""
        msg = {'interface_id': interface_id, 'frame': frame}
        return msg

    @classmethod
    @peripheral_server.reg_rx_handler
    def rx_frame(cls, msg):
        '''
            Processes reception of this type of message from 
            PeripheralServer.rx_msg
        '''
        interface_id = msg['interface_id']
        log.info("Adding Frame to: %s" % interface_id)
        interface = cls.interfaces[interface_id]
        frame = msg['frame']
        interface.buffer_frame_qmp(frame)


    @classmethod
    def get_rx_frame(cls, interface_id, get_time=False):
        log.info("Getting RX frame from: %s" % str(interface_id))
        interface = cls.interfaces[interface_id]
        return interface.get_frame(get_time)


    @classmethod
    def get_frame_info(cls, interface_id):
        '''
            return number of frames and length of first frame
        '''
        interface = cls.interfaces[interface_id]
        return interface.get_frame_info()
        

