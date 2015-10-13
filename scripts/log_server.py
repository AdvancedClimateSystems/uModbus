#!/usr/bin/env python
import sys
from logbook import StreamHandler, info
from socketserver import BaseRequestHandler, TCPServer

StreamHandler(sys.stdout).push_application()


class LogHandler(BaseRequestHandler):
    def handle(self):
        self.data = self.request.recv(1024).strip()
        info('{0} wrote: {1}'.format(self.client_address[0], self.data))
        self.request.sendall(self.data)


if __name__ == '__main__':
    HOST, PORT = 'localhost',1337
    server = TCPServer((HOST, PORT), LogHandler)

    try:
        server.serve_forever()
    finally:
        server.shutdown()
