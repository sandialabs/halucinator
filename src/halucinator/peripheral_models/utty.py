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



class UTTYInterface:

    def __init__(self, interface_id, enabled=True,
                  irq_num=None,):
        self.interface_id = interface_id
        self.rx_queue = deque()
        self.tx_queue = deque()
        self.irq_num = irq_num
        self.enabled = enabled
        # self.serial_port = serial.Serial(serial_port, baud)

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


    def buffer_rx_chars_qmp(self, chars): 
        '''
       
        '''
        if self.enabled:
            log.info("Adding chars to: %s" % self.interface_id)
            for char in chars:
                self.rx_queue.append(char)
            #self.rxchar_times.append(time.time())
        
            self._fire_interrupt_qmp()
        else:
            log.info("%s Not enabled: " % self.interface_id)
            return
    
    
    def get_rx_char(self, get_time=False):
        char = None
        rx_time = None
        
        if self.rx_queue:
            char = self.rx_queue.popleft()
            #rx_time = self.frame_times.popleft()
        else:
            return 0x00

        if get_time:
            return char#, rx_time
        else:
            return char

    def get_rx_buff_size(self, ):
        if self.rx_queue:
            #log.info()
            return len(self.rx_queue)
        else:
            return 0        



    def buffer_tx_char_qmp(self, char): 
        '''
        
        '''
        if self.enabled:
            self.tx_queue.append(char)
            #self.txchar_times.append(time.time())
            log.info("Adding char to: %s" % self.interface_id)
            self._fire_interrupt_qmp()
        else:
            return
    def get_tx_char(self, get_time=False):
        char = None
        rx_time = None
        
        if self.tx_queue:
            char = self.tx_queue.popleft()
            #rx_time = self.frame_times.popleft()

        if get_time:
            return char#, rx_time
        else:
            return char

    def get_tx_buff_size(self, ):
        if self.tx_queue:
            return len(self.tx_queue)
    
    # def get_frame_info(self):
    #     '''
    #         Returns the number of frames in the Queue and number of 
    #         len of first frame
    #     '''
    #     if self.rx_queue:   
    #         return len(self.rx_queue), len(self.rx_queue[0])
    #     return 0, 0

# Register the pub/sub calls and methods that need mapped
@peripheral_server.peripheral_model
class UTTYModel(object):

    interfaces = dict()

    @classmethod
    def add_interface(cls, interface_id, enabled=True,irq_num=None,):
        '''
           
        '''
        
        interface = UTTYInterface(interface_id, enabled=True,irq_num=irq_num)
        cls.interfaces[interface_id] = interface

    # @classmethod    
    # def enable_rx_isr_bp(cls, interface_id):
    #     cls.interfaces[interface_id].enable_irq_bp()

    # @classmethod
    # def disable_rx_isr_bp(cls, interface_id):
    #     cls.interfaces[interface_id].disable_irq()


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
    def tx_buf(cls, interface_id, buf):
        '''
            Creates the message that Peripheral.tx_msga will send on this 
            event
        '''
        msg = {'interface_id': interface_id, 'chars': buf}
        return msg

    @classmethod
    @peripheral_server.reg_rx_handler
    def rx_char_or_buf(cls, msg):
        '''
            Processes reception of this type of message from 
            PeripheralServer.rx_msg
        '''
        interface_id = msg['interface_id']
        interface = cls.interfaces[interface_id]
        if isinstance(msg['char'], int):
            log.info("Adding char to: %s" % interface_id)
            char = msg['char']
            interface.buffer_rx_chars_qmp([char])
        else:
            # TODO: support buffering
            char_buff = msg['char']
            log.info("Adding buffer to: %s" % interface_id)
            interface.buffer_rx_chars_qmp(char_buff)
            # log.info("Adding buffer to: %s" % interface_id)
            # chars = msg['buff']
            # interface.buffer_rx_chars_qmp(chars)
            pass


    @classmethod
    def get_rx_char(cls, interface_id, get_time=False):
        log.info("Getting RX char from: %s" % str(interface_id))
        interface = cls.interfaces[interface_id]
        char = interface.get_rx_char(get_time)
        try:
            char = ord(char)
        except TypeError:
            pass
        return char
    @classmethod
    def get_rx_buff_size(cls,interface_id):
        log.info("Getting RX buff size from: %s" % str(interface_id))
        interface = cls.interfaces[interface_id]
        
       
        return interface.get_rx_buff_size()


    # @classmethod
    # def get_frame_info(cls, interface_id):
    #     '''
    #         return number of frames and length of first frame
    #     '''
    #     interface = cls.interfaces[interface_id]
    #     return interface.get_frame_info()
        

