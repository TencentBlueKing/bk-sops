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


class BkUserCompatibleMixin:
    custom_fields = set(['chname', 'email', 'language', 'phone', 'qq', 'role', 'time_zone', 'uin', 'wx_userid',
                         'auth_token'] + ['chinese_name', 'company_code', 'company_id', 'company_list', 'company_name',
                                          'first_name', 'last_name', 'nick_name'])

    @property
    def chname(self):
        return self.get_property('chname')

    @property
    def email(self):
        return self.get_property('email')

    @property
    def language(self):
        return self.get_property('language')

    @property
    def phone(self):
        return self.get_property('phone')

    @property
    def qq(self):
        return self.get_property('qq')

    @property
    def role(self):
        return self.get_property('role')

    @property
    def time_zone(self):
        return self.get_property('time_zone')

    @property
    def uin(self):
        return self.get_property('uin')

    @property
    def wx_userid(self):
        return self.get_property('ex_userid')

    @property
    def auth_token(self):
        return self.get_property('auth_token')

    @property
    def chinese_name(self):
        return self.get_property('chinese_name')

    @property
    def company_name(self):
        return self.get_property('company_name')

    @property
    def company_code(self):
        return self.get_property('company_code')

    @property
    def company_id(self):
        return self.get_property('company_id')

    @property
    def company_list(self):
        return self.get_property('company_list')

    @property
    def first_name(self):
        return self.get_property('first_name')

    @property
    def last_name(self):
        return self.get_property('last_name')

    @property
    def nick_name(self):
        return self.get_property('nick_name')
