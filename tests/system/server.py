from umodbus import get_server

app = get_server('localhost', 0)


@app.route(slave_ids=[1], function_codes=[1, 2], addresses=list(range(0, 10)))
def read_status(slave_id, address):
    return address % 2


@app.route(slave_ids=[1], function_codes=[3, 4], addresses=list(range(0, 10)))
def read_register(slave_id, address):
    return address


@app.route(slave_ids=[1], function_codes=[5, 15], addresses=list(range(0, 10)))
def write_status(slave_id, address, value):
    pass


@app.route(slave_ids=[1], function_codes=[6, 16], addresses=list(range(0, 10)))
def write_register(slave_id, address, value):
    pass


@app.route(slave_ids=[1], function_codes=[1, 2, 3, 4, 5, 6, 15, 16],
           addresses=[666])
def failure(*args, **kwargs):
    raise Exception
