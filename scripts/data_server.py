#!/usr/bin/env python
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                '../'))

from logbook import StreamHandler, info
from modbus.server import get_server

StreamHandler(sys.stdout).push_application()

server = get_server('localhost', 1026)


@server.route(slave_ids=[1], function_codes=[1, 2], addresses=set(range(100, 200)))
def single_bit(slave_id, address):
    return address % 2


@server.route(slave_ids=[1], function_codes=[3, 4], addresses=set(range(100, 200)))
def multi_bit(slave_id, address):
    return address

if __name__ == '__main__':
    try:
        server.serve_forever()
    finally:
        server.shutdown()
