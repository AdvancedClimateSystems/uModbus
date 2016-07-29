from serial import serial_for_url

from umodbus import conf
from umodbus.server.serial import get_server
from umodbus.server.serial.rtu import RTUServer

conf.SIGNED_VALUES = True

s = serial_for_url('loop://')
app = get_server(RTUServer, s)

import route
route.bind_routes(app)
