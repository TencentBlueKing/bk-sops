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
the specific language governing permissions and limitations under the License.
"""


import ujson as json
from apigw_manager.apigw.decorators import apigw_require
from blueapps.account.decorators import login_exempt
from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework import serializers

from gcloud import err_code
from gcloud.apigw.decorators import mark_request_whether_is_trust, project_inject, return_json_response
from gcloud.contrib.audit.utils import bk_audit_add_event
from gcloud.contrib.operate_record.constants import OperateSource, OperateType, RecordType
from gcloud.contrib.operate_record.signal import operate_record_signal
from gcloud.iam_auth import IAMMeta
from gcloud.iam_auth.intercept import iam_intercept
from gcloud.iam_auth.view_interceptors.apigw import TemplateEditInterceptor
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.tasktmpl3.signals import post_template_save_commit
from gcloud.template_base.domains.template_manager import TemplateManager


manager = TemplateManager(template_model_cls=TaskTemplate)


class ExecutorProxySerializer(serializers.Serializer):
    """
    仅校验 executor_proxy 字段的 serializer
    走完整的 required/type 校验，避免手动 params.get 绕过
    """

    executor_proxy = serializers.CharField(
        help_text="执行代理人", required=True, allow_blank=True, allow_null=False
    )

    def validate_executor_proxy(self, value):
        user = getattr(self.context.get("request"), "user", None)
        if not user:
            raise serializers.ValidationError("user can not be empty.")
        if value and user.username != value:
            raise serializers.ValidationError(_("The agent may only be designated as the individual themselves."))
        return value


@login_exempt
@csrf_exempt
@require_POST
@apigw_require
@return_json_response
@mark_request_whether_is_trust
@project_inject
@iam_intercept(TemplateEditInterceptor())
def modify_template_executor_proxy(request, template_id, project_id):
    project = request.project
    try:
        params = json.loads(request.body)
    except Exception:
        return {"result": False, "message": "invalid json format", "code": err_code.REQUEST_PARAM_INVALID.code}

    # 通过 serializer 走完整字段校验（required/type/非法值）
    serializer = ExecutorProxySerializer(data=params, context={"request": request})
    if not serializer.is_valid():
        return {
            "result": False,
            "message": json.dumps(serializer.errors),
            "code": err_code.REQUEST_PARAM_INVALID.code,
        }
    validated_executor_proxy = serializer.validated_data["executor_proxy"]

    try:
        template = TaskTemplate.objects.get(id=template_id, project_id=project.id, is_deleted=False)
    except TaskTemplate.DoesNotExist:
        return {
            "result": False,
            "message": "template[id={template_id}] of project[project_id={project_id}] does not exist".format(
                template_id=template_id, project_id=project.id
            ),
            "code": err_code.CONTENT_NOT_EXIST.code,
        }

    editor = request.user.username

    # 走模板正常更新链路：
    with transaction.atomic():
        template.executor_proxy = validated_executor_proxy
        template.save(update_fields=["executor_proxy"])

        update_result = manager.update_pipeline(
            pipeline_template=template.pipeline_template, editor=editor,
        )
        if not update_result["result"]:
            return {
                "result": False,
                "message": update_result["message"],
                "code": err_code.UNKNOWN_ERROR.code,
            }

    # 发送模板保存信号（触发 statistics 等 side effect）
    post_template_save_commit.send(
        sender=TaskTemplate,
        project_id=template.project_id,
        template_id=template.id,
        is_deleted=template.is_deleted,
    )

    # 记录操作流水
    operate_record_signal.send(
        sender=RecordType.template.name,
        operator=editor,
        operate_type=OperateType.update.name,
        operate_source=OperateSource.api.name,
        instance_id=template.id,
        project_id=template.project_id,
    )

    # 审计上报
    bk_audit_add_event(
        username=editor,
        action_id=IAMMeta.FLOW_EDIT_ACTION,
        resource_id=IAMMeta.FLOW_RESOURCE,
        instance=template,
    )

    return {
        "result": True,
        "data": {"template_id": template.id, "executor_proxy": template.executor_proxy},
        "code": err_code.SUCCESS.code,
    }
