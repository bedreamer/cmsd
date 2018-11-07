# -*- coding: UTF-8 -*-
__author__ = 'lijie'
import django.template as dj
import settings


# 初始化模板环境
env = dj.Engine(dirs=settings.template_dirs, libraries=settings.template_user_filters)


def render(request, template_file_path, ctx=None):
    if ctx is None:
        ctx = dict()

    template = env.get_template(template_file_path)
    context = dj.Context()
    for key, value in ctx.items():
        context[key] = value
    context['request'] = request
    request.user = {}
    context['name'] = '你好'
    return template.render(context)


