# -*- coding: UTF-8 -*-
__author__ = 'lijie'
import json
import time
import codecs
import os
import hashlib
import base64
import mimetypes
import settings
import struct


# Response
mimetypes.init()


class HttpResponseBasic(object):
    """
    HTTP 基类应答


    """
    def __init__(self, code, status, headers):
        self.code = code
        self.status = status
        self.headers = dict(**headers)
        self.headers['Server'] = "mghttpd/v2.12"
        self.headers['Date'] = time.strftime("%a, %d %b %Y %H:%M:%S")
        self.body = ''

        self.add_cookie = list()

        # 已经发送了应答头部
        self.header_sent = False
        # 已经发送了应答主体
        self.body_sent = False

    def is_header_sent(self):
        return self.header_sent

    def is_body_sent(self):
        return self.body_sent

    def response_header(self, request):
        self.header_sent = True

        first_line = ' '.join([request.version, str(self.code), self.status])
        head_lines = '\r\n'.join(['%s: %s' % (key, value) for key, value in self.headers.items()])
        headers = '\r\n'.join([first_line, head_lines, '\r\n'])
        data = headers.encode()
        request.write(data)

    def response_body(self, request):
        self.body_sent = True

        if self.body is not None and len(self.body) > 0:
            request.write(self.body.encode())

    def on_body_received(self, request, data):
        pass

    def set_cookie(self, name, value, ttl, expires, path):
        pass


class HttpResponseHtml(HttpResponseBasic):
    def __init__(self, body, code=None, status=None, headers=None):
        if code is None:
            code = 200

        if status is None:
            status = 'OK'

        if headers is None:
            headers = dict()

        headers['Content-Length'] = len(body)
        headers['Content-Type'] = "text/html; charset=utf-8"
        super(self.__class__, self).__init__(code, status, headers)
        self.body = body


class HttpResponse(HttpResponseHtml):
    def __init__(self, body, code=None, status=None, headers=None):
        super(self.__class__, self).__init__(body, code, status, headers)


class HttpResponseJson(HttpResponseBasic):
    def __init__(self, obj, code=None, status=None, headers=None):
        if code is None:
            code = 200

        if status is None:
            status = 'OK'

        if headers is None:
            headers = dict()

        headers['Content-Type'] = 'application/json'
        self.obj = obj
        super(self.__class__, self).__init__(code, status, headers)

    def response_body(self, request):
        self.body_sent = True
        json.dump(self.obj, request, ensure_ascii=False)


class HttpNormalFile(HttpResponseBasic):
    def __init__(self, full_path):
        self.full_path = full_path
        super().__init__(200, 'OK', dict())

        self.headers['Content-Type'] = mimetypes.guess_type(full_path)[0]
        self.headers['Content-Length'] = os.stat(full_path).st_size
        self.file = self.read_some()

    def read_some(self):
        with codecs.open(self.full_path, 'rb') as file:
            while True:
                data = file.read(settings.max_transport_unit_size)
                if len(data) > 0:
                    yield data
                else:
                    break

    def response_body(self, request):
        data = b''
        try:
            data = self.file.__next__()
        except StopIteration:
            self.body_sent = True

        if len(data) > 0:
            request.write(data)


class HttpResponse404(HttpResponseBasic):
    def __init__(self):
        super().__init__(404, "Not Found", dict())


class HttpResponseNotFound(HttpResponse404):
    def __init__(self):
        super().__init__()


class HttpResponseRedirect(HttpResponseBasic):
    def __init__(self, target):
        super().__init__(301, "Moved Permanently", {'Location': target})
        self.body_sent = True


class HttpResponseInnerError(HttpResponseBasic):
    def __init__(self):
        super().__init__(500, "Inner Error", dict())
        self.body_sent = True


class HttpResponseBadRequest(HttpResponseBasic):
    def __init__(self):
        super().__init__(400, "Bad Request", dict())
        self.body_sent = True


class HttpResponseLongPoll(HttpResponseBasic):
    pass


class HttpResponseWebSocket(HttpResponseBasic):
    def __init__(self, key, version):
        super().__init__(101, 'Switching Protocols', dict())
        self.magic = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
        self.headers['Upgrade'] = 'websocket'
        self.headers['Connection'] = 'Upgrade'
        self.headers['Sec-WebSocket-Accept'] = self.calc_handshack_key(key, version)
        #self.headers['Sec-WebSocket-Protocol'] = 'soap, wamp'

        self.born = time.time()

    def calc_handshack_key(self, key, version):
        x = ''.join([key, self.magic])
        sha1 = hashlib.sha1()
        sha1.update(x.encode())
        h = sha1.digest()
        o = base64.encodebytes(h).decode()
        return o.rstrip()

    def on_body_received(self, reqeust, data):
        print('FIN:', (data[0]&0x80) >> 7)
        print('RSV1, RSV2, RSV3:', (data[0]&0x40)>>6, (data[0]&0x20)>>5, (data[0]&0x10)>>4)
        print('opcode:', (data[0]&0x0f))
        print('mask:', (data[1]&0x80) >> 7)
        if (data[1] & 0x80) >> 7 == 0:
            self.body_sent = True
            print("** Error: mask bit not 1.")
            return

        shit_len = data[1] & 0x7f
        if shit_len <= 125:
            pack_len = shit_len
            mask = data[2:6]
            payload = data[6:]
        elif shit_len == 126:
            pack_len = struct.unpack(">H", data[2:4])[0]
            mask = data[4:8]
            payload = data[8:]
        else:
            pack_len = struct.unpack(">Q", data[2:10])[0]
            mask = data[10:14]
            payload = data[14:]
        print("length: ", pack_len)

        print(len(mask), mask, len(payload), payload)
        origin = u''.join([chr(b ^ mask[i % len(mask)]) for i, b in enumerate(payload)])
        print(origin)

    def response_body(self, request):
        delta = time.time() - self.born
        frame = self.send_text(b'hello world!')
        request.write(frame)

        frame = self.send_text(b'x' * 126)
        request.write(frame)

        frame = self.send_text(b'y' * 127)
        request.write(frame)

        frame = self.send_text(b'z' * 300)
        request.write(frame)

        frame = self.send_bin(b'z' * 300)
        request.write(frame)

        self.body_sent = True

    #---------------------------
    def send_text(self, data):
        size = len(data)

        if size <= 125:
            length = struct.pack('B', size)
        elif size < 65535:
            length = struct.pack('>BH', 126, size)
        else:
            length = struct.pack('>BQ', 127, size)

        return b''.join([b'\x81', length, data])

    def send_bin(self, data):
        size = len(data)

        if size <= 125:
            length = struct.pack('B', size)
        elif size < 65535:
            length = struct.pack('>BH', 126, size)
        else:
            length = struct.pack('>BQ', 127, size)

        return b''.join([b'\x82', length, data])

    def on_ping(self):
        pass

    def ping(self):
        pass

    def on_pong(self):
        pass

    def pong(self):
        pass
