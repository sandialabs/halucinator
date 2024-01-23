# Copyright 2019 National Technology & Engineering Solutions of Sandia, LLC (NTESS).
# Under the terms of Contract DE-NA0003525 with NTESS, the U.S. Government retains
# certain rights in this software.
"""
Defines the peripheral model decorators and the methods for
working with breakpoints
"""

import sys
from functools import wraps
import importlib
import logging
from .. import hal_log as hal_log_conf
from .. import hal_stats

log = logging.getLogger(__name__)

hal_log = hal_log_conf.getHalLogger()


hal_stats.stats["used_intercepts"] = set()
hal_stats.stats["bypassed_funcs"] = set()

# LUT to map bp to addr
__bp_addr_lut = {}


def tx_map(per_model_funct):
    """
    Decorator that maps this function to the peripheral model that supports
    it. It registers the intercept and calls the
    Usage:  @intercept_tx_map(<PeripheralModel.method>, ['Funct1', 'Funct2'])

    Args:
        per_model_funct(PeripheralModel.method):  Method of child class that
            this method is providing a mapping for
    """
    print("In: intercept_tx_map", per_model_funct)

    def intercept_decorator(func):
        print("In: intercept_decorator", func)

        @wraps(func)
        def intercept_wrapper(self, target, bp_addr):
            bypass, ret_value, msg = func(self, target, bp_addr)
            log.debug("Values: %s", msg)
            per_model_funct(*msg)
            return bypass, ret_value

        return intercept_wrapper

    return intercept_decorator


def rx_map(per_model_funct):
    """
    Decorator that maps this function to the peripheral model that supports
    it. It registers the intercept and calls the
    Usage:  @intercept_rx_map(<PeripheralModel.method>, ['Funct1', 'Funct2'])

    Args:
        per_model_funct(PeripheralModel.method):  Method of child class that
            this method is providing a mapping for
    """
    print("In: intercept_rx_map", per_model_funct)

    def intercept_decorator(func):
        print("In: intercept_decorator", func)

        @wraps(func)
        def intercept_wrapper(self, target, bp_addr):
            models_inputs = per_model_funct()
            return func(self, target, bp_addr, *models_inputs)

        return intercept_wrapper

    return intercept_decorator


initalized_classes = {}
bp2handler_lut = {}


def get_bp_handler(intercept):
    """
    gets the bp_handler class from the config file class name.
    Instantiates it if has not been instantiated before if
    has it just returns the instantiated instance

    :param intercept: HALInterceptConfig
    """
    split_str = intercept.cls.split(".")

    module_str = ".".join(split_str[:-1])
    class_str = split_str[-1]
    module = importlib.import_module(module_str)

    cls_obj = getattr(module, class_str)
    if cls_obj in initalized_classes:
        bp_class = initalized_classes[cls_obj]
    else:
        if intercept.class_args is not None:
            log.info("Class: %s", cls_obj)
            log.info("Class Args: %s", intercept.class_args)
            bp_class = cls_obj(**intercept.class_args)
        else:
            bp_class = cls_obj()
        initalized_classes[cls_obj] = bp_class
    return bp_class


def register_bp_handler(qemu, intercept):
    """
    Registers a BP handler for specific address

    :param qemu:    Avatar qemu target
    :param intercept: HALInterceptConfig
    """
    if intercept.bp_addr is None:
        log.debug("No address specified for %s ignoring intercept", intercept)
        return None
    bp_cls = get_bp_handler(intercept)

    try:
        if intercept.registration_args is not None:
            log.info(
                "Registering BP Handler: %s.%s : %s, registration_args: %s",
                intercept.cls,
                intercept.function,
                hex(intercept.bp_addr),
                str(intercept.registration_args),
            )
            handler = bp_cls.register_handler(
                qemu,
                intercept.bp_addr,
                intercept.function,
                **intercept.registration_args
            )
        else:
            log.info(
                "Registering BP Handler: %s.%s : %s",
                intercept.cls,
                intercept.function,
                hex(intercept.bp_addr),
            )
            handler = bp_cls.register_handler(
                qemu, intercept.bp_addr, intercept.function
            )
    except ValueError as error:
        hal_log.error("Invalid BP registration failed for %s", intercept)
        hal_log.error(error)
        hal_log.error("Input registration args are %s", intercept.registration_args)
        # exit(-1)
        sys.exit(-1)

    if intercept.run_once:
        bp_temp = True
        log.debug("Setting as Tempory")
    else:
        bp_temp = False

    if intercept.watchpoint:
        if intercept.watchpoint == "r":
            breakpoint_num = qemu.set_watchpoint(
                intercept.bp_addr, write=False, read=True
            )
        elif intercept.watchpoint == "w":
            breakpoint_num = qemu.set_watchpoint(
                intercept.bp_addr, write=True, read=False
            )

        else:
            breakpoint_num = qemu.set_watchpoint(
                intercept.bp_addr, write=True, read=True
            )

    else:
        breakpoint_num = qemu.set_breakpoint(intercept.bp_addr, temporary=bp_temp)

    hal_stats.stats[breakpoint_num] = {
        "function": intercept.function,
        "desc": str(intercept),
        "count": 0,
        "method": handler.__name__,
    }

    __bp_addr_lut[breakpoint_num] = intercept.bp_addr
    bp2handler_lut[breakpoint_num] = (bp_cls, handler)
    log.info("BP is %i", breakpoint_num)
    return breakpoint_num


def interceptor(avatar, message):  # pylint: disable=unused-argument
    """
    Callback for Avatar2 break point watchman.  It then dispatches to
    correct handler
    """
    # HERE
    if message.__class__.__name__ == "WatchpointHitMessage":
        breakpoint_num = int(message.watchpoint_number)
    else:
        breakpoint_num = int(message.breakpoint_number)
    target = message.origin

    # prog_counter = target.regs.pc & 0xFFFFFFFE  # Clear Thumb bit
    prog_counter = __bp_addr_lut[breakpoint_num]

    try:
        cls, method = bp2handler_lut[breakpoint_num]
        hal_stats.stats[breakpoint_num]["count"] += 1
        hal_stats.write_on_update(
            "used_intercepts", hal_stats.stats[breakpoint_num]["function"]
        )
    except KeyError:
        log.info("BP Has no handler")
        return
    # print method
    try:
        intercept, ret_value = method(cls, target, prog_counter)

        if intercept:
            hal_stats.write_on_update(
                "bypassed_funcs", hal_stats.stats[breakpoint_num]["function"]
            )
    except Exception as err:
        log.exception("Error executing handler %s", repr(method))
        raise err
    if intercept:
        target.execute_return(ret_value)
    target.cont()
