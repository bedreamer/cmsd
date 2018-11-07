# -*- coding: UTF-8 -*-
__author__ = 'lijie'
import json
import time
import codecs
import os
import mimetypes
import settings


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
        request.write(headers.encode())

    def response_body(self, request):
        self.body_sent = True

        if self.body is not None and len(self.body) > 0:
            request.write(self.body.encode())

    def on_body_received(self, request, data):
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
        headers['Content-Type'] = "text/html"
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


class HttpResponseLongPoll(HttpResponseBasic):
    pass


class HttpResponseWebSocket(HttpResponseBasic):
    pass


