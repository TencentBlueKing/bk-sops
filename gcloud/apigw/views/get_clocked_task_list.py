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
from apigw_manager.apigw.decorators import apigw_require
from blueapps.account.decorators import login_exempt
from django.views.decorators.http import require_GET

from gcloud import err_code
from gcloud.apigw.decorators import return_json_response, timezone_inject, project_inject, mark_request_whether_is_trust
from gcloud.apigw.views.utils import paginate_list_data
from gcloud.clocked_task.models import ClockedTask
from gcloud.clocked_task.serializer import ClockedTaskSerializer
from gcloud.constants import CLOCKED_TASK_STATE
from gcloud.core.apis.drf.viewsets import IAMMixin
from gcloud.iam_auth import IAMMeta, get_iam_client
from gcloud.iam_auth.intercept import iam_intercept
from gcloud.iam_auth.resource_helpers.clocked_task import ClockedTaskResourceHelper
from gcloud.iam_auth.utils import get_flow_allowed_actions_for_user
from gcloud.iam_auth.view_interceptors.apigw.clocked_task_view import ProjectAndTaskViewInterceptor

iam = get_iam_client()


# 单独创建一个类是因为权限校验需要，需要 iam_resource_helper 属性
class ClockedTaskViewSet(IAMMixin):
    iam_resource_helper = ClockedTaskResourceHelper(
        iam=iam,
        system=IAMMeta.SYSTEM_ID,
        actions=[
            IAMMeta.CLOCKED_TASK_VIEW_ACTION,
            IAMMeta.CLOCKED_TASK_EDIT_ACTION,
            IAMMeta.CLOCKED_TASK_DELETE_ACTION,
        ],
    )


clocked_task_viewset = ClockedTaskViewSet()

VALID_STATES = [i[0] for i in CLOCKED_TASK_STATE]


@login_exempt
@require_GET
@apigw_require
@return_json_response
@mark_request_whether_is_trust
@project_inject
@timezone_inject
@iam_intercept(ProjectAndTaskViewInterceptor())
def get_clocked_task_list(request, project_id):
    """
    获取clocked_task列表（支持分页）
    """
    project = request.project
    filter_kwargs = dict(project_id=project.id)

    # 获取查询参数，前端页面的查询条件
    task_id = request.GET.get("id", None)
    task_name = request.GET.get("task_name", None)
    creator = request.GET.get("creator", None)
    editor = request.GET.get("editor", None)
    state = request.GET.get("state", None)

    if task_id:
        try:
            filter_kwargs["id"] = int(task_id)
        except ValueError:
            # 非数字输入，返回错误响应
            return {
                "result": False,
                "message": "参数id必须为数字",
                "code": err_code.REQUEST_PARAM_INVALID.code,
            }
    if task_name:
        filter_kwargs["task_name__icontains"] = task_name
    if creator:
        filter_kwargs["creator__icontains"] = creator
    if editor:
        filter_kwargs["editor__icontains"] = editor
    if state:
        # 校验state参数是否为有效值
        if state not in VALID_STATES:
            return {
                "result": False,
                "message": f"参数state必须为以下值之一: {', '.join(VALID_STATES)}",
                "code": err_code.REQUEST_PARAM_INVALID.code,
            }
        filter_kwargs["state"] = state

    queryset = ClockedTask.objects.filter(**filter_kwargs)

    # 分页
    paginated_queryset, count = paginate_list_data(request, queryset, without_count=False)

    # 序列化数据
    result_serializer = ClockedTaskSerializer(paginated_queryset, many=True)

    deserialized_instances = result_serializer.data

    auth_actions = clocked_task_viewset.iam_get_instances_auth_actions(request, paginated_queryset) or {}
    template_view_actions = get_flow_allowed_actions_for_user(
        request.user.username, [IAMMeta.FLOW_VIEW_ACTION], [inst.template_id for inst in paginated_queryset]
    )
    for deserialized_instance in deserialized_instances:
        deserialized_instance["auth_actions"] = auth_actions.get(deserialized_instance["id"], [])
        tmpl_id = str(deserialized_instance["template_id"])
        if tmpl_id in template_view_actions and template_view_actions[tmpl_id][IAMMeta.FLOW_VIEW_ACTION]:
            deserialized_instance["auth_actions"].append(IAMMeta.FLOW_VIEW_ACTION)

    response = {
        "result": True,
        "data": deserialized_instances,
        "count": count,
        "code": err_code.SUCCESS.code,
    }
    return response
