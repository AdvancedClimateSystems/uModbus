#!/usr/bin/env python
try:
    from socketserver import BaseRequestHandler, TCPServer
except ImportError:
    from socketserver import BaseRequestHandler, TCPServer


class LogHandler(BaseRequestHandler):
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print('{0} wrote: {1}'.format(self.client_address[0], self.data))
        self.request.sendall(self.data)


if __name__ == '__main__':
    HOST, PORT = 'localhost', 1338
    server = TCPServer((HOST, PORT), LogHandler)

    try:
        server.serve_forever()
    finally:
        server.shutdown()
