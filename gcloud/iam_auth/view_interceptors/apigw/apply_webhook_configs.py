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

from iam import Action, Subject
from iam.contrib.tastypie.shortcuts import allow_or_raise_immediate_response_for_resources_list

from gcloud.iam_auth import IAMMeta
from gcloud.iam_auth import get_iam_client
from gcloud.iam_auth import res_factory
from gcloud.iam_auth.intercept import ViewInterceptor
from gcloud.tasktmpl3.models import TaskTemplate

iam = get_iam_client()


class ApplyWebhookConfigs(ViewInterceptor):
    def process(self, request, *args, **kwargs):
        data = json.loads(request.body)
        template_ids = data.get("template_ids", [])
        subject = Subject("user", request.user.username)

        existing_templates = TaskTemplate.objects.filter(
            project_id=request.project.id, id__in=template_ids, is_deleted=False
        ).values_list("id", flat=True)
        missing_template_ids = set(template_ids) - set(list(existing_templates))
        if missing_template_ids:
            error_message = f"The templates already not exist {missing_template_ids}"
            logging.error(error_message)
            raise ValueError(error_message)

        action = Action(IAMMeta.FLOW_EDIT_ACTION)
        resources_list = res_factory.resources_list_for_flows(template_ids)

        allow_or_raise_immediate_response_for_resources_list(
            iam=iam,
            system=IAMMeta.SYSTEM_ID,
            subject=subject,
            action=action,
            resources_list=resources_list,
        )
