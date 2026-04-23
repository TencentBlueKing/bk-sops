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

import ujson as json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from blueapps.account.decorators import login_exempt
from gcloud import err_code
from gcloud.apigw.decorators import mark_request_whether_is_trust, return_json_response
from gcloud.apigw.decorators import project_inject
from gcloud.iam_auth.intercept import iam_intercept
from gcloud.iam_auth.view_interceptors.apigw.project_edit import ProjectEditInterceptor
from gcloud.core.models import ProjectConfig
from apigw_manager.apigw.decorators import apigw_require
from rest_framework import serializers


class ProjectExecutorProxySerializer(serializers.ModelSerializer):
    """
    专用于 "修改项目执行代理人" 接口的 serializer，
    仅允许修改 executor_proxy / executor_proxy_exempts，
    避免 custom_display_configs 等非相关字段被一并暴露/修改。
    两个字段均为必填，与网关文档声明保持一致。
    """

    class Meta:
        model = ProjectConfig
        fields = ["executor_proxy", "executor_proxy_exempts"]
        extra_kwargs = {
            "executor_proxy": {"required": True, "allow_blank": True},
            "executor_proxy_exempts": {"required": True, "allow_blank": True},
        }

    def validate_executor_proxy(self, value):
        user = getattr(self.context.get("request"), "user", None)
        if not user:
            raise serializers.ValidationError("user can not be empty.")
        if user.username != value and value:
            raise serializers.ValidationError("代理人仅可设置为本人")
        return value


@login_exempt
@csrf_exempt
@require_POST
@apigw_require
@return_json_response
@mark_request_whether_is_trust
@project_inject
@iam_intercept(ProjectEditInterceptor())
def modify_project_executor_proxy(request, project_id):
    """
    修改项目执行代理人配置
    """
    project = request.project

    try:
        params = json.loads(request.body)
    except Exception:
        return {"result": False, "message": "invalid json format", "code": err_code.REQUEST_PARAM_INVALID.code}

    # 获取或创建项目配置
    try:
        project_config, created = ProjectConfig.objects.get_or_create(project_id=project.id)
    except Exception as e:
        return {"result": False, "message": f"Failed to get project config: {str(e)}",
                "code": err_code.UNKNOWN_ERROR.code}

    # 使用专用序列化器进行参数校验和更新（仅允许修改 executor_proxy / executor_proxy_exempts）
    serializer = ProjectExecutorProxySerializer(
        instance=project_config,
        data=params,
        context={'request': request},
    )

    if not serializer.is_valid():
        return {
            "result": False,
            "message": serializer.errors,
            "code": err_code.REQUEST_PARAM_INVALID.code
        }

    # 更新配置
    serializer.save()
    data = dict(serializer.validated_data)
    data["project_id"] = project.id
    return {"result": True, "data": data, "code": err_code.SUCCESS.code}
