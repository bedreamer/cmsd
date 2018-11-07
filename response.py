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

    def mark_header_sent(self):
        self.header_sent = True

    def is_body_sent(self):
        return self.body_sent

    def mark_body_sent(self):
        self.body_sent = True

    def response_header(self, request):
        self.header_sent = True

        first_line = ' '.join([request.version, str(self.code), self.status])
        head_lines = '\r\n'.join(['%s: %s' % (key, value) for key, value in self.headers.items()])
        headers = '\r\n'.join([first_line, head_lines, '\r\n'])
        data = headers.encode()
        request.write(data)

    def response_body(self, request):
        self.mark_body_sent()

        if self.body is not None and len(self.body) > 0:
            request.write(self.body.encode())

    def on_body_received(self, request, data):
        pass

    def on_connection_down(self, request):
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
        self.mark_body_sent()
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
            self.mark_body_sent()

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
        self.mark_body_sent()


class HttpResponseInnerError(HttpResponseBasic):
    def __init__(self):
        super().__init__(500, "Inner Error", dict())
        self.mark_body_sent()


class HttpResponseBadRequest(HttpResponseBasic):
    def __init__(self):
        super().__init__(400, "Bad Request", dict())
        self.mark_body_sent()


class HttpResponseLongPoll(HttpResponseBasic):
    pass


class HttpResponseWebSocket(HttpResponseBasic):
    def __init__(self, key, version):
        super().__init__(101, 'Switching Protocols', dict())
        self.magic = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
        self.headers['Upgrade'] = 'websocket'
        self.headers['Connection'] = 'Upgrade'
        self.headers['Sec-WebSocket-Accept'] = self.calc_handshake_key(key, version)
        #self.headers['Sec-WebSocket-Protocol'] = 'soap, wamp'

        self.born = time.time()
        self.out = False
        self.recv_bytes = b''

        self.send_quene = list()

    def calc_handshake_key(self, key, version):
        x = ''.join([key, self.magic])
        sha1 = hashlib.sha1()
        sha1.update(x.encode())
        h = sha1.digest()
        o = base64.encodebytes(h).decode()
        return o.rstrip()

    def on_body_received(self, reqeust, data):
        self.recv_bytes = b''.join([self.recv_bytes, data])

        fin = (self.recv_bytes[0]&0x80) >> 7

        #print('FIN:', fin)
        rsv1, rsv2, rsv3 = (self.recv_bytes[0]&0x40)>>6, (self.recv_bytes[0]&0x20)>>5, (self.recv_bytes[0]&0x10)>>4
        if 1 in [rsv1, rsv2, rsv3]:
            self.mark_body_sent()
            print("** Error: rsv1, rsv2, rsv3 not be 0, gave:", rsv1, rsv2, rsv3)
            return

        #print('RSV1, RSV2, RSV3:', rsv1, rsv2, rsv3)
        opcode = self.recv_bytes[0] & 0x0f
        if opcode not in {0x01, 0x02, 0x08, 0x09, 0x0a}:
            self.mark_body_sent()
            print("** Error: opcode", opcode, "not supported!")
            return

        #print('opcode:', opcode)

        if len(self.recv_bytes) < 1:
            return

        mask_bit = (self.recv_bytes[1] & 0x80) >> 7
        #print('mask:', mask_bit)
        if mask_bit == 0:
            self.mark_body_sent()
            print("** Error: mask bit not 1.")
            return

        shit_len = self.recv_bytes[1] & 0x7f
        if shit_len <= 125:
            pack_len = shit_len
            if len(self.recv_bytes) < 6 + pack_len:
                return
            mask = self.recv_bytes[2:6]
            payload, self.recv_bytes = self.recv_bytes[6:6+pack_len], self.recv_bytes[6+pack_len:]
        elif shit_len == 126:
            pack_len = struct.unpack(">H", self.recv_bytes[2:4])[0]
            if len(self.recv_bytes) < 8 + pack_len:
                return
            mask = self.recv_bytes[4:8]
            payload, self.recv_bytes = self.recv_bytes[8:8+pack_len], self.recv_bytes[8+pack_len:]
        else:
            pack_len = struct.unpack(">Q", self.recv_bytes[2:10])[0]
            if len(self.recv_bytes) < 14 + pack_len:
                return
            mask = self.recv_bytes[10:14]
            payload, self.recv_bytes = self.recv_bytes[14:14+pack_len], self.recv_bytes[14+pack_len:]

        origin = u''.join([chr(b ^ mask[i % len(mask)]) for i, b in enumerate(payload)])
        print("op:", opcode, "len:", pack_len, origin)

        if opcode == 0x01:
            self.on_text_frame(payload)
        elif opcode == 0x02:
            self.on_bin_frame(payload)
        elif opcode == 0x08:
            self.on_close_frame(payload)
        elif opcode == 0x09:
            self.on_ping_frame(payload)
        elif opcode == 0x0a:
            self.on_pong_frame(payload)
        else:
            print("** Error: unsupported opcode", opcode)
            self.abort()

    def response_body(self, request):
        if len(self.send_quene) == 0:
            return

        frame = self.send_quene.pop(0)
        request.write(frame)

    def close(self):
        frame = self.make_close_frame(b'closed!')
        self.send_quene.append(frame)

    def abort(self):
        frame = self.make_close_frame(b'aborted!')
        self.send_quene.clear()
        self.send_quene.append(frame)

    def ping(self):
        frame = self.make_ping_frame()
        self.send_quene.append(frame)

    def on_close_frame(self, data):
        pass

    def on_text_frame(self, data):
        pass

    def on_bin_frame(self, data):
        pass

    def on_ping_frame(self, data):
        pass

    def on_pong_frame(self, data):
        pass

    @classmethod
    def make_frame(cls, op, data):
        size = len(data)

        if size <= 125:
            length = struct.pack('B', size)
        elif size < 65535:
            length = struct.pack('>BH', 126, size)
        else:
            length = struct.pack('>BQ', 127, size)

        return b''.join([op, length, data])

    @classmethod
    def make_close_frame(cls, data):
        return cls.make_frame(b'\x88', data)

    @classmethod
    def make_text_frame(cls, data):
        return cls.make_frame(b'\x81', data)

    @classmethod
    def make_bin_frame(cls, data):
        return cls.make_frame(b'\x82', data)

    @classmethod
    def make_ping_frame(cls):
        payload = {'tsp': time.time()}
        return cls.make_frame(b'\x89', json.dumps(payload).encode())

    @classmethod
    def make_pong_frame(cls, ping):
        return cls.make_frame(b'\x8a', ping)
