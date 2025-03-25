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
import logging
from copy import deepcopy

from gcloud.common_template.models import CommonTemplate
from gcloud.constants import PROJECT
from gcloud.tasktmpl3.models import TaskTemplate
from pipeline_web.preview_base import PipelineTemplateWebPreviewer

logger = logging.getLogger("root")


def preview_template_tree(project_id, template_source, template_id, version, exclude_task_nodes_id, tenant_id):
    if template_source == PROJECT:
        template = TaskTemplate.objects.get(pk=template_id, is_deleted=False, project_id=project_id)
    else:
        template = CommonTemplate.objects.get(pk=template_id, is_deleted=False, tenant_id=tenant_id)
    pipeline_tree = template.get_pipeline_tree_by_version(version)
    template_constants = deepcopy(pipeline_tree["constants"])
    PipelineTemplateWebPreviewer.preview_pipeline_tree_exclude_task_nodes(pipeline_tree, exclude_task_nodes_id)

    constants_not_referred = {
        key: value for key, value in list(template_constants.items()) if key not in pipeline_tree["constants"]
    }

    return {"pipeline_tree": pipeline_tree, "constants_not_referred": constants_not_referred}


def preview_template_tree_with_schemes(template, version, scheme_id_list):
    version = version or template.version

    pipeline_tree = template.get_pipeline_tree_by_version(version)
    template_constants = deepcopy(pipeline_tree["constants"])

    exclude_task_nodes_id = PipelineTemplateWebPreviewer.get_template_exclude_task_nodes_with_schemes(
        pipeline_tree, scheme_id_list
    )

    PipelineTemplateWebPreviewer.preview_pipeline_tree_exclude_task_nodes(pipeline_tree, exclude_task_nodes_id)

    constants_not_referred = {}
    custom_constants = {}
    for key, value in template_constants.items():
        if value["show_type"] == "show" and key not in pipeline_tree["constants"]:
            if value["source_type"] == "custom":
                custom_constants[key] = value

            constants_not_referred[key] = value

    # 添加outputs返回
    template_outputs = template.get_outputs(version)
    outputs = {}
    for key, value in template_outputs.items():
        # 如果输出变量来源于节点勾选，且来源的节点是执行方案删除节点的子集，则不展示该输出变量
        if value["source_type"] in ["component_outputs", "component_inputs"] and set(
            value["source_info"].keys()
        ).issubset(set(exclude_task_nodes_id)):
            continue

        outputs[key] = value

    return {
        "pipeline_tree": pipeline_tree,
        "custom_constants": custom_constants,
        "constants_not_referred": constants_not_referred,
        "outputs": outputs,
        "version": version,
    }
