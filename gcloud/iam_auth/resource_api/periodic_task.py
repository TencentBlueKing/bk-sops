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

from django.db.models import Q
from iam import PathEqDjangoQuerySetConverter
from iam.resource.provider import ListResult, ResourceProvider

from gcloud.core.models import Project
from gcloud.periodictask.models import PeriodicTask


def periodic_task_path_value_hook(value):
    # get id in "/project,id/"
    return value[1:-1].split(",")[1]


class PeriodicTaskResourceProvider(ResourceProvider):
    def list_attr(self, **options):
        """
        periodic_task 不包含属性
        """
        return ListResult(results=[])

    def list_attr_value(self, filter, page, **options):
        """
        periodic_task 不包含属性
        """

        return ListResult(results=[])

    def list_instance(self, filter, page, **options):
        """
        periodic_task 上层资源为 project
        """
        queryset = []
        with_path = False

        if not (filter.parent or filter.search or filter.resource_type_chain):
            queryset = PeriodicTask.objects.all()
        elif filter.parent:
            parent_id = filter.parent["id"]
            if parent_id:
                queryset = PeriodicTask.objects.filter(project_id=str(parent_id))
        elif filter.search and filter.resource_type_chain:
            # 返回结果需要带上资源拓扑路径信息
            with_path = True
            # 过滤 project periodic_task 名称
            project_keywords = filter.search.get("project", [])
            periodic_task_keywords = filter.search.get("periodic_task", [])

            project_filter = Q()
            periodic_task_filter = Q()

            for keyword in project_keywords:
                project_filter |= Q(name__icontains=keyword)

            for keyword in periodic_task_keywords:
                periodic_task_filter |= Q(task__name__icontains=keyword)  # TODO 优化

            project_ids = Project.objects.filter(project_filter).values_list("id", flat=True)
            queryset = PeriodicTask.objects.filter(project_id__in=list(project_ids)).filter(periodic_task_filter)

        results = [
            {"id": str(periodic_task.id), "display_name": periodic_task.name}
            for periodic_task in queryset[page.slice_from : page.slice_to]
        ]

        if with_path:
            results = [
                {
                    "id": str(periodic_task.id),
                    "display_name": periodic_task.name,
                    "path": [
                        [
                            {
                                "type": "project",
                                "id": str(periodic_task.project_id),
                                "display_name": periodic_task.project.name,
                            }
                        ]
                    ],
                }
                for periodic_task in queryset[page.slice_from : page.slice_to]
            ]

        return ListResult(results=results)

    def fetch_instance_info(self, filter, page, **options):
        """
        periodic_task 没有定义属性，只处理 filter 中的 ids 字段
        """
        ids = []
        if filter.ids:
            ids = [int(i) for i in filter.ids]

        results = [
            {"id": str(periodic_task.id), "display_name": periodic_task.name}
            for periodic_task in PeriodicTask.objects.filter(id__in=ids)
        ]
        return ListResult(results=results)

    def list_instance_by_policy(self, filter, page, **options):
        """
        periodic_task
        """

        expression = filter.expression
        if not expression:
            return ListResult(results=[])

        key_mapping = {
            "periodic_task.id": "id",
            "periodic_task.owner": "task__creator",  # TODO 优化
            "periodic_task._iam_path_": "project__id",
        }
        converter = PathEqDjangoQuerySetConverter(key_mapping, {"project__id": periodic_task_path_value_hook})
        filters = converter.convert(expression)

        results = [
            {"id": str(periodic_task.id), "display_name": periodic_task.name}
            for periodic_task in PeriodicTask.objects.filter(filters)[page.slice_from : page.slice_to]
        ]

        return ListResult(results=results)
