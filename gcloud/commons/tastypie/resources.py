# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
from django.core.exceptions import FieldDoesNotExist
from django.db.models.constants import LOOKUP_SEP
from tastypie.constants import ALL_WITH_RELATIONS, ALL
from tastypie.http import HttpForbidden
from tastypie.resources import ModelResource
from tastypie.exceptions import ImmediateHttpResponse, NotFound, InvalidFilterError
from django.db.models import Q
from haystack.query import SearchQuerySet
from tastypie.utils import dict_strip_unicode_keys

from iam.contrib.tastypie.resource import IAMResourceMixin

from .serializers import AppSerializer


class GCloudModelResource(IAMResourceMixin, ModelResource):
    login_exempt = False

    def wrap_view(self, view):
        """
        @summary: 统一处理函数装饰逻辑
        """
        view = super(GCloudModelResource, self).wrap_view(view)
        setattr(view, "login_exempt", self.login_exempt)
        return view

    def determine_format(self, request):
        """
        @summary: 强制指定返回数据格式为json
        """
        return "application/json"

    def unauthorized_result(self, exception):
        """
        @summary: return 403 if operation is forbidden, while default of tastypie is 401
        @return:
        """
        raise ImmediateHttpResponse(response=HttpForbidden())

    def _build_filters(self, filters=None, ignore_bad_filters=False):
        """
        Overrides BaseModelResource.build_filters to support query terms for related fields
        https://github.com/django-tastypie/django-tastypie/issues/1618
        """

        if filters is None:
            filters = {}

        qs_filters = {}

        for filter_expr, value in filters.items():
            filter_bits = filter_expr.split(LOOKUP_SEP)
            field_name = filter_bits.pop(0)

            if field_name not in self.fields:
                # It's not a field we know about. Move along citizen.
                continue

            try:
                filter_type = self.resolve_filter_type(field_name, filter_bits, "exact")
                lookup_bits = self.check_filtering(field_name, filter_type, filter_bits)
            except InvalidFilterError:
                if ignore_bad_filters:
                    continue
                else:
                    raise
            value = self.filter_value_to_python(value, field_name, filters, filter_expr, filter_type)

            qs_filter = LOOKUP_SEP.join(lookup_bits)
            qs_filters[qs_filter] = value

        return dict_strip_unicode_keys(qs_filters)

    def check_filtering(self, field_name, filter_type="exact", filter_bits=None):
        """ Overrides BaseModelResource.check_filtering to work with self.build_filters above """

        if filter_bits is None:
            filter_bits = []

        if field_name not in self._meta.filtering:
            raise InvalidFilterError("The '%s' field does not allow filtering." % field_name)

        # Check to see if it's an allowed lookup type.
        if filter_type != "exact" and self._meta.filtering[field_name] not in (ALL, ALL_WITH_RELATIONS):
            # Must be an explicit whitelist.
            if filter_type not in self._meta.filtering[field_name]:
                raise InvalidFilterError("'%s' is not an allowed filter on the '%s' field." % (filter_type, field_name))

        if self.fields[field_name].attribute is None:
            raise InvalidFilterError("The '%s' field has no 'attribute' for searching with." % field_name)

        if len(filter_bits) == 0:
            # Only a field provided, match with provided filter type
            return [self.fields[field_name].attribute] + [filter_type]

        elif len(filter_bits) == 1 and filter_bits[0] in self.get_query_terms(field_name):
            # Match with valid filter type (i.e. contains, startswith, Etc.)
            return [self.fields[field_name].attribute] + filter_bits

        else:
            # Check to see if it's a relational lookup and if that's allowed.
            if not getattr(self.fields[field_name], "is_related", False):
                raise InvalidFilterError("The '%s' field does not support relations." % field_name)

            if not self._meta.filtering[field_name] == ALL_WITH_RELATIONS:
                raise InvalidFilterError(
                    "Lookups are not allowed more than one level deep on the '%s' field." % field_name
                )

            # Recursively descend through the remaining lookups in the filter,
            # if any. We should ensure that all along the way, we're allowed
            # to filter on that field by the related resource.
            related_resource = self.fields[field_name].get_related_resource(None)

            next_field_name = filter_bits[0]
            next_filter_bits = filter_bits[1:]
            next_filter_type = related_resource.resolve_filter_type(next_field_name, next_filter_bits, filter_type)

            return [self.fields[field_name].attribute] + related_resource.check_filtering(
                next_field_name, next_filter_type, next_filter_bits
            )

    def get_query_terms(self, field_name):
        """ Helper to determine supported filter operations for a field """

        if field_name not in self.fields:
            raise InvalidFilterError("The '%s' field is not a valid field" % field_name)

        try:
            django_field_name = self.fields[field_name].attribute
            django_field = self._meta.object_class._meta.get_field(django_field_name)
            if hasattr(django_field, "field"):
                django_field = django_field.field  # related field
        except FieldDoesNotExist:
            raise InvalidFilterError("The '%s' field is not a valid field name" % field_name)

        return django_field.get_lookups().keys()

    def resolve_filter_type(self, field_name, filter_bits, default_filter_type=None):
        """ Helper to derive filter type from next segment in filter bits """

        if not filter_bits:
            # No filter type to resolve, use default
            return default_filter_type
        elif filter_bits[0] not in self.get_query_terms(field_name):
            # Not valid, maybe related field, use default
            return default_filter_type
        else:
            # A valid filter type
            return filter_bits[0]

    def build_filters(self, filters=None, ignore_bad_filters=False):
        """
        @summary:
        """
        if filters is None:
            filters = {}

        orm_filters = self._build_filters(filters, ignore_bad_filters)

        if filters.get("q", "").strip():
            if getattr(self.Meta, "q_fields", []):
                queries = [Q(**{"%s__contains" % field: filters["q"]}) for field in self.Meta.q_fields]
                query = queries.pop()
                for item in queries:
                    query |= item
                orm_filters["q"] = query

            else:
                sqs = (
                    SearchQuerySet()
                    .models(self._meta.object_class)
                    .auto_query(filters["q"])
                    .query_facet(self.Meta.q_fields)
                )
                # 创建自定义定过滤条件
                orm_filters["pk__in"] = [i.pk for i in sqs]

        return orm_filters

    def apply_filters(self, request, applicable_filters):
        """
        @summary:
        """
        if "q" in applicable_filters:
            query = applicable_filters.pop("q")
        else:
            query = None
        queryset = super(GCloudModelResource, self).apply_filters(request, applicable_filters)
        return queryset.filter(query) if query else queryset

    def obj_delete(self, bundle, **kwargs):
        """
        A ORM-specific implementation of ``obj_delete``.

        Takes optional ``kwargs``, which are used to narrow the query to find
        the instance.
        """
        if not hasattr(bundle.obj, "delete"):
            try:
                bundle.obj = self.obj_get(bundle=bundle, **kwargs)
            except self.Meta.object_class.DoesNotExist:
                raise NotFound("A model instance matching the " "provided arguments could not be found")

        self.authorized_delete_detail(self.get_object_list(bundle.request), bundle)
        if "is_deleted" in bundle.obj.__dict__:
            bundle.obj.__dict__.update({"is_deleted": True})
            bundle.obj.save()
        else:
            bundle.obj.delete()

    class CommonMeta:
        serializer = AppSerializer()
        always_return_data = True
        # 控制 Resource 一次显示多少个结果。默认值为 API_LIMIT_PER_PAGE 设置（如果设置）或20（如果未设置）
        limit = 0
        # 控制 Resource 一次显示的最大结果数。如果用户指定的 limit 高于 max_limit，它将被限制为 max_limit
        max_limit = 0

    class Meta(CommonMeta):
        abstract = True
