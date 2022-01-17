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
from collections import OrderedDict

from django.db.models import Q
from haystack.query import SearchQuerySet
from django_filters.constants import ALL_FIELDS
from django_filters.utils import get_all_model_fields
from django_filters import CharFilter
from django_filters.conf import settings
from django_filters.filterset import FilterSet

ALL = "__all__"


class VarietyFilterSet(FilterSet):
    @classmethod
    def get_fields(cls):
        model = cls._meta.model
        fields = cls._meta.fields
        exclude = cls._meta.exclude

        assert not (fields is None and exclude is None), (
            "Setting 'Meta.model' without either 'Meta.fields' or 'Meta.exclude' "
            "has been deprecated since 0.15.0 and is now disallowed. Add an explicit "
            "'Meta.fields' or 'Meta.exclude' to the %s class." % cls.__name__
        )

        if exclude is not None and fields is None:
            fields = ALL_FIELDS

        if fields == ALL_FIELDS:
            fields = get_all_model_fields(model)

        exclude = exclude or []
        if not isinstance(fields, dict):
            fields = [(f, [settings.DEFAULT_LOOKUP_EXPR]) for f in fields if f not in exclude]
        else:
            # 支持 __all__
            fields = cls.support_lookup_when_all(model, fields, exclude)
        return OrderedDict(fields)

    @staticmethod
    def support_lookup_when_all(model, fields, exclude):
        """获取model指定field的lookup"""
        if fields is None:
            return None
        find_fields = []
        for field in model._meta.fields:
            if field.name in fields and field.name not in exclude:
                lookups = fields[field.name]
                if lookups == ALL:
                    find_fields.append((field.name, field.get_lookups().keys()))
        return find_fields


class QFilterSet(VarietyFilterSet):
    q = CharFilter(method="filter_by_q")

    def filter_by_q(self, queryset, name, value):
        if getattr(self.Meta, "q_fields", []):
            queries = [Q(**{"%s__contains" % field: value}) for field in self.Meta.q_fields]
            query = queries.pop()
            for item in queries:
                query |= item
            return queryset.filter(query)

        else:
            sqs = SearchQuerySet().models(self._meta.object_class).auto_query(value).query_facet(self.Meta.q_fields)
            # 创建自定义定过滤条件
            return queryset.filter(pk__in=[i.pk for i in sqs])
