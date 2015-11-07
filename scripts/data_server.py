#!/usr/bin/env python
import os
import logging
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                '../'))

from umodbus.server import get_server
from umodbus.utils import log_to_stream

fmt = '%(asctime)s - %(name)s - %(levelname)-8s - %(module)s.%(funcName)s: ' +\
      '%(message)s'

log_to_stream(level=logging.DEBUG, fmt=fmt)
server = get_server('localhost', 1027)

@server.route(slave_ids=[1], function_codes=[1, 2], addresses=set(range(100, 200)))
def single_bit(slave_id, address):
    return address % 2


@server.route(slave_ids=[1], function_codes=[3, 4], addresses=list(range(100, 200)))
def return_address(slave_id, address):
    """ Return address. """
    print('Called with slave_id {0} and address {1}.'.format(slave_id, address))
    return address

@server.route(slave_ids=[1], function_codes=[3, 4], addresses=set(range(100, 200)))
def multi_bit(slave_id, address):
    return address


@server.route(slave_ids=[1], function_codes=[5, 6], addresses=set(range(100, 200)))
def single_coil(slave_id, address, value):
    print(value)



@server.route(slave_ids=[1], function_codes=[15, 16], addresses=set(range(100, 200)))
def multiple_coils(slave_id, address, value):
    print(value)

if __name__ == '__main__':
    try:
        server.serve_forever()
    finally:
        server.shutdown()
