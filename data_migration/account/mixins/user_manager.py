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

from blueapps.account.models import User


class UserManagerMixin:
    def update_or_create(self, defaults=None, **kwargs):
        props = []

        for k in defaults.keys():
            if k in User.custom_fields:
                props.append({'key': k, 'value': defaults.pop(k)})
        obj, created = super(UserManagerMixin, self).update_or_create(
            defaults, **kwargs)
        for p in props:
            obj.set_property(p['key'], p['value'])
        return obj, created
