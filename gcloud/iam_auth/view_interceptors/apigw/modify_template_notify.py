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

from gcloud.iam_auth import IAMMeta, PermissionCheck, PermissionService
from gcloud.iam_auth.intercept import ViewInterceptor
from gcloud.iam_auth.request_resources import load_resource_for_request


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
        tenant_id = request.user.tenant_id
        params = json.loads(request.body)

        template_source = params.get("common", False)
        template_id = kwargs["template_id"]
        # 根据模板来源设置不同的权限动作
        if not template_source:
            # 项目模板需要流程编辑权限
            action_id = IAMMeta.FLOW_EDIT_ACTION
            resource = load_resource_for_request(request, IAMMeta.FLOW_RESOURCE, template_id)
        else:
            # 公共模板需要公共流程编辑权限
            action_id = IAMMeta.COMMON_FLOW_EDIT_ACTION
            resource = load_resource_for_request(request, IAMMeta.COMMON_FLOW_RESOURCE, template_id)

        # trust only skips the user policy after tenant and ownership checks.
        if request.is_trust:
            return
        PermissionService().require(request.user.username, tenant_id, PermissionCheck(action_id, resource))
