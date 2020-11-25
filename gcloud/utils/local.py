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

from contextlib import contextmanager

try:
    from greenlet import getcurrent as get_ident
except ImportError:
    try:
        from six.moves._thread import get_ident
    except ImportError:
        from _thread import get_ident

__all__ = ["local", "Local", "get_ident"]


"""Thread-local/Greenlet-local objects

Thread-local/Greenlet-local objects support the management of
thread-local/greenlet-local data. If you have data that you want
to be local to a thread/greenlet, simply create a
thread-local/greenlet-local object and use its attributes:

  >>> mydata = Local()
  >>> mydata.number = 42
  >>> mydata.number
  42
  >>> hasattr(mydata, 'number')
  True
  >>> hasattr(mydata, 'username')
  False

  Reference :
  from threading import local
"""


class Localbase(object):

    __slots__ = ("__storage__", "__ident_func__")

    def __new__(cls, *args, **kwargs):
        self = object.__new__(cls, *args, **kwargs)
        object.__setattr__(self, "__storage__", {})
        object.__setattr__(self, "__ident_func__", get_ident)
        return self


class Local(Localbase):
    def __iter__(self):
        ident = self.__ident_func__()
        try:
            return iter(list(self.__storage__[ident].items()))
        except KeyError:
            return iter([])

    def __release_local__(self):
        self.__storage__.pop(self.__ident_func__(), None)

    def __getattr__(self, name):
        ident = self.__ident_func__()
        try:
            return self.__storage__[ident][name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        if name in ("__storage__", "__ident_func__"):
            raise AttributeError("%r object attribute '%s' is read-only" % (self.__class__.__name__, name))

        ident = self.__ident_func__()
        storage = self.__storage__
        if ident not in storage:
            storage[ident] = dict()
        storage[ident][name] = value

    def __delattr__(self, name):
        if name in ("__storage__", "__ident_func__"):
            raise AttributeError("%r object attribute '%s' is read-only" % (self.__class__.__name__, name))

        ident = self.__ident_func__()
        try:
            del self.__storage__[ident][name]
            if len(self.__storage__[ident]) == 0:
                self.__release_local__()
        except KeyError:
            raise AttributeError(name)

    def clear(self):
        self.__release_local__()


local = Local()


@contextmanager
def with_request_local():
    local_vars = {}
    for k in ["operator", "username", "current_request"]:
        if hasattr(local, k):
            local_vars[k] = getattr(local, k)
            delattr(local, k)

    try:
        yield local
    finally:
        for k, v in list(local_vars.items()):
            setattr(local, k, v)


@contextmanager
def with_client_user(username):
    with with_request_local() as local:
        local.username = username
        yield


@contextmanager
def with_client_operator(update_user):
    with with_request_local() as local:
        local.operator = update_user
        yield
