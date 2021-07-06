# Copyright 2019 National Technology & Engineering Solutions of Sandia, LLC (NTESS). 
# Under the terms of Contract DE-NA0003525 with NTESS, the U.S. Government retains 
# certain rights in this software.


import zmq
from halucinator.peripheral_models.peripheral_server import encode_zmq_msg, decode_zmq_msg
from halucinator.external_devices.ioserver import IOServer
import logging
import serial
import socket

log = logging.getLogger(__name__)

class SerialTunnel(object):
   
    def __init__(self, port, ioserver, baudrate, use_pipe=False):
        self.ioserver = ioserver
        self.prev_print = None
        if use_pipe:
            self.host_port = open('port', 'w+')
            if not self.host_port:
                print(f"Error opening file: {port}")
                exit(-1)
        else:
            self.host_port = serial.Serial(port, baudrate)
        ioserver.register_topic(
            'Peripheral.UTTYModel.tx_buf', self.write_handler)

    def write_handler(self, ioserver, msg):
        tx_bytes = msg['chars']
        print("Got %s From VM" % str(tx_bytes))
        self.host_port.write(tx_bytes)

    def send_data(self, msg_id, chars):
        data = {'interface_id': msg_id, 'char': chars}
        self.ioserver.send_msg('Peripheral.UTTYModel.rx_char_or_buf', data)


if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser()
    p.add_argument('-r', '--rx_port', default=5556,
                   help='Port number to receive zmq messages for IO on')
    p.add_argument('-t', '--tx_port', default=5555,
                   help='Port number to send IO messages via zmq')
    p.add_argument('--id', default="COM1",
                   help='Emulation Interace to listen to')
    p.add_argument('-p', '--port', required=True,
                   help='Host serial port to listen to')
    p.add_argument('-b','--baud', default=9600,
                   help='Baud rate')
    p.add_argument('-f','--use_file', default=False, action='store_true',
                   help='Use a file instead of serial port')
    args = p.parse_args()


    import halucinator.hal_log as hal_log
    hal_log.setLogConfig()

    io_server = IOServer(args.rx_port, args.tx_port)
    serial = SerialTunnel(args.port,io_server,args.baud, args.use_file)

    io_server.start()

    try:
        while(1):
            data = serial.host_port.read(1)
            if len(data) > 0:
                print(f"Got {data}")
                log.debug(f"Got {data}")
                serial.send_data(args.id,[data])

    except KeyboardInterrupt:
        pass
    log.info("Shutting Down")
    io_server.shutdown()
    # io_server.join()

   