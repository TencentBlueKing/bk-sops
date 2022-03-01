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

from django_filters.filterset import BaseFilterSet, FilterSetOptions, FilterSetMetaclass, FilterSet
from django_filters import Filter
from django.db import models
from gcloud.core.apis.drf.filters import BasePropertyFilter

ALL_LOOKUP = "__all__"
LOOKUP_SEP = "__"


class AllLookupSupportFilterSetOptions(FilterSetOptions):
    def __init__(self, options=None):
        self.lookups = getattr(options, "lookups", None)
        super(AllLookupSupportFilterSetOptions, self).__init__(options)


class AllLookupSupportFilterSetMetaclass(type):
    """
    FILTER_SET_OPTIONS_CLS 需要重新定义
    """

    def __new__(cls, name, bases, attrs):
        attrs["declared_filters"] = cls.get_declared_filters(bases, attrs)
        new_class = super().__new__(cls, name, bases, attrs)
        new_class._meta = new_class.FILTER_SET_OPTIONS_CLS(getattr(new_class, "Meta", None))
        new_class.base_filters = new_class.get_filters()
        assert not hasattr(new_class, "filter_for_reverse_field"), (
            "`%(cls)s.filter_for_reverse_field` has been removed. "
            "`%(cls)s.filter_for_field` now generates filters for reverse fields. "
            "See: https://django-filter.readthedocs.io/en/master/guide/migration.html" % {"cls": new_class.__name__}
        )
        return new_class

    @classmethod
    def get_declared_filters(cls, bases, attrs):
        return FilterSetMetaclass.get_declared_filters(bases, attrs)


class AllLookupSupportFilterSet(BaseFilterSet, metaclass=AllLookupSupportFilterSetMetaclass):
    FILTER_SET_OPTIONS_CLS = AllLookupSupportFilterSetOptions

    @classmethod
    def set_field_lookup(cls, field, lookups, fields_lookups):
        """
        :param field: 需要被查询lookup的model字段
        :param lookups: 需要被查询 lookups
        :param fields_lookups: 原始查询数据
        """

        if lookups != ALL_LOOKUP:
            return

        model = cls._meta.model
        if LOOKUP_SEP in field:
            # 处理 {"groups__info__name" : "__all__"}的情况
            fields = field.split(LOOKUP_SEP)
            for index, _field in enumerate(fields, start=1):
                if index == len(fields):
                    fields_lookups[field] = model._meta.get_field(_field).get_lookups().keys()
                model = model._meta.get_field(_field).related_model
            return

        field_object = model._meta.get_field(field)
        if field_object.is_relation:
            # 外键只支持一层子级lookups
            for relation_field in field_object.related_model._meta.fields:
                lookup_field = LOOKUP_SEP.join([field, relation_field.name])
                fields_lookups.update({lookup_field: relation_field.get_lookups().keys()})
        else:
            fields_lookups[field] = field_object.get_lookups().keys()

    @classmethod
    def get_fields(cls):
        """
        1.支持 lookups, 当fields为list或tuple时生效，使fields中字段支持lookups中声明的查询语法。
        如： fields = ["id", "name", "info__num"]
            lookups = ["in", "contains"]

        如 ：fields = ["id", "name", "info__num"]
            lookups = "__all__"

        2.支持 fields 属性指定的字段支持orm中所有查询语法。为外键声明 all 时只支持一层子级字段查询
        如： fields = {"id":“ __all__","name": “__all__"}
        如： fields = {"id":“ __all__","name": ["in", "contains"], "info__num": ["in", "range"]}
        如： fields = {"id":“ __all__","name": ["in", "contains"], "info__num": “__all__”}
        如： fields = ["id", "name", "info__num"]
        """
        exclude = cls._meta.exclude or []
        lookups = cls._meta.lookups
        fields = cls._meta.fields

        fields_lookups = super(AllLookupSupportFilterSet, cls).get_fields()

        if isinstance(fields, dict):
            for field, lookups in fields_lookups.items():
                if field not in exclude:
                    cls.set_field_lookup(field, lookups, fields_lookups)
        else:
            if not lookups:
                return fields_lookups
            fields = fields_lookups.keys() if fields == ALL_LOOKUP else fields
            for field in fields:
                if field not in exclude:
                    cls.set_field_lookup(field, lookups, fields_lookups)
        return fields_lookups


class PropertyFilterSet(FilterSet):
    """
    Filtering for properties

    example property_fields:
        property_fields = [
            (property_name, fieldFilter, [support_lookup_expr])
            property字段名, 过滤器, 受支持的lookup
        ]
    """

    _PROPERTY_FIELDS_META_KEY = "property_fields"

    def __init__(self, *args, **kwargs):
        # inject property_filters into base_filters
        self._loading_property_filters()
        self.property_filters = set()
        super().__init__(*args, **kwargs)

    def _build_property_filter(self, property_filter_cls, property_name, lookup):
        """Add property filters to base_filters"""
        filter_name = f"{property_name}__{lookup}"

        self.base_filters[filter_name] = property_filter_cls(field_name=filter_name, lookup_expr=lookup)

    def _loading_property_filters(self):
        property_fields = self.__class__.Meta.__dict__.get(self._PROPERTY_FIELDS_META_KEY, None)
        filter_model_cls = self.__class__.Meta.__dict__["model"]
        if not property_fields:
            return
        for field in property_fields:
            property_name, property_filter_cls, lookup_expr = field
            # valid property_name valid attribute
            if not isinstance(property_name, str) and not hasattr(filter_model_cls, property_name):
                raise ValueError(f"{property_name} is not a valid field of {filter_model_cls}")
            # valid property_filter_cls
            if not issubclass(property_filter_cls, Filter):
                raise ValueError(f"{property_filter_cls} is not subclass of django_filter.Filter")
            # valid lookup_expr
            if not isinstance(lookup_expr, list):
                raise ValueError("lookup_expr must be a list")
            # build Filters
            for lookup in lookup_expr:
                self._build_property_filter(property_filter_cls, property_name, lookup)

    def property_filter_queryset(self, queryset):
        pk_list = queryset.values_list("pk", flat=True)
        initial_queryset = queryset
        for name, value in self.property_filters:
            filter = self.filters[name]
            # do qs filter
            pk_list = filter.qs_filter(queryset, name, value)
        # get new queryset by pk_list
        return initial_queryset.filter(pk__in=pk_list)

    def filter_queryset(self, queryset):
        # django_filter
        for name, value in self.form.cleaned_data.items():
            if isinstance(self.filters[name], BasePropertyFilter):
                # PropertyFilter need another process function
                if value:
                    self.property_filters.add((name, value))
                continue
            queryset = self.filters[name].filter(queryset, value)
            assert isinstance(
                queryset, models.QuerySet
            ), "Expected '%s.%s' to return a QuerySet, but got a %s instead." % (
                type(self).__name__,
                name,
                type(queryset).__name__,
            )
        # property filter
        if self.__class__.Meta.__dict__.get(self._PROPERTY_FIELDS_META_KEY, None):
            queryset = self.property_filter_queryset(queryset)
        return queryset
