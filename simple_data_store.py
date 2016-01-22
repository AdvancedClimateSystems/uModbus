#!/usr/bin/env python
# scripts/examples/simple_data_store.py
import logging
from collections import defaultdict

from umodbus import get_server, conf
from umodbus.utils import log_to_stream

# Add stream handler to logger 'uModbus'.
log_to_stream(level=logging.DEBUG)

# A very simple data store which maps addresss against their values.
data_store = defaultdict(int)

conf.MULTI_BIT_VALUE_SIGNED = True
app = get_server('localhost', 1027)


@app.route(slave_ids=[1], function_codes=[3, 4], addresses=list(range(0, 10)))
def read_data_store(slave_id, address):
    """" Return value of address. """
    print('Retrieve {0} from address {1}.'.format(data_store[address], address))
    return data_store[address]


@app.route(slave_ids=[1], function_codes=[6, 16], addresses=list(range(0, 10)))
def write_data_store(slave_id, address, value):
    """" Set value for address. """
    print('Store {0} at address {1}.'.format(value, address))
    data_store[address] = value

if __name__ == '__main__':
    try:
        app.serve_forever()
    finally:
        app.shutdown()
        app.server_stop()
