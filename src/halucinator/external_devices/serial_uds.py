# Copyright 2019 National Technology & Engineering Solutions of Sandia, LLC (NTESS).
# Under the terms of Contract DE-NA0003525 with NTESS, the U.S. Government retains
# certain rights in this software.


import logging
import socket
import time

from halucinator.external_devices.ioserver import IOServer

log = logging.getLogger(__name__)


class UDSTunnel(object):
    def __init__(self, socket_addr, ioserver):
        self.ioserver = ioserver
        self.prev_print = None

        self.host_port = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.host_port.connect(socket_addr)
        log.debug(f"Connected to {socket_addr}")
        ioserver.register_topic("Peripheral.UTTYModel.tx_buf", self.write_handler)

    def write_handler(self, ioserver, msg):
        tx_bytes = msg["chars"]
        print("Got %s From VM" % str(tx_bytes))
        self.host_port.send(tx_bytes)

    def send_data(self, msg_id, chars):
        data = {"interface_id": msg_id, "char": chars}
        self.ioserver.send_msg("Peripheral.UTTYModel.rx_char_or_buf", data)

    def shutdown(self):
        self.host_port.close()


if __name__ == "__main__":
    from argparse import ArgumentParser

    p = ArgumentParser()
    p.add_argument(
        "-r", "--rx_port", default=5556, help="Port number to receive zmq messages for IO on"
    )
    p.add_argument("-t", "--tx_port", default=5555, help="Port number to send IO messages via zmq")
    p.add_argument("--id", default="COM1", help="Emulation Interace to listen to")
    p.add_argument("-a", "--addr", required=True, help="Unix socket name")
    args = p.parse_args()

    import halucinator.hal_log as hal_log

    hal_log.setLogConfig()

    io_server = IOServer(args.rx_port, args.tx_port)
    uds_tunnel = UDSTunnel(args.addr, io_server)

    io_server.start()

    try:
        while 1:
            data = uds_tunnel.host_port.recv(1)
            if len(data) > 0:
                print(f"Got {data}")
                log.debug(f"Got {data}")
                uds_tunnel.send_data(args.id, [data])
                time.sleep(25)

    except KeyboardInterrupt:
        pass
    log.info("Shutting Down")
    uds_tunnel.shutdown()
    io_server.shutdown()
    # io_server.join()
