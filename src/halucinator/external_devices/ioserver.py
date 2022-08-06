# Copyright 2019 National Technology & Engineering Solutions of Sandia, LLC (NTESS).
# Under the terms of Contract DE-NA0003525 with NTESS, the U.S. Government retains
# certain rights in this software.

import binascii
import logging
import time
from threading import Event, Thread

import zmq

from halucinator.peripheral_models.peripheral_server import decode_zmq_msg, encode_zmq_msg

log = logging.getLogger(__name__)


class IOServer(Thread):
    def __init__(self, rx_port=5556, tx_port=5555, log_file=None):
        Thread.__init__(self)
        self.rx_port = rx_port
        self.tx_port = tx_port
        self.__stop = Event()
        self.context = zmq.Context()
        io2hal_pipe = "ipc:///tmp/Halucinator2IoServer%i" % self.rx_port
        self.rx_socket = self.context.socket(zmq.SUB)
        self.rx_socket.connect(io2hal_pipe)
        print(f"Connected to {io2hal_pipe}")

        hal2io_pipe = "ipc:///tmp/IoServer2Halucinator%i" % self.tx_port
        self.tx_socket = self.context.socket(zmq.PUB)
        self.tx_socket.connect(hal2io_pipe)
        print(f"Connected to {hal2io_pipe}")

        self.poller = zmq.Poller()
        self.poller.register(self.rx_socket, zmq.POLLIN)
        self.handlers = {}
        self.packet_log = None
        if log_file is not None:
            self.packet_log = open(log_file, "wt")
            self.packet_log.write("Direction, Time, Topic, Data\n")

    def register_topic(self, topic, method):
        log.debug("Registering RX_Port: %s, Topic: %s" % (self.rx_port, topic))
        self.rx_socket.setsockopt(zmq.SUBSCRIBE, topic.encode("utf-8"))
        self.handlers[topic] = method

    def run(self):

        while not self.__stop.is_set():
            socks = dict(self.poller.poll(1000))
            if self.rx_socket in socks and socks[self.rx_socket] == zmq.POLLIN:
                msg = self.rx_socket.recv_string()
                log.debug("Received: %s" % str(msg))
                topic, data = decode_zmq_msg(msg)
                if self.packet_log:
                    self.packet_log.write(
                        "Sent, %i, %s, %s\n" % (time.time(), topic, binascii.hexlify(data["frame"]))
                    )
                    self.packet_log.flush()
                method = self.handlers[topic]
                method(self, data)
        log.debug("IO Server Stopped")

    def shutdown(self):
        log.debug("Stopping Host IO Server")
        self.__stop.set()
        if self.packet_log:
            self.packet_log.close()

    def send_msg(self, topic, data):
        msg = encode_zmq_msg(topic, data)
        self.tx_socket.send_string(msg)
        if self.packet_log:
            # TODO, make logging more generic so will work for non-frames
            if "frame" in data:

                self.packet_log.write(
                    "Received, %i, %s, %s\n" % (time.time(), topic, binascii.hexlify(data["frame"]))
                )
                self.packet_log.flush()


def main():
    from argparse import ArgumentParser

    p = ArgumentParser()
    p.add_argument(
        "-r", "--rx_port", default=5556, help="Port number to receive zmq messages for IO on"
    )
    p.add_argument("-t", "--tx_port", default=5555, help="Port number to send IO messages via zmq")
    args = p.parse_args()

    import halucinator.hal_log as hal_log

    hal_log.setLogConfig()

    io_server = IOServer(args.rx_port, args.tx_port)
    io_server.start()

    try:
        while 1:
            topic = input("Topic:")
            msg_id = input("ID:")
            data = input("Data:")

            d = {"id": msg_id, "data": data}
            io_server.send_msg(topic, d)
    except KeyboardInterrupt:
        io_server.shutdown()
        # io_server.join()


if __name__ == "__main__":
    main()
