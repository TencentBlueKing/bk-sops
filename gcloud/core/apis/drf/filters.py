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

import abc

from django_filters import Filter, CharFilter, BooleanFilter, DateTimeFilter, NumberFilter
from gcloud.core.apis.drf.property_lookups import CharLookup, NumberLookup, DateTimeLookup, BooleanLookup


class BasePropertyFilter(Filter, abc.ABC):
    """subclass needs add attr: lookup_class"""

    def _value_comparison_with_lookup(self, real_value, value, lookup_expr: list) -> bool:
        return self.lookup_class.lookup(real_value, value, lookup_expr)

    def qs_filter(self, queryset, property_name, property_value):
        """property取值过滤，构建过滤后的pk_list"""
        pk_list = set()
        property_name = "".join(property_name.split("__")[0:-1])
        for obj in queryset:
            real_property_value = getattr(obj, property_name)
            if not self._value_comparison_with_lookup(real_property_value, property_value, self.lookup_expr):
                continue
            pk_list.add(obj.id)
        return pk_list


class CharPropertyFilter(BasePropertyFilter, CharFilter):
    lookup_class = CharLookup


class NumberPropertyFilter(BasePropertyFilter, NumberFilter):
    lookup_class = NumberLookup


class DateTImePropertyFilter(BasePropertyFilter, DateTimeFilter):
    lookup_class = DateTimeLookup


class BooleanPropertyFilter(BasePropertyFilter, BooleanFilter):
    lookup_class = BooleanLookup
