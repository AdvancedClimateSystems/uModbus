class Map:
    def __init__(self):
        self._rules = []

    def add_rule(self, endpoint, slave_ids, function_codes, addresses):
        self._rules.append(DataRule(endpoint, slave_ids, function_codes,
                                    addresses))

    def match(self, slave_id, function_code, address):
        for rule in self._rules:
            if rule.match(slave_id, function_code, address):
                return rule.endpoint


class DataRule:
    def __init__(self, endpoint, slave_ids, function_codes, addresses):
        self.endpoint = endpoint
        self.slave_ids = slave_ids
        self.function_codes = function_codes
        self.addresses = addresses

    def match(self, slave_id, function_code, address):
        if slave_id in self.slave_ids and\
            function_code in self.function_codes and \
                address in self.addresses:
                    return True

        return False
