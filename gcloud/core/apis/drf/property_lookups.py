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

import re
from datetime import datetime

METHOD_PREFIX = "property_"


def _check_regx(regx, string):
    if re.search(regx, string):
        return True
    return False


class LookupMethods:
    """all field"""

    def property_exact(self, real_value, value):
        return real_value == value

    def property_iexact(self, real_value, value):
        return real_value != value

    def property_isnull(self, real_value, value):
        return real_value is None if value else real_value is not None

    """charfield"""

    def property_contains(self, real_value, value):
        return value in real_value

    def property_icontains(self, real_value, value):
        return value.lower() in real_value.lower()

    def property_in(self, real_value, value):
        return value in real_value

    def property_startswith(self, real_value, value):
        return real_value.startswith(value)

    def property_istartswith(self, real_value, value):
        return real_value.lower().startswith(value.lower())

    def property_endswith(self, real_value, value):
        return real_value.endswith(value)

    def property_iendswith(self, real_value, value):
        return real_value.lower().endswith(value.lower())

    def property_regex(self, real_value, value):
        return _check_regx(regx=value, string=real_value)

    def property_iregex(self, real_value, value):
        return _check_regx(regx=value.lower(), string=real_value.lower())

    """datetimefield && numberfield"""

    def property_gt(self, real_value, value):
        return real_value > value

    def property_gte(self, real_value, value):
        return real_value >= value

    def property_lt(self, real_value, value):
        return real_value < value

    def property_lte(self, real_value, value):
        return real_value <= value

    """datetimefield"""

    def property_date(self, real_value, value):
        return datetime.date(real_value) == datetime.date(value)

    def property_year(self, real_value, value):
        return real_value.year == value

    def property_month(self, real_value, value):
        return real_value.month == value

    def property_day(self, real_value, value):
        return real_value.day == value

    def property_time(self, real_value, value):
        return real_value.time() == value

    def property_hour(self, real_value, value):
        return real_value.hour == value

    def property_minute(self, real_value, value):
        return real_value.minute == value

    def property_second(self, real_value, value):
        return real_value.second == value


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

    property_exact = LookupMethods.property_exact
    property_isnull = LookupMethods.property_isnull


class CharLookup(BaseLookup):
    property_iexact = LookupMethods.property_iexact
    property_contains = LookupMethods.property_contains
    property_icontains = LookupMethods.property_icontains
    property_in = LookupMethods.property_in
    property_startswith = LookupMethods.property_startswith
    property_istartswith = LookupMethods.property_istartswith
    property_endswith = LookupMethods.property_endswith
    property_iendswith = LookupMethods.property_iendswith
    property_regex = LookupMethods.property_regex
    property_iregex = LookupMethods.property_iregex


class NumberLookup(BaseLookup):
    property_exact = LookupMethods.property_exact
    property_gt = LookupMethods.property_gt
    property_gte = LookupMethods.property_gte
    property_lt = LookupMethods.property_lt
    property_lte = LookupMethods.property_lte


class DateTimeLookup(BaseLookup):
    property_gt = LookupMethods.property_gt
    property_gte = LookupMethods.property_gte
    property_lt = LookupMethods.property_lt
    property_lte = LookupMethods.property_lte
    property_date = LookupMethods.property_date
    property_year = LookupMethods.property_year
    property_month = LookupMethods.property_month
    property_day = LookupMethods.property_day
    property_time = LookupMethods.property_time
    property_hour = LookupMethods.property_hour
    property_minute = LookupMethods.property_minute
    property_second = LookupMethods.property_second


class BooleanLookup(BaseLookup):
    property_iexact = LookupMethods.property_iexact
