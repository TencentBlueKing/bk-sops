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
from django.db.models import Q
from iam import PathEqDjangoQuerySetConverter
from iam.contrib.django.dispatcher import InvalidPageException
from iam.resource.provider import ListResult, ResourceProvider

from gcloud.clocked_task.models import ClockedTask
from gcloud.core.models import Project
from gcloud.iam_auth.conf import SEARCH_INSTANCE_CACHE_TIME

attr_names = {"en": {"iam_resource_owner": "Resource Owner"}, "zh-cn": {"iam_resource_owner": "资源创建者"}}


def clocked_task_path_value_hook(value):
    # get id in "/project,id/"
    return value[1:-1].split(",")[1]


class ClockedTaskResourceProvider(ResourceProvider):
    def pre_search_instance(self, filter, page, **options):
        if page.limit == 0 or page.limit > 1000:
            raise InvalidPageException("limit in page too large")

    def get_project_ids(self, tenant_id, extra_filter=Q()):

        return list(Project.objects.filter(tenant_id=tenant_id).filter(extra_filter).values_list("id", flat=True))

    def search_instance(self, filter, page, **options):
        """
        clocked task search instance
        """
        keyword = filter.keyword
        cache_keyword = "iam_search_instance_clocked_task_{}".format(keyword)
        project_id = filter.parent["id"] if filter.parent else None

        results = cache.get(cache_keyword)
        if results is None:
            project_filter = Q()
            if project_id:
                project_filter = Q(project_id=project_id)
            project_ids = self.get_project_ids(options["bk_tenant_id"], project_filter)
            queryset = ClockedTask.objects.filter(task_name__icontains=keyword, project_id__in=project_ids).only(
                "task_name"
            )
            results = [
                {"id": str(clocked_task.id), "display_name": clocked_task.task_name}
                for clocked_task in queryset[page.slice_from : page.slice_to]
            ]
            cache.set(cache_keyword, results, SEARCH_INSTANCE_CACHE_TIME)
        return ListResult(results=results, count=len(results))

    def list_attr(self, **options):
        """
        clocked_task 包含 iam_resource_owner 属性
        """
        return ListResult(
            results=[
                {"id": "iam_resource_owner", "display_name": attr_names[options["language"]]["iam_resource_owner"]}
            ],
            count=1,
        )

    def list_attr_value(self, filter, page, **options):
        """
        clocked_task 包含 iam_resource_owner 属性
        """
        if filter.attr == "iam_resource_owner":
            user_model = get_user_model()
            users = user_model.objects.filter(tenant_id=options["bk_tenant_id"]).values_list("username", flat=True)
            results = [{"id": username, "display_name": username} for username in users]
        else:
            results = []

        return ListResult(results=results, count=len(results))

    def list_instance(self, filter, page, **options):
        """
        clocked_task 上层资源为 project
        """
        queryset = []
        with_path = False
        project_ids = self.get_project_ids(options["bk_tenant_id"])
        if not (filter.parent or filter.search or filter.resource_type_chain):
            queryset = ClockedTask.objects.filter(project_id__in=project_ids)
        elif filter.parent:
            parent_id = filter.parent["id"]
            if parent_id:
                project = Project.objects.filter(tenant_id=options["bk_tenant_id"], id=parent_id).first()
                if project:
                    queryset = ClockedTask.objects.filter(project_id=parent_id)
                else:
                    queryset = ClockedTask.objects.none()
            else:
                queryset = ClockedTask.objects.filter(project_id__in=project_ids)
        elif filter.search and filter.resource_type_chain:
            # 返回结果需要带上资源拓扑路径信息
            with_path = True
            # 过滤 project clocked_task 名称
            project_keywords = filter.search.get("project", [])
            clocked_task_keywords = filter.search.get("clocked_task", [])

            project_keyword_filter = Q()
            clocked_task_filter = Q()

            for keyword in project_keywords:
                project_keyword_filter |= Q(name__icontains=keyword)

            for keyword in clocked_task_keywords:
                clocked_task_filter |= Q(task_name__icontains=keyword)

            project_ids = self.get_project_ids(options["bk_tenant_id"], project_keyword_filter)
            queryset = ClockedTask.objects.filter(project_id__in=project_ids).filter(clocked_task_filter)

        count = queryset.count()
        results = [
            {"id": str(clocked_task.id), "display_name": clocked_task.task_name}
            for clocked_task in queryset[page.slice_from : page.slice_to]
        ]

        if with_path:
            include_project_ids = [
                clocked_task.project_id for clocked_task in queryset[page.slice_from : page.slice_to]
            ]
            projects = list(Project.objects.filter(id__in=include_project_ids).values("id", "name"))
            project_mapping = {project["id"]: project["name"] for project in projects}
            results = [
                {
                    "id": str(clocked_task.id),
                    "display_name": clocked_task.task_name,
                    "path": [
                        [
                            {
                                "type": "project",
                                "id": str(clocked_task.project_id),
                                "display_name": project_mapping[clocked_task.project_id],
                            }
                        ]
                    ],
                }
                for clocked_task in queryset[page.slice_from : page.slice_to]
            ]

        return ListResult(results=results, count=count)

    def fetch_instance_info(self, filter, **options):
        """
        clocked_task 没有定义属性，只处理 filter 中的 ids 字段
        """
        queryset = ClockedTask.objects.none()
        if filter.ids:
            ids = [int(i) for i in filter.ids]
            project_ids = self.get_project_ids(options["bk_tenant_id"])
            queryset = ClockedTask.objects.filter(id__in=ids, project_id__in=project_ids)

        count = queryset.count()

        results = [
            {
                "id": str(clocked_task.id),
                "display_name": clocked_task.task_name,
                "_bk_iam_approver_": clocked_task.creator,
            }
            for clocked_task in queryset
        ]
        return ListResult(results=results, count=count)

    def list_instance_by_policy(self, filter, page, **options):
        """
        clocked_task
        """

        expression = filter.expression
        if not expression:
            return ListResult(results=[], count=0)

        key_mapping = {
            "clocked_task.id": "id",
            "clocked_task.owner": "creator",
            "clocked_task._bk_iam_path_": "project_id",
        }
        converter = PathEqDjangoQuerySetConverter(key_mapping, {"project_id": clocked_task_path_value_hook})
        filters = converter.convert(expression)
        project_ids = self.get_project_ids(options["bk_tenant_id"])
        queryset = ClockedTask.objects.filter(filters, project_id__in=project_ids)
        count = queryset.count()

        results = [
            {"id": str(clocked_task.id), "display_name": clocked_task.task_name}
            for clocked_task in queryset[page.slice_from : page.slice_to]
        ]

        return ListResult(results=results, count=count)
