# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db.models import Q, Value
from django.utils.translation import gettext_lazy as _
from iam import PathEqDjangoQuerySetConverter
from iam.contrib.django.dispatcher import InvalidPageException
from iam.resource.provider import ListResult, ResourceProvider

from gcloud.core.models import Project
from gcloud.iam_auth.conf import SEARCH_INSTANCE_CACHE_TIME
from gcloud.taskflow3.models import TaskFlowInstance

attr_names = {
    "en": {"type": "Task type", "iam_resource_owner": "Resource owner"},
    "zh-cn": {"type": _("任务类型"), "iam_resource_owner": _("资源创建者")},
}

attr_value_names = {
    "en": {"common": "Normal task", "common_func": "Functional task"},
    "zh-cn": {"common": _("普通任务"), "common_func": _("职能化任务")},
}

attr_value_nameset = {"Normal task"}


def task_path_value_hook(value):
    # get id in "/project,id/"
    return value[1:-1].split(",")[1]


class TaskResourceProvider(ResourceProvider):
    def pre_search_instance(self, filter, page, **options):
        if page.limit == 0 or page.limit > 1000:
            raise InvalidPageException("limit in page too large")

    def pre_list_instance(self, filter, page, **options):
        if page.limit == 0 or page.limit > 1000:
            raise InvalidPageException("limit in page too large")

    def pre_list_instance_by_policy(self, filter, page, **options):
        if page.limit == 0 or page.limit > 1000:
            raise InvalidPageException("limit in page too large")

    def search_instance(self, filter, page, **options):
        """
        task search instance
        """
        keyword = filter.keyword
        cache_keyword = "iam_search_instance_task_{}".format(keyword)
        project_id = filter.parent["id"] if filter.parent else None

        results = cache.get(cache_keyword)
        if results is None:
            queryset = (
                TaskFlowInstance.objects.select_related("pipeline_instance")
                .filter(pipeline_instance__name__icontains=keyword, is_deleted=Value(0))
                .only("pipeline_instance__name")
            )
            if project_id:
                queryset = queryset.filter(project__id=project_id)
            results = [
                {"id": str(task.id), "display_name": task.name} for task in queryset[page.slice_from : page.slice_to]
            ]
            cache.set(cache_keyword, results, SEARCH_INSTANCE_CACHE_TIME)
        return ListResult(results=results, count=len(results))

    def list_attr(self, **options):
        """
        task 包含 type 属性
        """
        return ListResult(
            results=[
                {"id": "type", "display_name": attr_names[options["language"]]["type"]},
                {"id": "iam_resource_owner", "display_name": attr_names[options["language"]]["iam_resource_owner"]},
            ],
            count=2,
        )

    def list_attr_value(self, filter, page, **options):
        """
        task 属性值类型较少，不处理 keyword filter
        """
        if filter.attr == "type":
            results = [
                {"id": "common", "display_name": attr_value_names[options["language"]]["common"]},
                {"id": "common_func", "display_name": attr_value_names[options["language"]]["common_func"]},
            ]
        elif filter.attr == "iam_resource_owner":
            user_model = get_user_model()
            users = user_model.objects.all().values_list("username", flat=True)
            results = [{"id": username, "display_name": username} for username in users]
        else:
            results = []

        return ListResult(results=results, count=len(results))

    def list_instance(self, filter, page, **options):
        """
        task 上层资源为 project
        """
        queryset = []
        with_path = False

        if not (filter.parent or filter.search or filter.resource_type_chain):
            queryset = TaskFlowInstance.objects.filter(is_deleted=Value(0))
        elif filter.parent:
            parent_id = filter.parent["id"]
            if parent_id:
                queryset = TaskFlowInstance.objects.filter(project_id=str(parent_id), is_deleted=Value(0))
            else:
                queryset = TaskFlowInstance.objects.filter(is_deleted=Value(0))
        elif filter.search and filter.resource_type_chain:
            # 返回结果需要带上资源拓扑路径信息
            with_path = True
            # 过滤 project task 名称
            project_keywords = filter.search.get("project", [])
            task_keywords = filter.search.get("task", [])

            project_filter = Q()
            task_filter = Q(is_deleted=Value(0))

            for keyword in project_keywords:
                project_filter |= Q(name__icontains=keyword)

            for keyword in task_keywords:
                task_filter |= Q(pipeline_instance__name__icontains=keyword)  # TODO 优化

            project_ids = Project.objects.filter(project_filter).values_list("id", flat=True)
            queryset = TaskFlowInstance.objects.filter(project_id__in=list(project_ids)).filter(task_filter)

        count = queryset.count()
        results = [
            {"id": str(task.id), "display_name": task.name} for task in queryset[page.slice_from : page.slice_to]
        ]

        if with_path:
            results = [
                {
                    "id": str(task.id),
                    "display_name": task.name,
                    "path": [[{"type": "project", "id": str(task.project_id), "display_name": task.project.name}]],
                }
                for task in queryset[page.slice_from : page.slice_to]
            ]

        return ListResult(results=results, count=count)

    def fetch_instance_info(self, filter, **options):
        """
        task 没有定义属性，只处理 filter 中的 ids 字段
        """
        ids = []
        if filter.ids:
            ids = [int(i) for i in filter.ids]

        queryset = TaskFlowInstance.objects.filter(id__in=ids)

        count = queryset.count()
        results = [
            {"id": str(task.id), "display_name": task.name, "_bk_iam_approver_": task.creator} for task in queryset
        ]
        return ListResult(results=results, count=count)

    def list_instance_by_policy(self, filter, page, **options):
        """
        task
        """

        expression = filter.expression
        if not expression:
            return ListResult(results=[], count=0)

        key_mapping = {
            "task.id": "id",
            "task.owner": "pipeline_instance__creator",  # TODO 优化
            "task._bk_iam_path_": "project__id",
            "task.type": "flow_type",
        }
        converter = PathEqDjangoQuerySetConverter(key_mapping, {"project__id": task_path_value_hook})
        filters = converter.convert(expression)

        queryset = TaskFlowInstance.objects.filter(filters)
        count = queryset.count()
        results = [
            {"id": str(task.id), "display_name": task.name} for task in queryset[page.slice_from : page.slice_to]
        ]

        return ListResult(results=results, count=count)
