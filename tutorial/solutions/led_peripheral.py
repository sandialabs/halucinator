# Copyright 2020 National Technology & Engineering Solutions of Sandia, LLC (NTESS).
# Under the terms of Contract DE-NA0003525 with NTESS, the U.S. Government retains
# certain rights in this software.

import logging

from halucinator.peripheral_models import peripheral_server

log = logging.getLogger(__name__)


# STEP 1.  Register the class with the peripheral server
#    using the @peripheral_server.peripheral_model decorator
@peripheral_server.peripheral_model
class LEDModel(object):
    @classmethod
    # STEP 2.  Add the @peripheral_server.tx_msg decorater to transmit the return
    #    value of this method out the peripheral server with topic
    #    'Peripheral.LEDModel.led_status'
    @peripheral_server.tx_msg
    def led_status(cls, led_id, status):
        log.debug("LED Status %s: %s" % (led_id, status))
        # STEP 3. Compose a dictionary with the keys 'id' and 'status' and return it
        return {"id": led_id, "status": status}

    @classmethod
    def led_off(cls, led_id):
        log.debug("LED Off %s" % (led_id))
        # STEP 4.  Call the led_status method providing False for off
        cls.led_status(led_id, False)

    @classmethod
    def led_on(cls, led_id):
        log.debug("LED On %s" % (led_id))
        # STEP 5.  Call the led_status method providing True for On
        cls.led_status(led_id, True)
