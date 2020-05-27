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

from tastypie.http import HttpForbidden, NotFound
from tastypie.resources import ModelResource
from tastypie.exceptions import ImmediateHttpResponse
from django.db.models import Q
from haystack.query import SearchQuerySet

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

    def build_filters(self, filters=None, ignore_bad_filters=False):
        """
        @summary:
        """
        if filters is None:
            filters = {}

        orm_filters = super(GCloudModelResource, self).build_filters(filters, ignore_bad_filters)

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

    class Meta:
        serializer = AppSerializer()
        always_return_data = True
        # 控制 Resource 一次显示多少个结果。默认值为 API_LIMIT_PER_PAGE 设置（如果设置）或20（如果未设置）
        limit = 0
        # 控制 Resource 一次显示的最大结果数。如果用户指定的 limit 高于 max_limit，它将被限制为 max_limit
        max_limit = 0
