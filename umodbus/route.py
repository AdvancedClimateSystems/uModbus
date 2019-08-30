class Map:
    def __init__(self):
        self._rules = []

    def add_rule(self, endpoint, slave_ids, function_codes, addresses, starting_address=None):
        self._rules.append(DataRule(endpoint, slave_ids, function_codes,
                                    addresses, starting_address))

    def match(self, slave_id, function_code, address, starting_address):
        for rule in self._rules:
            if rule.match(slave_id, function_code, address, starting_address):
                return rule.endpoint


class DataRule:
    def __init__(self, endpoint, slave_ids, function_codes, addresses, starting_address):
        self.endpoint = endpoint
        self.slave_ids = slave_ids
        self.function_codes = function_codes
        self.addresses = addresses
        self.starting_address = starting_address

    def match(self, slave_id, function_code, address, starting_address):
        if slave_id in self.slave_ids and \
            function_code in self.function_codes and \
            (True if self.starting_address is None else starting_address == self.starting_address) and \
                address in self.addresses:
                    return True

        return False
