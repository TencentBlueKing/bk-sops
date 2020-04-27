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

from __future__ import absolute_import, unicode_literals

from django.apps import AppConfig


class ConsistencyConfig(AppConfig):

    name = 'auth_backend.contrib.consistency'

    def ready(self):
        from auth_backend.contrib.consistency.signals.handlers import instance_register_fail_handler  # noqa
        from auth_backend.contrib.consistency.signals.handlers import instance_batch_register_fail_handler  # noqa
