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

# Global in-memory store of cache data. Keyed by name, to provide
# multiple named local memory caches.
import time
from contextlib import contextmanager
from django.core.cache.backends.base import DEFAULT_TIMEOUT, BaseCache
from threading import Lock

_caches = {}
_expire_info = {}
_locks = {}

"""
来源于 django.core.cache.backends.locmem

将每次写/读缓存的 pickle.dumps/pickle.loads 操作省略，提高吞吐量
"""


@contextmanager
def dummy():
    """A context manager that does nothing special."""
    yield


class DummyPickle(object):
    def dumps(self, value, protocol):
        return value

    def loads(self, pickled):
        return pickled


pickle = DummyPickle()
setattr(pickle, "HIGHEST_PROTOCOL", 1)


class LocMemCache(BaseCache):
    def __init__(self, name, params):
        BaseCache.__init__(self, params)
        self._cache = _caches.setdefault(name, {})
        self._expire_info = _expire_info.setdefault(name, {})
        self._lock = _locks.setdefault(name, Lock())

    def add(self, key, value, timeout=DEFAULT_TIMEOUT, version=None):
        key = self.make_key(key, version=version)
        self.validate_key(key)
        pickled = pickle.dumps(value, pickle.HIGHEST_PROTOCOL)
        with self._lock:
            if self._has_expired(key):
                self._set(key, pickled, timeout)
                return True
            return False

    def get(self, key, default=None, version=None, acquire_lock=True):
        key = self.make_key(key, version=version)
        self.validate_key(key)
        pickled = None
        with (self._lock if acquire_lock else dummy()):
            if not self._has_expired(key):
                pickled = self._cache[key]
        if pickled is not None:
            try:
                return pickle.loads(pickled)
            except pickle.PickleError:
                return default

        with (self._lock if acquire_lock else dummy()):
            try:
                del self._cache[key]
                del self._expire_info[key]
            except KeyError:
                pass
            return default

    def _set(self, key, value, timeout=DEFAULT_TIMEOUT):
        if len(self._cache) >= self._max_entries:
            self._cull()
        self._cache[key] = value
        self._expire_info[key] = self.get_backend_timeout(timeout)

    def set(self, key, value, timeout=DEFAULT_TIMEOUT, version=None):
        key = self.make_key(key, version=version)
        self.validate_key(key)
        pickled = pickle.dumps(value, pickle.HIGHEST_PROTOCOL)
        with self._lock:
            self._set(key, pickled, timeout)

    def incr(self, key, delta=1, version=None):
        with self._lock:
            value = self.get(key, version=version, acquire_lock=False)
            if value is None:
                raise ValueError("Key '%s' not found" % key)
            new_value = value + delta
            key = self.make_key(key, version=version)
            pickled = pickle.dumps(new_value, pickle.HIGHEST_PROTOCOL)
            self._cache[key] = pickled
        return new_value

    def has_key(self, key, version=None):
        key = self.make_key(key, version=version)
        self.validate_key(key)
        with self._lock:
            if not self._has_expired(key):
                return True

        with self._lock:
            try:
                del self._cache[key]
                del self._expire_info[key]
            except KeyError:
                pass
            return False

    def _has_expired(self, key):
        exp = self._expire_info.get(key, -1)
        if exp is None or exp > time.time():
            return False
        return True

    def _cull(self):
        if self._cull_frequency == 0:
            self.clear()
        else:
            doomed = [k for (i, k) in enumerate(self._cache) if i % self._cull_frequency == 0]
            for k in doomed:
                self._delete(k)

    def _delete(self, key):
        try:
            del self._cache[key]
        except KeyError:
            pass
        try:
            del self._expire_info[key]
        except KeyError:
            pass

    def delete(self, key, version=None):
        key = self.make_key(key, version=version)
        self.validate_key(key)
        with self._lock:
            self._delete(key)

    def clear(self):
        self._cache.clear()
        self._expire_info.clear()
