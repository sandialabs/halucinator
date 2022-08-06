# Copyright 2019 National Technology & Engineering Solutions of Sandia, LLC (NTESS).
# Under the terms of Contract DE-NA0003525 with NTESS, the U.S. Government retains
# certain rights in this software.

import logging
from threading import Event, Thread

from halucinator.peripheral_models import peripheral_server
from halucinator.peripheral_models.interrupts import Interrupts

log = logging.getLogger(__name__)


# Register the pub/sub calls and methods that need mapped
@peripheral_server.peripheral_model
class TimerModel(object):

    active_timers = {}

    @classmethod
    def start_timer(cls, name, isr_num, rate):
        log.debug("Starting timer: %s" % name)
        if name not in cls.active_timers:
            stop_event = Event()
            t = TimerIRQ(stop_event, name, isr_num, rate)
            cls.active_timers[name] = (stop_event, t)
            t.start()

    @classmethod
    def stop_timer(cls, name):
        if name in cls.active_timers:
            (stop_event, t) = cls.active_timers[name]
            stop_event.set()

    @classmethod
    def clear_timer(cls, irq_name):
        # cls.stop_timer(name)
        Interrupts.clear_active(irq_name)

    @classmethod
    def shutdown(cls):
        for key, (stop_event, t) in list(cls.active_timers.items()):
            stop_event.set()


class TimerIRQ(Thread):
    def __init__(self, event, irq_name, irq_num, rate):
        Thread.__init__(self)
        self.stopped = event
        self.name = irq_name
        self.irq_num = irq_num
        self.rate = rate

    def run(self):
        while not self.stopped.wait(self.rate):
            log.info("Sending IRQ: %s" % self.irq_num)
            Interrupts.set_active_qmp(self.irq_num)
            # call a function
