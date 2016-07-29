from serial import serial_for_url

from umodbus import conf
from umodbus.server.serial import get_server
from umodbus.server.serial.rtu import RTUServer

from tests.system import route

conf.SIGNED_VALUES = True

s = serial_for_url('loop://')
app = get_server(RTUServer, s)

route.bind_routes(app)
