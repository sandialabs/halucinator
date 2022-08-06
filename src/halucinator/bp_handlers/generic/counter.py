# Copyright 2019 National Technology & Engineering Solutions of Sandia, LLC (NTESS).
# Under the terms of Contract DE-NA0003525 with NTESS, the U.S. Government retains
# certain rights in this software.

from halucinator.bp_handlers.bp_handler import BPHandler, bp_handler


class Counter(BPHandler):
    """
    Returns an increasing value for each addresss accessed

    Halucinator configuration usage:
    - class: halucinator.bp_handlers.Counter
      function: <func_name> (Can be anything)
      addr: <addr>
      registration_args:{increment:1} (Optional)
    """

    def __init__(self):
        self.increment = {}
        self.counts = {}

    def register_handler(self, qemu, addr, func_name, increment=1):
        """ """
        self.increment[addr] = increment
        self.counts[addr] = 0

        return Counter.get_value

    @bp_handler
    def get_value(self, qemu, addr):
        """
        Gets the counter value
        """
        self.counts[addr] += self.increment[addr]
        return True, self.counts[addr]
