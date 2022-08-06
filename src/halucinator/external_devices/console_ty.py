# Copyright 2019 National Technology & Engineering Solutions of Sandia, LLC (NTESS).
# Under the terms of Contract DE-NA0003525 with NTESS, the U.S. Government retains
# certain rights in this software.


import logging

from halucinator.external_devices.ioserver import IOServer

log = logging.getLogger(__name__)


class TyConsole(object):
    def __init__(self, ioserver):
        self.ioserver = ioserver
        self.prev_print = None
        ioserver.register_topic("Peripheral.UTTYModel.tx_buf", self.write_handler)

    def write_handler(self, ioserver, msg):
        txt = msg["chars"].decode("utf-8")
        if self.prev_print == "-> " and txt == "-> ":
            return
        else:
            self.prev_print = txt
            print("%s" % txt, end=" ", flush=True)

    def send_data(self, msg_id, chars):
        data = {"interface_id": msg_id, "char": chars}
        self.ioserver.send_msg("Peripheral.UTTYModel.rx_char_or_buf", data)


if __name__ == "__main__":
    from argparse import ArgumentParser

    p = ArgumentParser()
    p.add_argument(
        "-r", "--rx_port", default=5556, help="Port number to receive zmq messages for IO on"
    )
    p.add_argument("-t", "--tx_port", default=5555, help="Port number to send IO messages via zmq")
    p.add_argument("--id", default="COM1", help="Emulation Interace to listen to")
    p.add_argument("-n", "--newline", default=False, action="store_true", help="Append Newline")
    args = p.parse_args()

    import halucinator.hal_log as hal_log

    hal_log.setLogConfig()

    io_server = IOServer(args.rx_port, args.tx_port)
    console = TyConsole(io_server)

    io_server.start()

    try:
        while 1:
            buff = []
            data = input()
            log.debug("Got %s" % str(data))
            if args.newline:
                data += "\n"
            if data == "\\n":
                data = "\r\n"
            elif data == "":
                break
            # d = {'id':args.id, 'data': data}
            for char in data:
                buff.append(ord(char))
            console.send_data(args.id, buff)
    except KeyboardInterrupt:
        pass
    log.info("Shutting Down")
    io_server.shutdown()
    # io_server.join()
