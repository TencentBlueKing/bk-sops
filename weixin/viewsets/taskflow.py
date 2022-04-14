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

from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.common_template.models import CommonTemplate
from gcloud.core.apis.drf.viewsets import TaskFlowInstanceViewSet
from gcloud.iam_auth import IAMMeta
from weixin.utils import iam_based_obj_list_filter


class WxTaskFlowInstanceViewSet(TaskFlowInstanceViewSet):
    def destroy(self, request, *args, **kwargs):
        raise PermissionDenied

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        # 支持使用方配置不分页
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page if page else queryset, many=True)
        # 注入权限
        data = self.injection_auth_actions(request, serializer.data, queryset)
        # 注入template_info（name、deleted
        # 项目流程
        template_ids = [
            int(instance["template_id"])
            for instance in data
            if instance["template_id"] and instance["template_source"] == "project"
        ]
        template_info = TaskTemplate.objects.filter(id__in=template_ids).values(
            "id", "pipeline_template__name", "is_deleted"
        )
        template_info_map = {
            str(t["id"]): {"name": t["pipeline_template__name"], "is_deleted": t["is_deleted"]} for t in template_info
        }
        # 公共流程
        common_template_ids = [
            int(instance["template_id"])
            for instance in data
            if instance["template_id"] and instance["template_source"] == "common"
        ]
        common_template_info = CommonTemplate.objects.filter(id__in=common_template_ids).values(
            "id", "pipeline_template__name", "is_deleted"
        )
        common_template_info_map = {
            str(t["id"]): {"name": t["pipeline_template__name"], "is_deleted": t["is_deleted"]}
            for t in common_template_info
        }
        for instance in data:
            if instance["template_source"] == "project":
                instance["template_name"] = template_info_map.get(instance["template_id"], {}).get("name")
                instance["template_deleted"] = template_info_map.get(instance["template_id"], {}).get(
                    "is_deleted", True
                )
            else:
                instance["template_name"] = common_template_info_map.get(instance["template_id"], {}).get("name")
                instance["template_deleted"] = common_template_info_map.get(instance["template_id"], {}).get(
                    "is_deleted", True
                )
        data = iam_based_obj_list_filter(data, [IAMMeta.TASK_VIEW_ACTION, IAMMeta.TASK_OPERATE_ACTION])
        return self.get_paginated_response(data) if page is not None else Response(data)
