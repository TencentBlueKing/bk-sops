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

import json
import logging

from gcloud.iam_auth import IAMMeta, PermissionCheck, PermissionService, res_factory
from gcloud.iam_auth.exceptions import IAMPermissionDenied
from gcloud.iam_auth.intercept import ViewInterceptor
from gcloud.tasktmpl3.models import TaskTemplate


class ApplyWebhookConfigs(ViewInterceptor):
    def process(self, request, *args, **kwargs):
        data = json.loads(request.body)
        template_ids = data.get("template_ids", [])
        tenant_id = request.user.tenant_id

        existing_templates = TaskTemplate.objects.filter(
            project_id=request.project.id,
            project__tenant_id=tenant_id,
            id__in=template_ids,
            is_deleted=False,
        ).values_list("id", flat=True)
        missing_template_ids = set(template_ids) - set(list(existing_templates))
        if missing_template_ids:
            error_message = f"The templates already not exist {missing_template_ids}"
            logging.error(error_message)
            raise ValueError(error_message)

        # Trusted applications skip only the user policy check. Template
        # existence, project ownership and tenant validation above still run.
        if request.is_trust:
            return

        resources = [item[0] for item in res_factory.resources_list_for_flows(template_ids, tenant_id)]
        decisions = PermissionService().allowed_resources(
            request.user.username, tenant_id, IAMMeta.FLOW_EDIT_ACTION, resources
        )
        missing = [
            PermissionCheck(IAMMeta.FLOW_EDIT_ACTION, resource)
            for resource in resources
            if not decisions[str(resource.id)]
        ]
        if missing:
            raise IAMPermissionDenied(missing)
