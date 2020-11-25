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

import ujson as json

from iam import Action, Subject
from iam.shortcuts import allow_or_raise_auth_failed

from gcloud.iam_auth import IAMMeta
from gcloud.iam_auth import res_factory
from gcloud.iam_auth import get_iam_client
from gcloud.iam_auth.intercept import ViewInterceptor
from gcloud.constants import PROJECT
from gcloud.tasktmpl3.constants import NON_COMMON_TEMPLATE_TYPES

iam = get_iam_client()


class CreatePeriodicTaskInterceptor(ViewInterceptor):
    def process(self, request, *args, **kwargs):
        if request.is_trust:
            return

        params = json.loads(request.body)
        template_source = params.get("template_source", PROJECT)
        template_id = kwargs["template_id"]

        subject = Subject("user", request.user.username)

        if template_source in NON_COMMON_TEMPLATE_TYPES:
            action = Action(IAMMeta.FLOW_CREATE_PERIODIC_TASK_ACTION)
            resources = res_factory.resources_for_flow(template_id)
            allow_or_raise_auth_failed(iam, IAMMeta.SYSTEM_ID, subject, action, resources)

        else:
            action = Action(IAMMeta.COMMON_FLOW_CREATE_PERIODIC_TASK_ACTION)
            resources = res_factory.resources_for_common_flow(template_id)
            allow_or_raise_auth_failed(iam, IAMMeta.SYSTEM_ID, subject, action, resources)
