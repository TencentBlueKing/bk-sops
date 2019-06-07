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


class Resource(object):
    def __init__(self, rtype, name, actions, parent=None, scope_type=None, scope_id=None):
        self.rtype = rtype
        self.name = name
        self.actions = actions
        self.parent = parent
        self.scope_type = scope_type
        self.scope_id = scope_id

    def register_resource_type(self, interfaces):
        pass

    def register_resource_instance(self, interfaces):
        pass

    def verify(self, username, actions):
        pass

    def search_instances(self, username, actions):
        pass
