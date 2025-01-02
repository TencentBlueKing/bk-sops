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
from iam.shortcuts import allow_or_raise_auth_failed

from gcloud.iam_auth import IAMMeta
from gcloud.iam_auth import get_iam_client
from gcloud.iam_auth import res_factory
from gcloud.iam_auth.intercept import ViewInterceptor
from gcloud.contrib.template_market.models import TemplateSharedRecord

iam = get_iam_client()


class CopyTemplateInterceptor(ViewInterceptor):
    def process(self, request, *args, **kwargs):
        data = json.loads(request.body)
        new_project_id = data.get("new_project_id")
        template_ids = data.get("template_ids")
        subject = Subject("user", request.user.username)

        existing_records = TemplateSharedRecord.objects.filter(
            project_id=request.project.id, template_id__in=template_ids
        ).values_list("template_id", flat=True)

        missing_template_ids = set(template_ids) - set(existing_records)
        if missing_template_ids:
            error_message = f"The following templates are not shared {missing_template_ids}"
            logging.error(error_message)
            raise ValueError(error_message)

        action = Action(IAMMeta.FLOW_CREATE_ACTION)
        resources = res_factory.resources_for_project(new_project_id)
        allow_or_raise_auth_failed(iam, IAMMeta.SYSTEM_ID, subject, action, resources, cache=True)
