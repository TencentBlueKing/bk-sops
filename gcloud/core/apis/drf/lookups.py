# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2022 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

"""
lookup methods define
def example_methods(self, real_value, value):
    pass
"""
METHOD_PREFIX = "property_"


class LookupMethos:
    def property_exact(self, real_value, value):
        return real_value == value

    def property_iexact(self, real_value, value):
        return real_value != value

    def property_contains(self, real_value, value):
        pass

    def property_icontains(self, real_value, value):
        pass

    def property_in(self, real_value, value):
        pass

    def property_gt(self, real_value, value):
        pass

    def property_gte(self, real_value, value):
        pass

    def property_lt(self, real_value, value):
        pass

    def property_lte(self, real_value, value):
        pass

    def property_startswith(self, real_value, value):
        pass

    def property_istartswith(self, real_value, value):
        pass

    def property_endswith(self, real_value, value):
        pass

    def property_iendswith(self, real_value, value):
        pass

    def property_range(self, real_value, value):
        pass

    def property_date(self, real_value, value):
        pass

    def property_year(self, real_value, value):
        pass

    def property_iso_year(self, real_value, value):
        pass

    def property_month(self, real_value, value):
        pass

    def property_day(self, real_value, value):
        pass

    def property_week(self, real_value, value):
        pass

    def property_week_day(self, real_value, value):
        pass

    def property_iso_week_day(self, real_value, value):
        pass

    def property_quarter(self, real_value, value):
        pass

    def property_time(self, real_value, value):
        pass

    def property_hour(self, real_value, value):
        pass

    def property_minute(self, real_value, value):
        pass

    def property_second(self, real_value, value):
        pass

    def property_isnull(self, real_value, value):
        pass

    def property_regex(self, real_value, value):
        pass

    def property_iregex(self, real_value, value):
        pass


class BaseLookup:
    @classmethod
    def lookup(self, real_value, value, lookup):
        # 调用对应的方法
        # 1、加前缀
        lookup_method = getattr(self, METHOD_PREFIX + lookup)
        # 一旦有一个满足就return
        if lookup_method(self, real_value, value):
            return True
        else:
            return False

    property_exact = LookupMethos.property_exact
    property_isnull = LookupMethos.property_isnull


class CharLookup(BaseLookup):
    property_iexact = LookupMethos.property_iexact
    property_contains = LookupMethos.property_contains
    property_icontains = LookupMethos.property_icontains
    property_in = LookupMethos.property_in
    property_startswith = LookupMethos.property_startswith
    property_istartswith = LookupMethos.property_istartswith
    property_endswith = LookupMethos.property_endswith
    property_iendswith = LookupMethos.property_iendswith
    property_regex = LookupMethos.property_regex
    property_iregex = LookupMethos.property_iregex


class NumberLookup(BaseLookup):
    property_exact = LookupMethos.property_exact
    property_gt = LookupMethos.property_gt
    property_gte = LookupMethos.property_gte
    property_lt = LookupMethos.property_lt
    property_lte = LookupMethos.property_lte


class DateTimeLookup(BaseLookup):
    property_exact = LookupMethos.property_exact


class BooleanLookup(BaseLookup):
    property_exact = LookupMethos.property_exact
    property_iexact = LookupMethos.property_iexact
