# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import threading


class SimpleThreadLocal:
    def __init__(self):
        self._thread_local = threading.local()

    def set(self, key: str, value) -> None:
        if not hasattr(self._thread_local, "vars"):
            self._thread_local.vars = {}
        self._thread_local.vars[key] = value

    def get(self, key: str, default=None):
        if not hasattr(self._thread_local, "vars"):
            return default
        return self._thread_local.vars.get(key, default)


thread_local = SimpleThreadLocal()
