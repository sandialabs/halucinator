# Copyright 2019 National Technology & Engineering Solutions of Sandia, LLC (NTESS). 
# Under the terms of Contract DE-NA0003525 with NTESS, the U.S. Government retains 
# certain rights in this software.

from os import sys, path
from ..peripheral_models.peripheral_server import encode_zmq_msg, decode_zmq_msg
import zmq
from multiprocessing import Process
from .ioserver import IOServer
import logging

import os
import socket
import time
import binascii
import scapy.all as scapy
import serial
log = logging.getLogger(__name__)

__run_server = True
__host_port = None
__rx_buffering= False
# def rx_from_emulator(emu_rx_port, interface):
#     ''' 
#         Receives 0mq messages from emu_rx_port    
#         args:
#             emu_rx_port:  The port number on which to listen for messages from
#                           the emulated software
#     '''
#     global __run_server
#     #global __host_port
#     topic = "Peripheral.EthernetModel.tx_frame"
#     context = zmq.Context()
#     mq_socket = context.socket(zmq.SUB)
#     mq_socket.connect("tcp://localhost:%s" % emu_rx_port)
#     mq_socket.setsockopt(zmq.SUBSCRIBE, topic.encode('utf-8'))

#     while (__run_server):
#         msg = mq_socket.recv_string()
#         # print "Got from emulator:", msg
#         topic, data = decode_zmq_msg(msg)
#         frame = data['frame']
#         # if len(frame) < 64:
#         #    frame = frame +('\x00' * (64-len(frame)))
#         p = scapy.Raw(frame)
#         scapy.sendp(p, iface=interface)
#         # __host_port.send(frame)
#         print("Sending Frame (%i) on eth: %s" %
#               (len(frame), binascii.hexlify(frame)))


def rx_from_host(io_server, msg_id):
    global __run_server
    global __host_port
    global __rx_buffering
    topic = "Peripheral.UTTYModel.rx_char_or_buf"
    #topic = "Interrupt.Trigger"

    buffer=[]
    #__rx_buffering = True
    while (__run_server):
        
        if __rx_buffering:
            # TODO: Support buffering, time based?
            #data = {'interface_id': msg_id, 'buff': []]}
            char = __host_port.read()
            

            if len(buffer) < 40:
                char_byte = int.from_bytes(char, byteorder='little')
                buffer.append(char_byte)
            else:
                char_byte = int.from_bytes(char, byteorder='little')
                buffer.append(char_byte)
                data = {'interface_id': msg_id, 'char': buffer}
                #to_emu_socket.send_string(msg)
                print("Sent message to emulator ", buffer)
                io_server.send_msg(topic,data)
                buffer=[]

            
        else:
            char = __host_port.read()
            
            char_byte = int.from_bytes(char, byteorder='little')
            print(char_byte)
            data = {'interface_id': msg_id, 'char': char_byte}
            #to_emu_socket.send_string(msg)
            print("Sent message to emulator ", binascii.hexlify(char))
            io_server.send_msg(topic,data)
            #input("Press enter to dent data")
            


def start(port, io_server, msg_id="COM1",baudrate =9600):
    global __run_server
    global __host_port
    __host_port = serial.Serial(port, baudrate)
    
    #io_server.start()
    log.debug("Starting Servers")
    # tx_data = Process(target=rx_from_emulator,
    #                          args=(emu_rx_port, interface)).start()
    # rx_process = Process(
    #     target=rx_from_host, args=(io_server, msg_id)).start()
    rx_from_host(io_server, msg_id)
    try:
        while (1):
            time.sleep(0.1)
    except KeyboardInterrupt:
        __run_server = False
    # emu_rx_process.join()
    # rx_process.join()
    


if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser()
    p.add_argument('-r', '--rx_port', default=5556,
                   help='Port number to receive zmq messages for IO on')
    p.add_argument('-t', '--tx_port', default=5555,
                   help='Port number to send IO messages via zmq')
    p.add_argument('-p', '--port', required=True,
                   help='Host serial port to listen to')
    p.add_argument('--id', default="COM1",
                   help='Emulation Interace to listen to')
    p.add_argument('-b','--baud', default=9600,
                   help='Baud rate')
    args = p.parse_args()
    io_server = IOServer(args.rx_port, args.tx_port)
    time.sleep(1)

    start(args.port, io_server, args.id,args.baud)
