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

from iam import Action, Subject
from iam.exceptions import AuthFailedException
from iam.shortcuts import allow_or_raise_auth_failed

from gcloud.core.models import Project
from gcloud.iam_auth import IAMMeta, get_iam_client, res_factory
from gcloud.iam_auth.intercept import ViewInterceptor

iam = get_iam_client()


class _ProjectActionInterceptor(ViewInterceptor):
    """Django function view 通用项目级 IAM 校验拦截器基类。

    APIGW 侧的 ProjectViewInterceptor 依赖 ``@project_inject`` 注入的
    ``request.project``，而 Django 侧（taskflow3/tasktmpl3/contrib 等）一般
    通过 URL 路径以 ``kwargs["project_id"]`` 传入项目 ID，因此提供一份独立的
    基于 kwargs 的实现，避免在每个视图模块重复书写鉴权样板。
    """

    action = None

    def process(self, request, *args, **kwargs):
        project_id = kwargs.get("project_id")
        if project_id is None:
            project_id = request.GET.get("project_id") or request.POST.get("project_id")

        subject = Subject("user", request.user.username)
        action = Action(self.action)

        # project_id 缺失或指向不存在的项目时，统一按鉴权失败(403)处理：
        # 1. 避免 resources_for_project 内部 Project.objects.get(id=None/不存在) 抛
        #    DoesNotExist 造成 500，攻击者可借 500/403 差异探测拦截器是否挂载；
        # 2. 缺少项目作用域的请求本就无法通过对象级鉴权，直接拒绝更安全。
        if not project_id:
            raise AuthFailedException(IAMMeta.SYSTEM_ID, subject, action, [])
        try:
            resources = res_factory.resources_for_project(project_id)
        except Project.DoesNotExist:
            raise AuthFailedException(IAMMeta.SYSTEM_ID, subject, action, [])

        allow_or_raise_auth_failed(
            iam=iam,
            system=IAMMeta.SYSTEM_ID,
            subject=subject,
            action=action,
            resources=resources,
            cache=True,
        )


class ProjectViewInterceptor(_ProjectActionInterceptor):
    """项目查看级权限校验，对应 IAMMeta.PROJECT_VIEW_ACTION。"""

    action = IAMMeta.PROJECT_VIEW_ACTION


class ProjectFlowCreateInterceptor(_ProjectActionInterceptor):
    """项目下流程创建权限校验，对应 IAMMeta.FLOW_CREATE_ACTION。

    用于 import / check_before_import 等"导入前置探测"接口，与正式导入接口的
    项目级权限保持一致，避免攻击者借助预检接口探测目标项目的流程冲突情况。
    """

    action = IAMMeta.FLOW_CREATE_ACTION
