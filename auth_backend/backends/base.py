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

import abc


class AuthBackend(object):
    __metaclass__ = abc.ABCMeta

    def register_instance(self, resource, instance):
        raise NotImplementedError()

    def batch_register_instance(self, resource, instances):
        raise NotImplementedError()

    def update_instance(self, resource, instance):
        raise NotImplementedError()

    def delete_instance(self, resource, instance):
        raise NotImplementedError()

    def batch_delete_instance(self, resource, instances):
        raise NotImplementedError()
