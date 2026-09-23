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
from apigw_manager.apigw.decorators import apigw_require
from blueapps.account.decorators import login_exempt
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from pipeline.core.constants import PE
from pipeline.models import TemplateScheme

from gcloud import err_code
from gcloud.apigw.decorators import mark_request_whether_is_trust, project_inject, return_json_response
from gcloud.apigw.views.utils import logger
from gcloud.iam_auth.intercept import iam_intercept
from gcloud.iam_auth.view_interceptors.apigw import TemplateEditInterceptor
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.template_base.apis.drf.serilaziers.template_scheme import TemplateSchemeSerializer


def validate_scheme_nodes(pipeline_tree, node_ids):
    """
    校验执行方案中的节点是否为流程模板 pipeline_tree 中真实存在的可选节点

    :param pipeline_tree: 流程模板的 pipeline_tree
    :param node_ids: 执行方案中包含的节点ID列表
    :return: 校验通过返回空字符串，否则返回错误信息
    """
    activities = pipeline_tree.get(PE.activities, {})

    not_exist_node_ids = [node_id for node_id in node_ids if node_id not in activities]
    if not_exist_node_ids:
        return "node ids do not exist in template pipeline_tree: {}".format(", ".join(not_exist_node_ids))

    not_optional_node_ids = [node_id for node_id in node_ids if not activities[node_id].get("optional", False)]
    if not_optional_node_ids:
        return "node ids are not optional in template pipeline_tree: {}".format(", ".join(not_optional_node_ids))

    return ""


@login_exempt
@csrf_exempt
@require_POST
@apigw_require
@mark_request_whether_is_trust
@return_json_response
@project_inject
@iam_intercept(TemplateEditInterceptor())
def create_template_scheme(request, project_id, template_id):
    try:
        params = json.loads(request.body)
    except Exception:
        return {"result": False, "message": "invalid json format", "code": err_code.REQUEST_PARAM_INVALID.code}

    if not isinstance(params, dict):
        return {"result": False, "message": "invalid param format", "code": err_code.REQUEST_PARAM_INVALID.code}

    if isinstance(params.get("data"), list):
        params["data"] = json.dumps(params["data"])
    serializer = TemplateSchemeSerializer(data=params)
    if not serializer.is_valid():
        return {"result": False, "message": serializer.errors, "code": err_code.REQUEST_PARAM_INVALID.code}
    validated_data = serializer.validated_data

    try:
        node_ids = json.loads(validated_data["data"])
    except (ValueError, TypeError):
        return {"result": False, "message": "data is not a valid json string",
                "code": err_code.REQUEST_PARAM_INVALID.code}
    if not isinstance(node_ids, list) or not node_ids:
        return {"result": False, "message": "data must be a non-empty list of node ids",
                "code": err_code.REQUEST_PARAM_INVALID.code}

    try:
        template = TaskTemplate.objects.get(id=template_id, project_id=request.project.id, is_deleted=False)
    except TaskTemplate.DoesNotExist:
        return {
            "result": False,
            "message": "template(%s) does not exist" % template_id,
            "code": err_code.CONTENT_NOT_EXIST.code,
        }

    try:
        pipeline_tree = template.get_pipeline_tree_by_version(None)
    except Exception as e:
        logger.exception("[API] create_template_scheme get pipeline_tree error: %s", e)
        return {
            "result": False,
            "message": "get template(%s) pipeline_tree failed: %s" % (template_id, e),
            "code": err_code.UNKNOWN_ERROR.code,
        }

    # 校验执行方案中的节点是否为流程模板 pipeline_tree 中真实存在的可选节点，防止创建出无法使用的执行方案
    message = validate_scheme_nodes(pipeline_tree, node_ids)
    if message:
        return {"result": False, "message": message, "code": err_code.REQUEST_PARAM_INVALID.code}

    unique_id = "{}-{}".format(template_id, validated_data["name"])
    if TemplateScheme.objects.filter(template_id=template.pipeline_template.id, unique_id=unique_id).exists():
        return {
            "result": False,
            "message": "scheme with unique_id(%s) already exists" % unique_id,
            "code": err_code.REQUEST_PARAM_INVALID.code,
        }

    try:
        scheme = TemplateScheme.objects.create(
            template_id=template.pipeline_template.id,
            unique_id=unique_id,
            name=validated_data["name"],
            data=json.dumps(node_ids),
        )
    except Exception as e:
        logger.exception("[API] create_template_scheme error: %s", e)
        return {"result": False, "message": "create scheme failed", "code": err_code.UNKNOWN_ERROR.code}

    return {
        "result": True,
        "data": {
            "id": scheme.id,
            "unique_id": scheme.unique_id,
            "name": scheme.name,
            "data": scheme.data,
        },
        "code": err_code.SUCCESS.code,
        "message": "success",
    }
