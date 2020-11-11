#!/usr/bin/env python
# scripts/examples/simple_tcp_server.py
import logging
from socketserver import TCPServer
from collections import defaultdict
from argparse import ArgumentParser

from umodbus import conf
from umodbus.server.tcp import RequestHandler, get_server
from umodbus.utils import log_to_stream

# Add stream handler to logger 'uModbus'.
log_to_stream(level=logging.DEBUG)

# A very simple data store which maps addresses against their values.
data_store = defaultdict(int)

# Enable values to be signed (default is False).
conf.SIGNED_VALUES = True

# Parse command line arguments
parser = ArgumentParser()
parser.add_argument("-b", "--bind", default="localhost:502")

args = parser.parse_args()
if ":" not in args.bind:
    args.bind += ":502"
host, port = args.bind.rsplit(":", 1)
port = int(port)

TCPServer.allow_reuse_address = True
try:
    app = get_server(TCPServer, (host, port), RequestHandler)
except PermissionError:
    print("You don't have permission to bind on {}".format(args.bind))
    print("Hint: try with a different port (ex: --bind localhost:50200)")
    exit(1)


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
