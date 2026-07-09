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
from copy import deepcopy

from apigw_manager.apigw.decorators import apigw_require
from blueapps.account.decorators import login_exempt
from django.views.decorators.http import require_GET
from pipeline.models import TemplateScheme

from gcloud import err_code
from gcloud.apigw.decorators import mark_request_whether_is_trust, project_inject, return_json_response
from gcloud.apigw.views.utils import logger
from gcloud.iam_auth.intercept import iam_intercept
from gcloud.iam_auth.view_interceptors.apigw import FlowViewInterceptor
from gcloud.tasktmpl3.models import TaskTemplate
from pipeline_web.preview_base import PipelineTemplateWebPreviewer


@login_exempt
@require_GET
@apigw_require
@return_json_response
@mark_request_whether_is_trust
@project_inject
@iam_intercept(FlowViewInterceptor())
def get_template_schemes(request, project_id, template_id):
    tenant_id = request.user.tenant_id
    template = TaskTemplate.objects.get(project_id=request.project.id, id=template_id, project__tenant_id=tenant_id)

    schemes = TemplateScheme.objects.filter(template__id=template.pipeline_template.id)

    # 根据前端参数决定是否返回 constants 详情
    with_constants = request.GET.get("with_constants", "false").lower() == "true"

    data = []
    if with_constants:
        # 获取模板的 pipeline_tree，用于计算可选节点
        pipeline_tree = template.get_pipeline_tree_by_version(None)
        optional_node_ids = []
        for node_id, node_data in pipeline_tree["activities"].items():
            if node_data.get("optional", False):
                optional_node_ids.append(node_id)

    for s in schemes:
        scheme_info = {
            "id": s.unique_id,
            "name": s.name,
            "data": s.data,
        }

        if with_constants:
            # 解析执行方案包含的节点ID列表（这些是执行方案中选中的节点）
            try:
                scheme_data = json.loads(s.data)
            except json.JSONDecodeError:
                logger.exception("[API] get_template_schemes invalid json format: {}".format(s.data))
                scheme_info["detail"] = {"constants": {}}
                data.append(scheme_info)
                continue

            # 计算需要排除的节点ID：可选节点中未被执行方案选中的节点
            # scheme_data 包含的是执行方案选中的节点ID
            # exclude_task_nodes_id 需要传入的是要移除的节点ID
            exclude_task_nodes_id = list(set(optional_node_ids) - set(scheme_data))
            # 外层只取一次 pipeline_tree，循环里 deepcopy 后直接调用
            # 避免每次循环重复查询数据库构建 pipeline_tree
            try:
                tree_copy = deepcopy(pipeline_tree)
                PipelineTemplateWebPreviewer.preview_pipeline_tree_exclude_task_nodes(tree_copy, exclude_task_nodes_id)
                detail = {"constants": tree_copy.get("constants", {})}
            except Exception as e:
                logger.exception("[API] get_template_schemes fail: {}".format(e))
                return {
                    "result": False,
                    "message": "get_template_schemes fail: {}".format(e),
                    "code": err_code.UNKNOWN_ERROR.code,
                }

            scheme_info["detail"] = detail

        data.append(scheme_info)

    return {"result": True, "data": data, "code": err_code.SUCCESS.code}
