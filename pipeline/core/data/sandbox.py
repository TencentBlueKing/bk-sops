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

# mock str return value of Built-in Functions，make str(func) return "func" rather than "<built-in function func>"

import builtins

SANDBOX = {}


class MockStrMeta(type):

    def __new__(cls, name, bases, attrs):
        new_cls = super(MockStrMeta, cls).__new__(cls, name, bases, attrs)
        SANDBOX.update({new_cls.str_return: new_cls})
        return new_cls

    def __str__(cls):
        return cls.str_return

    def __call__(cls, *args, **kwargs):
        return cls.call(*args, **kwargs)


for func_name in dir(builtins):
    """
    @summary: generate mock class of built-in functions like id,int
    """
    if func_name.lower() == func_name and not func_name.startswith('_'):
        new_func_name = "Mock{}".format(func_name.capitalize())
        MockStrMeta(new_func_name, (object, ), {"call": getattr(builtins, func_name), "str_return": func_name})
