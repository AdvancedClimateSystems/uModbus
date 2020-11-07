from serial import serial_for_url

from umodbus import conf
from umodbus.utils import recv_exactly
from umodbus.server.serial import get_server
from umodbus.server.serial.rtu import RTUServer

from tests.system import route

conf.SIGNED_VALUES = True


class StreamReader:

    def __init__(self, serial_port):
        self.serial_port = serial_port

    async def readexactly(self, n):
        return recv_exactly(self.serial_port.read, n)

    async def read(self, n):
        return self.serial_port.read(n)


class StreamWriter:

    def __init__(self, serial_port):
        self.serial_port = serial_port

    def write(self, data):
        self.serial_port.write(data)
        self.serial_port.flush()
        app.serve_once()

    async def drain(self):
        pass


s = serial_for_url('loop://')
app = get_server(RTUServer, s)

route.bind_routes(app)
