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
from json import JSONDecodeError

from apigw_manager.apigw.decorators import apigw_require
from blueapps.account.decorators import login_exempt
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework import serializers

from gcloud import err_code
from gcloud.apigw.decorators import mark_request_whether_is_trust, project_inject, return_json_response
from gcloud.common_template.models import CommonTemplate
from gcloud.core.apis.drf.serilaziers.staff_group import StaffGroupSetSerializer
from gcloud.core.models import StaffGroupSet
from gcloud.iam_auth.intercept import iam_intercept
from gcloud.iam_auth.view_interceptors.apigw.modify_template_notify import NotifyTemplateInterceptor
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.conf import settings
from gcloud.tasktmpl3.signals import post_template_save_commit
from gcloud.contrib.operate_record.constants import OperateSource, OperateType, RecordType
from gcloud.contrib.operate_record.signal import operate_record_signal
from gcloud.iam_auth import IAMMeta
from gcloud.contrib.audit.utils import bk_audit_add_event
from gcloud.template_base.domains.template_manager import TemplateManager

get_client_by_user = settings.ESB_GET_CLIENT_BY_USER
DEFAULT_NOTIFY_GROUPS = ["Maintainers", "Developer", "Tester", "ProductPm"]
task_manager = TemplateManager(template_model_cls=TaskTemplate)
common_manager = TemplateManager(template_model_cls=CommonTemplate)


class TemplateNotifyUpdateSerializer(serializers.Serializer):
    """
    专门用于更新模板通知设置的序列化器
    只处理notify_type和notify_receivers字段，避免pipeline_tree校验
    """
    notify_type = serializers.CharField(required=True, allow_blank=False)
    notify_receivers = serializers.CharField(required=True, allow_blank=False)

    def validate_notify_type(self, value):
        """验证通知类型是否合法"""
        if not value:
            return value

        # 获取支持的通知类型
        request = self.context.get('request')
        if not request:
            return value

        client = get_client_by_user(request.user.username)
        result = client.cmsi.get_msg_type()
        if result.get("result"):
            supported_notify_types = [item['type'] for item in result['data']]
        else:
            raise serializers.ValidationError("获取通知类型失败")

        notify_data = json.loads(value)

        if notify_data.get("success", []):
            if not set(notify_data["success"]).issubset(set(supported_notify_types)):
                raise serializers.ValidationError(f"success通知类型不合法，支持的通知类型为：{supported_notify_types}")
        if notify_data.get("fail", []):
            if not set(notify_data["fail"]).issubset(set(supported_notify_types)):
                raise serializers.ValidationError(f"fail通知类型不合法，支持的通知类型为：{supported_notify_types}")

        return value

    def validate_notify_receivers(self, value):
        """验证通知接收者是否合法"""
        if not value:
            return value

        notify_data = json.loads(value)

        request = self.context.get('request')
        if not request:
            return value

        # 详细的字典结构校验
        if notify_data:
            # 检查receiver_group字段
            if "receiver_group" in notify_data and not isinstance(notify_data["receiver_group"], list):
                raise serializers.ValidationError("receiver_group必须是数组类型")

            # 检查more_receiver字段
            if "more_receiver" in notify_data and not isinstance(notify_data["more_receiver"], str):
                raise serializers.ValidationError("more_receiver必须是字符串类型")

            # 检查extra_info字段
            if "extra_info" in notify_data:
                extra_info = notify_data["extra_info"]
                if not isinstance(extra_info, dict):
                    raise serializers.ValidationError("extra_info必须是字典类型")

                # 检查bkchat子字段
                if "bkchat" in extra_info:
                    bkchat = extra_info["bkchat"]
                    if not isinstance(bkchat, dict):
                        raise serializers.ValidationError("bkchat必须是字典类型")

                    # 检查success和fail字段
                    if "success" not in bkchat or not isinstance(bkchat["success"], str):
                        raise serializers.ValidationError("bkchat.success必须是字符串类型")

                    if "fail" not in bkchat or not isinstance(bkchat["fail"], str):
                        raise serializers.ValidationError("bkchat.fail必须是字符串类型")

        # 获取所有用户组
        queryset = StaffGroupSet.objects.filter(is_deleted=False, project_id=request.project.id)
        serializer = StaffGroupSetSerializer(queryset, many=True)
        # 统一转换为字符串类型，兼容客户端传入整型 ID 或字符串 ID 的情况
        supported_groups = [str(item['id']) for item in serializer.data]
        supported_groups.extend(DEFAULT_NOTIFY_GROUPS)

        # 将客户端传入的 receiver_group 元素也统一转换为字符串再做子集判断
        receiver_group = [str(group) for group in notify_data.get('receiver_group', [])]
        if not set(receiver_group).issubset(set(supported_groups)):
            raise serializers.ValidationError(f"receiver_group必须包含在支持的用户组中: {supported_groups}")
        return value

    def update(self, instance, validated_data):
        """
        更新模板的通知设置
        """
        # 更新notify_type字段
        if 'notify_type' in validated_data:
            instance.notify_type = validated_data['notify_type']

        # 更新notify_receivers字段
        if 'notify_receivers' in validated_data:
            instance.notify_receivers = validated_data['notify_receivers']

        request = self.context.get('request')
        editor = request.user.username
        if self.context.get("common", False):
            result = common_manager.update_pipeline(
                pipeline_template=instance.pipeline_template,
                editor=editor
            )
        else:
            result = task_manager.update_pipeline(
                pipeline_template=instance.pipeline_template,
                editor=editor
            )
        if not result["result"]:
            message = result["message"]
            raise serializers.ValidationError(message)
        instance.save()
        return instance


@login_exempt
@csrf_exempt
@require_POST
@apigw_require
@return_json_response
@mark_request_whether_is_trust
@project_inject
@iam_intercept(NotifyTemplateInterceptor())
def modify_template_notify(request, template_id, project_id):
    """
    流程模板执行通知接口

    Args:
        request: HTTP请求对象
        template_id: 模板ID
        project_id: 项目ID

    Returns:
        通知结果
    """
    project = request.project
    try:
        params = json.loads(request.body)
    except JSONDecodeError:
        return {"result": False, "message": "invalid json format.", "code": err_code.REQUEST_PARAM_INVALID.code}

    # 获取参数并进行类型校验
    param_notify_type = params.get("notify_type", {})
    param_notify_receivers = params.get("notify_receivers", {})

    # 顶层类型校验 - notify_type必须是字典
    if not isinstance(param_notify_type, dict):
        return {
            "result": False,
            "message": "Invalid notify_type, expected a dictionary",
            "code": err_code.REQUEST_PARAM_INVALID.code
        }

    # 顶层类型校验 - notify_receivers必须是字典
    if not isinstance(param_notify_receivers, dict):
        return {
            "result": False,
            "message": "Invalid notify_receivers, expected a dictionary",
            "code": err_code.REQUEST_PARAM_INVALID.code
        }

    # 详细的字段校验将在序列化器中完成

    is_common = params.get("common", False)

    try:
        # 获取模板信息
        if is_common:
            template = CommonTemplate.objects.get(id=template_id, is_deleted=False)
        else:
            template = TaskTemplate.objects.get(id=template_id, project_id=project.id, is_deleted=False)
    except CommonTemplate.DoesNotExist:
        return {
            "result": False,
            "message": "template(%s) does not exist" % template_id,
            "code": err_code.CONTENT_NOT_EXIST.code,
        }
    except TaskTemplate.DoesNotExist:
        return {
            "result": False,
            "message": "(%s) template not found" % template_id,
            "code": err_code.CONTENT_NOT_EXIST.code
        }

    # 使用专门的通知更新序列化器
    update_data = {
        "notify_type": json.dumps(param_notify_type),
        "notify_receivers": json.dumps(param_notify_receivers)
    }

    # 使用TemplateNotifyUpdateSerializer进行部分更新
    serializer = TemplateNotifyUpdateSerializer(
        template,
        data=update_data,
        partial=True,
        context={"request": request, "common": is_common}
    )
    if not serializer.is_valid():
        return {
            "result": False,
            "message": "Invalid update data",
            "code": err_code.REQUEST_PARAM_INVALID.code,
            "errors": serializer.errors
        }

    # 保存更新
    serializer.save()

    # 发送信号和记录操作流水
    if is_common:
        # 公用模板
        post_template_save_commit.send(sender=CommonTemplate, template_id=template.id, is_deleted=False)

        operate_record_signal.send(
            sender=RecordType.common_template.name,
            operator=request.user.username,
            operate_type=OperateType.update.name,
            operate_source=OperateSource.api.name,
            instance_id=template.id,
        )
        bk_audit_add_event(
            username=request.user.username,
            action_id=IAMMeta.COMMON_FLOW_EDIT_ACTION,
            resource_id=IAMMeta.COMMON_FLOW_RESOURCE,
            instance=template,
        )
    else:
        post_template_save_commit.send(
            sender=TaskTemplate,
            project_id=template.project_id,
            template_id=template.id,
            is_deleted=template.is_deleted,
        )
        # 记录操作流水
        operate_record_signal.send(
            sender=RecordType.template.name,
            operator=request.user.username,
            operate_type=OperateType.update.name,
            operate_source=OperateSource.api.name,
            instance_id=template.id,
            project_id=template.project.id,
        )
        bk_audit_add_event(
            username=request.user.username,
            action_id=IAMMeta.FLOW_EDIT_ACTION,
            resource_id=IAMMeta.FLOW_RESOURCE,
            instance=template,
        )
    return {
        "result": True,
        "data": {
            "notify_type": param_notify_type,
            "notify_receivers": param_notify_receivers,
            "template_id": int(template_id)
        },
        "code": err_code.SUCCESS.code
    }
