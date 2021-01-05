# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import logging

from pipeline.core.data.expression import ConstantTemplate

from gcloud.tasktmpl3.models import TaskTemplate

logger = logging.getLogger("root")


def get_template_context(pipeline_template, data_type, username=""):
    try:
        template = TaskTemplate.objects.get(pipeline_template=pipeline_template)
    except TaskTemplate.DoesNotExist:
        logger.warning("TaskTemplate Does not exist: pipeline_template.id=%s" % pipeline_template.pk)
        return {}
    context = {
        "project_id": template.project.id,
        "project_name": template.project.name,
        "operator": template.pipeline_template.editor or username,
    }
    return context


def analysis_pipeline_constants_ref(pipeline_tree):

    result = {key: {"activities": [], "gateways": [], "constants": []} for key in pipeline_tree.get("constants", {})}

    def ref_counter(key):
        return result.setdefault("${%s}" % key, {"activities": [], "gateways": [], "constants": []})

    for act_id, act in pipeline_tree.get("activities", {}).items():
        if act["type"] == "SubProcess":
            subproc_consts = act.get("constants", {})
            for key, info in subproc_consts.items():
                refs = ConstantTemplate(info["value"]).get_reference()
                for r in refs:
                    ref_counter(r)["activities"].append(act_id)

        elif act["type"] == "ServiceActivity":
            act_data = act.get("component", {}).get("data", {})
            for data_item in act_data.values():
                refs = ConstantTemplate(data_item["value"]).get_reference()
                for r in refs:
                    ref_counter(r)["activities"].append(act_id)

    for gateway_id, gateway in pipeline_tree.get("gateways", {}).items():
        if gateway["type"] != "ExclusiveGateway":
            continue

        for condition in gateway.get("conditions", {}).values():
            refs = ConstantTemplate(condition["evaluate"]).get_reference()
            for r in refs:
                ref_counter(r)["gateways"].append(gateway_id)

    for key, const in pipeline_tree.get("constants", {}).items():
        refs = ConstantTemplate(const.get("value")).get_reference()
        for r in refs:
            ref_counter(r)["constants"].append(key)

    return result
