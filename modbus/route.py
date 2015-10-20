import sys
from logbook import StreamHandler, debug, info

StreamHandler(sys.stdout).push_application()


class Map:

    def __init__(self):
        self._rules = []

    def add_rule(self, endpoint, slave_ids, function_codes, addresses):
        debug('Register {0} for slave id\'s {1}, function codes {2} and '
              'addresses {3}.'.format(endpoint, slave_ids, function_codes,
                                      addresses))

        self._rules.append(DataRule(endpoint, slave_ids, function_codes,
                                    addresses))

    def match(self, slave_id, function_code, address):
        request = 'slave_id: {0}, function_code: {1}, address: {2}'.\
            format(slave_id, function_code, address)

        for rule in self._rules:
            if rule.match(slave_id, function_code, address):
                debug('Found match "{0}" for request {1}.'.format(rule.endpoint, request))
                return rule.endpoint

        debug('No match found for {0}.'.format(request))


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
