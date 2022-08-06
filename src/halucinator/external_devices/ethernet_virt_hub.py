# Copyright 2019 National Technology & Engineering Solutions of Sandia, LLC (NTESS).
# Under the terms of Contract DE-NA0003525 with NTESS, the U.S. Government retains
# certain rights in this software.

import logging
import time

from halucinator.external_devices.host_ethernet_server import HostEthernetServer
from halucinator.external_devices.ioserver import IOServer
from halucinator.external_devices.trigger_interrupt import SendInterrupt

log = logging.getLogger(__name__)


class VirtualEthHub(object):
    def __init__(self, ioservers=[]):
        """
        args:
        ioserver:  list of ioservers to bridge together
        """
        self.ioservers = []
        self.host_socket = None
        self.host_interface = None
        for server in ioservers:
            self.add_server(server)

    def add_server(self, ioserver):
        self.ioservers.append(ioserver)
        ioserver.register_topic("Peripheral.EthernetModel.tx_frame", self.received_frame)

    def received_frame(self, from_server, msg):
        for server in self.ioservers:
            log.info("Forwarding, msg")
            if server != from_server:
                server.send_msg("Peripheral.EthernetModel.rx_frame", msg)

    def shutdown(self):
        for server in self.ioservers:
            log.debug("Eth Hub:Shutting Down")
            server.shutdown()


def main():
    from argparse import ArgumentParser

    p = ArgumentParser()
    p.add_argument(
        "-r",
        "--rx_ports",
        nargs="+",
        default=[5556, 5558],
        help="Port numbers to receive zmq messages for IO on",
    )
    p.add_argument(
        "-t",
        "--tx_ports",
        nargs="+",
        default=[5555, 5557],
        help="Port numbers to send IO messages via zmq, lenght must match --rx_ports",
    )
    p.add_argument(
        "-i", "--interface", required=False, default=None, help="Ethernet Interace to echo data on"
    )
    p.add_argument(
        "-p",
        "--enable_host_rx",
        required=False,
        default=False,
        action="store_true",
        help="Enable Receiving data from host interface, requires -i",
    )
    args = p.parse_args()

    if len(args.rx_ports) != len(args.tx_ports):
        print("Number of rx_ports and number of tx_ports must match")
        p.print_usage()
        quit(-1)

    logging.basicConfig()
    log.setLevel(logging.DEBUG)

    hub = VirtualEthHub()

    if args.interface is not None:
        host_eth = HostEthernetServer(args.interface, args.enable_host_rx)
        hub.add_server(host_eth)
        host_eth.start()

    for idx, rx_port in enumerate(args.rx_ports):
        print(idx)
        server = IOServer(rx_port, args.tx_ports[idx])
        hub.add_server(server)
        if idx == 0:
            interrupter = SendInterrupt(server)

        server.start()

    time.sleep(2)
    try:
        while 1:
            intr = input("ISR Num:")
            intr = int(intr)
            interrupter.trigger_interrupt(intr)

            pass
    except KeyboardInterrupt:
        pass
    log.info("Shutting Down")
    hub.shutdown()


if __name__ == "__main__":
    main()
