# Copyright 2019 National Technology & Engineering Solutions of Sandia, LLC (NTESS).
# Under the terms of Contract DE-NA0003525 with NTESS, the U.S. Government retains
# certain rights in this software.

import logging
import socket
from collections import deque
from threading import Event, Thread

log = logging.getLogger(__name__)


class TCPModel(Thread):
    sock = None
    conn = None

    def __init__(self, *args, **kwargs):
        self.packet_queue = deque()
        self.packet_times = deque()  # Used to record reception time
        self.port = None
        self.sock = None
        self._shutdown = Event()
        Thread.__init__(self, *args, **kwargs)

    def listen(self, port):
        self.port = port
        self.start()

    def run(self):
        # Receive thread
        log.warn("TCP Listen thread started, port %d" % self.port)
        self.sock = socket.socket()
        self.sock.bind(("0.0.0.0", self.port))
        self.sock.listen(5)
        while not self._shutdown.is_set():
            conn, addr = self.sock.accept()
            self.conn = conn
            log.info("Received connection from %s on port %d" % (repr(addr), self.port))
            try:
                data = conn.recv(1500)
                while data:
                    self.packet_queue.append(data)
                    data = conn.recv(1500)
            except Exception as err:
                log.exception("Error reading data from client: %s", err)
            finally:
                if conn:
                    conn.close()
                self.conn = None
        log.info("Listen thread shutting down")

    def tx_packet(self, payload):
        """
        Creates the message that Peripheral.tx_msgs will send on this
        event
        """
        log.info("TCP: Sending %s" % payload)

        if self.conn is None:
            log.critical("Trying to send data when there's " + "no connected client!")
        else:
            self.conn.send(payload)
        # msg = {'port': port, 'payload': payload}
        # return msg

    def get_rx_packet(self):
        if self.packet_queue:
            log.info("TCP: Returning frame")
            pkt = self.packet_queue.popleft()
            return pkt
        else:
            log.info("TCP: No data to return")
            return None
