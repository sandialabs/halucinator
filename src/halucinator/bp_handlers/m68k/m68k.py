from ..bp_handler import BPHandler, bp_handler
import logging, sys
from ... import hal_log

log = logging.getLogger(__name__)
hal_log = hal_log.getHalLogger()

class ReturnZero(BPHandler):
    '''
        Break point handler that just returns zero
        Halucinator configuration usage:
        - class: halucinator.bp_handlers.ReturnZero
          function: <func_name> (Can be anything)
          registration_args: {silent:false}
          addr: <addr>
    '''
    def __init__(self, filename=None):
        self.silent = {}
        self.func_names = {}

    def register_handler(self, qemu, addr, func_name, silent=False):
        self.silent[addr] = silent
        self.func_names[addr] = func_name
        return ReturnZero.return_zero

    @bp_handler
    def return_zero(self, qemu, addr):
        '''
            Intercept Execution and return 0
        '''
        if not self.silent[addr]:
            hal_log.info("ReturnZero: %s " %(self.func_names[addr]))
        return True, 0
