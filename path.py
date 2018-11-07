# -*- coding: UTF-8 -*-
__author__ = 'lijie'
import re
import os
import settings
import response


class PathProcessorWrapper:
    def __init__(self, processor, origin_express, app, match_express, match_dmap, methods):
        self.processor = processor
        self.origin_express = origin_express
        self.app = app
        self.match_express = match_express
        self.match_reg = re.compile(match_express)
        self.match_dmap = match_dmap
        self.methods = methods

    def match(self, path, method):
        if method not in self.methods:
            return None, None

        match_result = self.match_reg.match(path)
        if match_result is None:
            return None, None
        params_dict = {name: self.match_dmap[name].format(value) for name, value in match_result.groupdict().items()}
        return params_dict, self.wrapper_process

    def wrapper_process(self, request, **kwargs):
        user_response = self.processor(request, **kwargs)

        if isinstance(user_response, str):
            return response.HttpResponseHtml(user_response)
        elif isinstance(user_response, bytes):
            return response.HttpResponseHtml(user_response.decode())
        elif issubclass(user_response.__class__, response.HttpResponseBasic):
            return user_response
        elif isinstance(user_response, int) or isinstance(user_response, float) or isinstance(user_response, list)\
                or isinstance(user_response, tuple) or isinstance(user_response, dict):
            return response.HttpResponseJson(user_response)
        else:
            raise NotImplementedError("str bytes int float list tuple dict or response.HttpResponseBasic supported!")


class INT(int):
    @staticmethod
    def rexpress(): return '[-+]?\d+'

    @staticmethod
    def format(x): return int(x)


class STR(str):
    @staticmethod
    def rexpress(): return '.+?'

    @staticmethod
    def format(x): return str(x)


class HEX(str):
    @staticmethod
    def rexpress(): return '[0-9a-fA-F]+?'

    @staticmethod
    def format(x): return str(x)


def bind(origin_path_express, processor, app=None, method=None):
    if app is None:
        app = 'main'
    if method is None:
        method = ['GET', 'POST']

    def express_path_compile():
        r_match = re.compile(r'<(int|str|hex):(?P<name>.*?)>')
        result = r_match.findall(origin_path_express)
        if result is None:
            return ''.join(['^', origin_path_express, '$']), dict()
        else:
            dmap = {name: eval(t.upper()) for t, name in result}
            match_p = origin_path_express
            for t, name in result:
                old_pattern = ''.join(['<', t, ':', name, '>'])
                new_pattern = ''.join(['(?P<' + name + '>', dmap[name].rexpress(), ')'])
                match_p = match_p.replace(old_pattern, new_pattern)
            return ''.join(['^', match_p, '$']), dmap

    match_express, match_dmap = express_path_compile()
    return PathProcessorWrapper(processor, origin_path_express, app, match_express, match_dmap, method)


_global_path_router = list()


def route(path, **kwargs):
    global _global_path_router

    if 'app' not in kwargs:
        kwargs['app'] = 'main'

    def wrapper(func):
        router_item = bind(path, func, **kwargs)
        _global_path_router.append(router_item)

    return wrapper


def default_file_handle(request, **kwargs):
    full_path = settings.www_dir + request.path
    if os.path.exists(full_path) is False or os.path.isfile(full_path) is False:
        return response.HttpResponseNotFound()
    else:
        return response.HttpNormalFile(full_path)


def search_route_path(request):
    global _global_path_router

    for router in _global_path_router:
        params_dict, processor = router.match(request.path, request.method)
        if params_dict is None:
            continue

        return params_dict, processor
    return {}, default_file_handle


