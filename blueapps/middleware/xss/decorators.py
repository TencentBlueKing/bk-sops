# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from django.utils.decorators import available_attrs

try:
    from functools import wraps
except ImportError:
    from django.utils.functional import wraps  # Python 2.4 fallback.


# ===============================================================================
# 转义装饰器
# ===============================================================================
def escape_exempt(view_func):
    """
    转义豁免，被此装饰器修饰的action可以不进行中间件escape
    """

    def wrapped_view(*args, **kwargs):
        return view_func(*args, **kwargs)

    wrapped_view.escape_exempt = True
    return wraps(view_func, assigned=available_attrs(view_func))(wrapped_view)


def escape_script(view_func):
    """
    被此装饰器修饰的action会对GET与POST参数进行javascript escape
    """

    def wrapped_view(*args, **kwargs):
        return view_func(*args, **kwargs)

    wrapped_view.escape_script = True
    return wraps(view_func, assigned=available_attrs(view_func))(wrapped_view)


def escape_url(view_func):
    """
    被此装饰器修饰的action会对GET与POST参数进行url escape
    """

    def wrapped_view(*args, **kwargs):
        return view_func(*args, **kwargs)

    wrapped_view.escape_url = True
    return wraps(view_func, assigned=available_attrs(view_func))(wrapped_view)


def escape_exempt_param(*param_list, **param_list_dict):
    """
    此装饰器用来豁免某个view函数的某个参数
    @param param_list: 参数列表
    @return:
    """

    def _escape_exempt_param(view_func):
        def wrapped_view(*args, **kwargs):
            return view_func(*args, **kwargs)

        if param_list_dict.get("param_list"):
            wrapped_view.escape_exempt_param = param_list_dict["param_list"]
        else:
            wrapped_view.escape_exempt_param = list(param_list)
        return wraps(view_func, assigned=available_attrs(view_func))(wrapped_view)

    return _escape_exempt_param
