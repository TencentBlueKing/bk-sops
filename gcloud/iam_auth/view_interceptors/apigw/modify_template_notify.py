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

from iam import Action, Subject
from iam.shortcuts import allow_or_raise_auth_failed

from gcloud.iam_auth import IAMMeta
from gcloud.iam_auth import get_iam_client
from gcloud.iam_auth import res_factory
from gcloud.iam_auth.intercept import ViewInterceptor

iam = get_iam_client()


class NotifyTemplateInterceptor(ViewInterceptor):
    """流程模板执行失败通知权限拦截器"""

    def process(self, request, *args, **kwargs):
        """
        处理权限验证
        Args:
            request: HTTP请求对象
            args: 位置参数
            kwargs: 关键字参数
        """
        # 如果是信任请求，跳过权限验证
        if request.is_trust:
            return

        params = json.loads(request.body)

        template_source = params.get("common", False)
        template_id = kwargs["template_id"]
        subject = Subject("user", request.user.username)
        # 根据模板来源设置不同的权限动作
        if not template_source:
            # 项目模板需要流程编辑权限
            action = Action(IAMMeta.FLOW_EDIT_ACTION)
            resources = res_factory.resources_for_flow(template_id)
        else:
            # 公共模板需要公共流程编辑权限
            action = Action(IAMMeta.COMMON_FLOW_EDIT_ACTION)
            resources = res_factory.resources_for_common_flow(template_id)

        # 验证权限
        allow_or_raise_auth_failed(iam, IAMMeta.SYSTEM_ID, subject, action, resources, cache=True)
