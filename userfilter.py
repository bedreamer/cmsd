# -*- coding: utf8 -*-
from django import template


# Django要求必须是register
register = template.Library()


@register.filter(name='have')
def have(body, finger):
    if body.find(finger) < 0:
        return False
    return True


@register.filter(name='odd')
def odd(v):
    print(v, type(v))
    return True
