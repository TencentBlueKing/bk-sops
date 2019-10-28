# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import logging
import functools
import importlib
import time
from hashlib import md5

from django.core.cache import cache as default_cache
try:
    import celery
    from celery import task
except Exception:
    celery = None

    def task(func):
        return func


def with_cache(seconds=60, prefix="", ex=None, check=lambda data: True, pre_get=False, countdown=0, cache=None):
    """
    装饰器工厂方法
    缓存装饰器，如果能在cache数据库中找到有效缓存数据，则直接使用缓存，如果没有找到则调用原始函数
    :param prefix: 缓存关键字前缀,默认函数名
    :param ex: 缓存关键字（变量部分），默认用所有参数作为缓存关键字
    :param seconds: 缓存时间，默认60秒钟
    :param check: 校验函数，校验获取到的数据是否有效，返回bool值，如果check结果为false则func计算结果不会写入数据库，直接返回数据
    :param pre_get: 预获取下一次数据， 默认False
    :param countdown: 延迟获取时间，pre_get为True时该字段才有效
    :param cache: 缓存，默认使用 django cache
    :return:
    """
    if ex is None:
        ex = [-1]

    if cache is None:
        cache = default_cache

    def wrapper(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            # 计算缓存key
            cache_key = prefix
            if not cache_key:
                cache_key = func.__name__
            cache_key = generate_cache_key(cache_key, ex, args, kwargs)

            task_running = kwargs.pop("__in_celery", False)

            # 直接获取cache，无效重新计算
            data = cache.get(cache_key)
            if data is None:
                data = func(*args, **kwargs)
                if not check(data):
                    return data
                cache.set(cache_key, data, seconds)

            # 如果是在进行预获取
            if pre_get and not task_running:
                if celery is None:
                    raise Exception('pre_get need installing celery first')
                kwargs["__func_module"] = func.__module__
                kwargs["__func_name"] = func.__name__
                kwargs["__cache_key"] = cache_key
                pre_get_task.apply_async(countdown=countdown, args=args, kwargs=kwargs)
            return data
        return inner
    return wrapper


def to_sorted_str(params):
    """
    对于用字典作为关键的时候，该方法能够一定程度保证前后计算出来的key一致
    :param params:
    :return:
    """
    if isinstance(params, dict):
        data = [(key, params[key]) for key in sorted(params.keys())]
        s = ""
        for k, v in data:
            s += "-%s:%s" % (k, to_sorted_str(v))
        return s
    elif isinstance(params, list) or isinstance(params, tuple):
        data = [to_sorted_str(x) for x in params]
        return "[%s]" % (",".join(data))
    else:
        return "%s" % params


def generate_cache_key(prefix, ex, args, kwargs):
    """
    生成缓存关键字key
    :param prefix: 缓存前缀，比如 "ijobs_user_account"
    :param ex: 附加key位置 [0,3,"biz_cc_id"]
        如果出现-1则表示所有参数 key = "%s, %s" % (args, kwargs)
        如果出现非负整数则为args下标对应字段, 比如args[0], args[3]
        如果出现字符串则为kwargs对应字段, 比如 kwargs["biz_cc_id"]
    :param args: 函数的参数列表
    :param kwargs:函数的参数列表
    :return:
    例如：
    @with_cache("ijobs_user_accout",[0,"biz_cc_id"])
    get_ijobs_account("user00", **{"biz_cc_id":295})
    output: ijobs_user_accout-user00-295
    """
    # 计算cache_key
    cache_key = ""
    if -1 in ex:
        cache_key = cache_key + to_sorted_str(args) + to_sorted_str(kwargs)
    else:
        for item in ex:
            if isinstance(item, int):
                ex_item = args[item]
            elif isinstance(item, str):
                ex_item = kwargs.get(item)
            else:
                raise Exception("unexpected ex type")
            ex_item = to_sorted_str(ex_item)
            cache_key += "-%s" % ex_item

    # 如果如果cache_key太长，则对参数部分用md5表示
    if len(prefix) + len(cache_key) >= 200:
        cache_key = md5(cache_key).hexdigest()
    return prefix + cache_key


@task
def pre_get_task(*args, **kwargs):
    """
    celery预获取执行数据
    """
    mod = importlib.import_module(kwargs.pop("__func_module"))
    func_name = kwargs.pop("__func_name")
    kwargs.pop("__cache_key")
    kwargs["__in_celery"] = True
    try:
        result = mod.__dict__[func_name](*args, **kwargs)
    except Exception as e:
        msg = "pre_get_task ERROR, func_name=%s, error=%s" % (func_name, e)
        logger = logging.getLogger('celery')
        logger.error(msg)
        return {"result": False, "data": msg}
    return result


@with_cache(prefix="test", ex=[0])
def test(seconds):
    """
    demo
    :param seconds:
    :return:
    """
    time.sleep(seconds)
