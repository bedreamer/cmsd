# -*- coding: UTF-8 -*-
__author__ = 'lijie'
import select
import socket
from selector import Selector
from request import HttpRequest


socket.socket.write = socket.socket.send


class TCPServerBasic(object):
    """
    TCP服务器
    usage:
        server = TCPServer('0.0.0.0', 8000)
        server.run_forever()
    """
    def __init__(self, ip, port, ReqeustHandle, **kwargs):
        self.loop = Selector()

        self.ip = ip
        self.port = port
        self.RequestHandle = ReqeustHandle
        self.kwargs = kwargs

        self.server = socket.socket()
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)

    def file(self):
        return self.server

    def setup(self, selector):
        selector.register(self, Selector.EVREADABLE)

    def on_readable(self):
        """
        服务器句柄可读
        """
        conn, addr = self.server.accept()

        connection = self.RequestHandle(conn, addr, **self.kwargs)

        hold = connection.begin()
        if hold is False:
            print("new connection aborted by", self.RequestHandle.__name__)
            connection.end()
        else:
            print("new connection accepted.")
            connection.setup(self.loop)

    def on_writable(self):
        raise NotImplemented

    def run_forever(self):
        self.server.bind((self.ip, self.port))
        self.server.listen(15)
        self.setup(self.loop)
        self.loop.run_forever()


if __name__ == '__main__':
    server = TCPServerBasic('127.0.0.1', 8000, HttpRequest)
    server.run_forever()
