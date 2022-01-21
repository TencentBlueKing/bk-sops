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

from django_filters.conf import settings
from django_filters.filterset import FilterSet


ALL_LOOKUP = "__all__"
LOOKUP_SEP = "__"


class AllLookupSupportFilterSet(FilterSet):
    @classmethod
    def get_field_lookup(cls, field, source_lookup):
        """
        :param field: 需要被查询lookup的model字段
        :param source_lookup: field原始lookup查询条件
        """
        # 外键透传, 为ALL_LOOKUP时返回 exact
        if LOOKUP_SEP in field:
            return [settings.DEFAULT_LOOKUP_EXPR] if source_lookup == ALL_LOOKUP else source_lookup

        field = cls._meta.model._meta.get_field(field)
        return field.get_lookups().keys()

    @classmethod
    def get_fields(cls):
        """
        支持filterset meta中配置flookups, 当fields为list或tuple时，使fields中字段支持lookups中声明的lookup。
        如 ：lookups = ["in", "contains"]
        如 ：lookups = "__all__"

        支持filterset meta fields属性指定的filter字段支持orm中所有查询语法。声明外键为all时暂只支持exact查询
        如： fields = {"id":“ __all__","name": “__all__"}
        如： fields = {"id":“ __all__","name": ["in", "contains"], "info__num": ["in", "range"]}
        如： fields = ["id", "name", "info__num"]
        """
        exclude = cls._meta.exclude or []
        source_fields = super(AllLookupSupportFilterSet, cls).get_fields()

        if isinstance(cls._meta.fields, dict):
            for field, lookups in source_fields.items():
                if field in exclude:
                    continue
                elif lookups == ALL_LOOKUP:
                    source_fields[field] = cls.get_field_lookup(field, source_fields[field])
        else:
            lookups = getattr(cls._meta, "lookups")
            if not lookups:
                return source_fields

            for field in cls._meta.fields:
                if field in exclude:
                    continue

                field_lookup = cls.get_field_lookup(field, source_fields[field])
                if lookups == ALL_LOOKUP:
                    source_fields[field] = field_lookup
                else:
                    source_fields[field] = list(set(lookups) & set(field_lookup))
        return source_fields
