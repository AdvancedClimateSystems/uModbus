#!/usr/bin/env python
# scripts/examples/simple_data_store.py
import logging
from socketserver import TCPServer
from collections import defaultdict

from umodbus import conf
from umodbus.server import get_server
from umodbus.server.tcp import RequestHandler
from umodbus.utils import log_to_stream

# Add stream handler to logger 'uModbus'.
log_to_stream(level=logging.DEBUG)

# A very simple data store which maps addresses against their values.
data_store = defaultdict(int)

# Enable values to be signed (default is False).
conf.SIGNED_VALUES = True

TCPServer.allow_reuse_address = True
app = get_server(TCPServer, ('localhost', 502), RequestHandler)


@app.route(slave_ids=[1], function_codes=[1, 2], addresses=list(range(0, 10)))
def read_data_store(slave_id, function_code, address):
    """" Return value of address. """
    return data_store[address]


@app.route(slave_ids=[1], function_codes=[5, 15], addresses=list(range(0, 10)))
def write_data_store(slave_id, function_code, address, value):
    """" Set value for address. """
    data_store[address] = value

if __name__ == '__main__':
    try:
        app.serve_forever()
    finally:
        app.shutdown()
        app.server_close()
