# -*- coding: UTF-8 -*-
__author__ = 'lijie'
import os


# 模板目录位置
template_dirs = [
    os.path.abspath(__file__).strip(os.path.basename(__file__)) + 'templates'
]

# 用户定义的过滤器模块映射
template_user_filters = {
    'userfileter': 'userfilter'
}

# 静态文件存放目录
www_dir = os.path.abspath(__file__).strip(os.path.basename(__file__)) + 'www'


# 最大传输块大小
max_transport_unit_size = 2048