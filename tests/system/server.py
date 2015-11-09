from umodbus import get_server

app = get_server('localhost', 0)


@app.route(slave_ids=[1], function_codes=[1, 2], addresses=list(range(0, 10)))
def read_coils(slave_id, address):
    return address % 2


@app.route(slave_ids=[1], function_codes=[1, 2], addresses=[666])
def failure(slave_id, address):
    raise Exception
