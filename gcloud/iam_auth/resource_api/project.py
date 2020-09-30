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

from django.core.cache import cache

from iam import DjangoQuerySetConverter
from iam.contrib.django.dispatcher import InvalidPageException
from iam.resource.provider import ListResult, ResourceProvider
from gcloud.core.models import Project

CACHE_TIME_FOR_PROJECT = 60 * 10


class ProjectResourceProvider(ResourceProvider):
    def pre_search_instance(self, filter, page, **options):
        if page.limit == 0 or page.limit > 1000:
            raise InvalidPageException("limit in page too large")

    def search_instance(self, filter, page, **options):
        """
        project 没有上层资源，不需要处理 filter 的 parent
        """
        keyword = filter.keyword

        results = cache.get(keyword)
        if results is None:
            queryset = Project.objects.filter(name__icontains=keyword, is_disable=False)
            results = [
                {"id": str(project.id), "display_name": project.name}
                for project in queryset[page.slice_from : page.slice_to]
            ]
            cache.set(keyword, results, CACHE_TIME_FOR_PROJECT)
        return ListResult(results=results, count=len(results))

    def list_attr(self, **options):
        """
        project 资源没有属性，返回空
        """
        return ListResult(results=[], count=0)

    def list_attr_value(self, filter, page, **options):
        """
        project 资源没有属性，返回空
        """
        return ListResult(results=[], count=0)

    def list_instance(self, filter, page, **options):
        """
        project 没有上层资源，不需要处理 filter 中的字段
        """
        queryset = Project.objects.all()

        count = queryset.count()
        results = [{"id": str(p.id), "display_name": p.name} for p in queryset[page.slice_from : page.slice_to]]

        return ListResult(results=results, count=count)

    def fetch_instance_info(self, filter, **options):
        """
        project 没有定义属性，只处理 filter 中的 ids 字段
        """
        ids = []
        if filter.ids:
            ids = [int(i) for i in filter.ids]

        queryset = Project.objects.filter(id__in=ids)

        count = queryset.count()
        results = [{"id": str(p.id), "display_name": p.name} for p in queryset]
        return ListResult(results=results, count=count)

    def list_instance_by_policy(self, filter, page, **options):
        """
        project 资源只处理 id 即可，owner 都是 admin，不处理
        """

        expression = filter.expression
        if not expression:
            return ListResult(results=[], count=0)

        key_mapping = {"project.id": "id"}
        converter = DjangoQuerySetConverter(key_mapping)
        filters = converter.convert(expression)

        queryset = Project.objects.filter(filters)
        count = queryset.count()
        results = [{"id": str(p.id), "display_name": p.name} for p in queryset]

        return ListResult(results=results, count=count)
