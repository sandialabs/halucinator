# Copyright 2021 National Technology & Engineering Solutions of Sandia, LLC
# (NTESS). Under the terms of Contract DE-NA0003525 with NTESS,
# the U.S. Government retains certain rights in this software.

import logging
import sys

from halucinator import hal_log
from halucinator.bp_handlers.bp_handler import BPHandler, bp_handler

log = logging.getLogger(__name__)
hal_log = hal_log.getHalLogger()


class ReturnZero(BPHandler):
    """
    Break point handler that just returns zero

    Halucinator configuration usage:
    - class: halucinator.bp_handlers.ReturnZero
      function: <func_name> (Can be anything)
      registration_args: {silent:false}
      addr: <addr>
    """

    def __init__(self, filename=None):
        self.silent = {}
        self.func_names = {}

    def register_handler(self, qemu, addr, func_name, silent=False):
        self.silent[addr] = silent
        self.func_names[addr] = func_name
        return ReturnZero.return_zero

    @bp_handler
    def return_zero(self, qemu, addr):
        """
        Intercept Execution and return 0
        """
        if not self.silent[addr]:
            hal_log.info("ReturnZero: %s " % (self.func_names[addr]))
        return True, 0


class ReturnConstant(BPHandler):
    """
    Break point handler that returns a constant

    Halucinator configuration usage:
    - class: halucinator.bp_handlers.ReturnConstant
      function: <func_name> (Can be anything)
      registration_args: { ret_value:(value), silent:false}
      addr: <addr>
    """

    def __init__(self, filename=None):
        self.ret_values = {}
        self.silent = {}
        self.func_names = {}

    def register_handler(self, qemu, addr, func_name, ret_value=None, silent=False):
        self.ret_values[addr] = ret_value
        self.silent[addr] = ret_value
        self.func_names[addr] = func_name
        return ReturnConstant.return_constant

    @bp_handler
    def return_constant(self, qemu, addr):
        """
        Intercept Execution and return constant
        """
        if not self.silent[addr]:
            hal_log.info(
                "ReturnConstant: %s : %#x" % (self.func_names[addr], self.ret_values[addr])
            )
        return True, self.ret_values[addr]


class SkipFunc(BPHandler):
    """
    Break point handler that immediately returns from the function

    Halucinator configuration usage:
    - class: halucinator.bp_handlers.SkipFunc
      function: <func_name> (Can be anything)
      registration_args: {silent:false}
      addr: <addr>
    """

    def __init__(self, filename=None):
        self.silent = {}
        self.func_names = {}

    def register_handler(self, qemu, addr, func_name, silent=False):
        self.silent[addr] = silent
        self.func_names[addr] = func_name
        return SkipFunc.skip

    @bp_handler
    def skip(self, qemu, addr):
        """
        Just return
        """
        if not self.silent[addr]:
            hal_log.info("SkipFunc: %s " % (self.func_names[addr]))
        return True, None


class KillExit(BPHandler):
    """
    Break point handler that stops emulation and kills avatar/halucinator

    Halucinator configuration usage:
    - class: halucinator.bp_handlers.KillExit
      function: <func_name> (Can be anything)
      addr: <addr>
    """

    def __init__(self, filename=None):
        self.silent = {}
        self.func_names = {}

    def register_handler(self, qemu, addr, func_name, silent=False):
        self.silent[addr] = silent
        self.func_names[addr] = func_name
        return KillExit.kill_and_exit

    @bp_handler
    def kill_and_exit(self, qemu, addr):
        """
        Just return
        """
        if not self.silent[addr]:
            hal_log.info("Killing: %s " % (self.func_names[addr]))

        avatar = qemu.avatar
        avatar.stop()
        avatar.shutdown()
        sys.exit(0)


class SetRegisters(BPHandler):
    """
    Break point handler that changes a register

    Halucinator configuration usage:
    - class: halucinator.bp_handlers.SetRegisters
      function: <func_name> (Can be anything)
      registration_args: { registers: {'<reg_name>':<value>}}
      addr: <addr>
      addr_hook: True
    """

    def __init__(self, filename=None):
        self.silent = {}
        self.changes = {}

    def register_handler(self, qemu, addr, func_name, registers={}, silent=False):
        self.silent[addr] = silent
        log.debug(
            "Registering: %s at addr: %s with SetRegisters %s" % (func_name, hex(addr), registers)
        )
        self.changes[addr] = registers
        return SetRegisters.set_registers

    @bp_handler
    def set_registers(self, qemu, addr, *args):
        """
        Intercept Execution and return 0
        """
        for change in self.changes[addr].items():
            reg = change[0]
            value = change[1]
            qemu.write_register(reg, value)
            log.debug("set_register: %s : %#x" % (reg, value))
        return False, 0


class SetMemory(BPHandler):
    """
    Break point handler that changes a memory address

    Halucinator configuration usage:
    - class: halucinator.bp_handlers.SetMemory
      function: <func_name> (Can be anything)
      registration_args: { addresses: {<mem_address>: <value>}}
      addr: <addr>
    """

    def __init__(self, filename=None):
        self.silent = {}
        self.changes = {}

    def register_handler(self, qemu, addr, func_name, addresses={}, silent=False):
        self.silent[addr] = silent
        log.debug(
            "Registering: %s at addr: %s with SetMemory %s" % (func_name, hex(addr), addresses)
        )
        self.changes[addr] = addresses
        return SetMemory.set_memory

    @bp_handler
    def set_memory(self, qemu, addr, *args):
        """
        Intercept Execution and return 0
        """
        for change in self.changes[addr].items():
            address = change[0]
            value = change[1]
            qemu.write_memory(address, 4, value)
            log.debug("set_memory: %s : %#x" % (address, value))
        return False, 0
