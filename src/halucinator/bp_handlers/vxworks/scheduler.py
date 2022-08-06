# Copyright 2021 National Technology & Engineering Solutions of Sandia, LLC
# (NTESS). Under the terms of Contract DE-NA0003525 with NTESS,
# the U.S. Government retains certain rights in this software.

"""Scheduler module for VxWorks"""
import logging

from halucinator.bp_handlers.bp_handler import BPHandler, bp_handler

log = logging.getLogger(__name__)


class BColors:
    """For pretty coloring of messages"""

    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"


class Scheduler(BPHandler):
    """Scheduler Class BP handler"""

    def __init__(self, tcb):
        """
        VxWorks Scheduler Functions instrumentation

        config file entry
        - class
          class_args: {tcb: (address of TCB)}
        """
        self.last_task = None
        self.tcb = tcb

    @bp_handler(["reschedule"])
    def reschedule(self, qemu, bp_addr):
        """reschedule"""
        log.debug("reschedule")
        return False, None

    @bp_handler(["windResume"])
    def wind_resume(self, qemu, bp_addr):
        """wind_resume"""
        log.debug("wind_resume")
        return False, None

    @bp_handler(["workQDoWork"])
    def work_q_do_work(self, qemu, bp_addr):
        """work_q_do_work"""
        log.debug("work_q_do_work")
        return False, None

    @bp_handler(["taskDestroy"])
    def task_destroy(self, qemu, bp_addr):
        """task_destroy"""
        tid_ptr = qemu.read_memory(self.tcb, 4, 1)
        log.debug(BColors.FAIL + "TASK DESTROYED")
        log.debug("Task Name: %s" % qemu.read_string(qemu.read_memory(tid_ptr + 0x34, 4, 1)))
        log.debug("Exit Code: %s" % hex(qemu.read_memory(tid_ptr + 0x88, 4, 1)))

        return False, None

    @bp_handler(["task_switch"])
    def task_switch(self, qemu, bp_addr):
        """task_switch"""
        c_tcb = qemu.read_memory(self.tcb, 4, 1)
        tcb = qemu.read_memory(c_tcb, 4, 0x21)
        offset_lookup = {
            "Status": tcb[int(0x3C / 0x4)],
            "Priority": tcb[int(0x40 / 0x4)],
            "PriNormal": tcb[int(0x44 / 0x4)],
            "priMutexCnt": tcb[int(0x48 / 0x4)],
            "lockCnt": tcb[int(0x50 / 0x4)],
            "entry": hex(tcb[int(0x74 / 0x4)]),
            "pStackBase": hex(tcb[int(0x78 / 0x4)]),
            "pStackLimit": hex(tcb[int(0x7C / 0x4)]),
            "pStackEnd": hex(tcb[int(0x80 / 0x4)]),
        }
        if self.last_task == qemu.read_string(tcb[int(0x34 / 0x4)]):
            pass
        else:
            self.last_task = qemu.read_string(tcb[int(0x34 / 0x4)])
            log.debug(BColors.OKBLUE + "TASK SWITCH")
            log.debug("Task Name: %s" % qemu.read_string(tcb[int(0x34 / 0x4)]))
            for key, value in offset_lookup.items():
                log.debug(" %s: %s" % (key, value))
            log.debug(BColors.ENDC)
        return False, None
