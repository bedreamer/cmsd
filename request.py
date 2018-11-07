# -*- coding: UTF-8 -*-
__author__ = 'lijie'
import view
import path
import time
from selector import Selector


class HttpRequest:
    def __init__(self, conn, addr):
        self.conn = conn

        self.addr = addr
        self.down = False

        self.receive_bytes = b''
        self.receive_head_bytes = b''

        self.request_head_lines = None
        self.method, self.url, self.version, self.headers = None, None, None, None
        self.path, self.query_string = None, None

        self.response = None

    def file(self):
        return self.conn

    def mark_down(self):
        self.down = True

    def setup(self, selector):
        """
        called by selector while every single loop head
        :param selector:
        :return:
        """
        if not self.down:
            selector.register(self, Selector.EVREADABLE)
            if self.response is not None:
                selector.register(self, Selector.EVWRITABLE)
        else:
            selector.unregister(self, Selector.EVREADABLE)
            selector.unregister(self, Selector.EVWRITABLE)
            self.end()

    def read(self, n):
        try:
            return self.conn.recv(n)
        except:
            self.mark_down()
            return b''

    def write(self, data):
        try:
            if isinstance(data, str):
                return self.conn.send(data.encode())
            else:
                return self.conn.send(data)
        except Exception as e:
            print(e)
            self.mark_down()
            return None

    def on_readable(self):
        """
        called while self.file() is readable
        :return:
        """
        data = self.read(2048)
        if len(data) == 0:
            self.mark_down()
            return
        elif self.response is None:
            self.receive_bytes = b''.join([self.receive_bytes, data])
            terminal_idx = self.receive_bytes.find(b'\r\n\r\n')
            if terminal_idx < 0:
                return

            header_bytes = self.receive_bytes[:terminal_idx]
            remain_bytes = self.receive_head_bytes[terminal_idx + 4:]
            self.response = self.on_process_request_header(header_bytes, remain_bytes)
        else:
            self.response.on_body_received(self, data)

    def on_process_request_header(self, header_bytes, remain_bytes):
        self.request_head_lines = header_bytes.decode().split('\r\n')

        self.method, self.url, self.version = self.request_head_lines.pop(0).split(' ')
        self.headers = {line.split(':')[0]: line.split(':')[1].strip() for line in self.request_head_lines}

        if '?' in self.url:
            self.path, self.query_string = self.url.split('?')
        else:
            self.path, self.query_string = self.url, ''

        params_dict, processor = path.search_route_path(self)
        response = processor(self, **params_dict)
        if len(remain_bytes) > 0:
            response.on_body_received(self, remain_bytes)

        print(time.strftime("[%Y-%m-%d %H:%M:%S]"), self.method, self.path, response.code, response.status)
        return response

    def get_cookie(self):
        if 'Cookie' not in self.headers:
            return dict()
        else:
            pass

    def on_writable(self):
        """
        called while self.file() is writable
        :return:
        """
        if self.down is True:
            return

        if self.response is None:
            return

        if self.response.is_header_sent() is False:
            self.response.response_header(self)
        elif self.response.is_body_sent() is False:
            self.response.response_body(self)
        else:
            self.mark_down()

    def begin(self):
        """
        called by Server while a connection is incoming.
        test connection is hold neccessory or not
        :return: False connection will be aborted True will hold.
            if need hold this connection.
        """
        return True

    def end(self):
        """
        called by self while connection down or called by Server while reject a connection incoming.
        :return:
        """
        if self.conn:
            self.conn.close()
            self.conn = None
            #print("closed.")

