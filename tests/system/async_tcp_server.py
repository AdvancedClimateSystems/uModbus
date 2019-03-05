from umodbus import conf
from umodbus.server.tcp import get_async_server, RequestHandler

from tests.system import route

conf.SIGNED_VALUES = True

app = get_async_server(('localhost', 0), RequestHandler)

route.bind_routes(app)
