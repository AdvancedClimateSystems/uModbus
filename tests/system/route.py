def bind_routes(server):
    server.route_map.add_rule(read_status, slave_ids=[1], function_codes=[1, 2], addresses=list(range(0, 10)))  # NOQA
    server.route_map.add_rule(read_register, slave_ids=[1], function_codes=[3, 4], addresses=list(range(0, 10)))  # NOQA
    server.route_map.add_rule(write_status, slave_ids=[1], function_codes=[5, 15], addresses=list(range(0, 10)))  # NOQA
    server.route_map.add_rule(write_register, slave_ids=[1], function_codes=[6, 16], addresses=list(range(0, 10)))  # NOQA
    server.route_map.add_rule(failure, slave_ids=[1], function_codes=[1, 2, 3, 4, 5, 6, 15, 16], addresses=[666])  # NOQA


def read_status(slave_id, function_code, address):
    return address % 2


def read_register(slave_id, function_code, address):
    return -address


def write_status(slave_id, function_code, address, value):
    pass


def write_register(slave_id, function_code, address, value):
    pass


def failure(*args, **kwargs):
    raise Exception
