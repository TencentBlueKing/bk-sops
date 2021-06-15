# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import ujson as json

from gcloud.tasktmpl3.models import TaskTemplate
from pipeline_web.parser.validator import validate_web_pipeline_tree
from pipeline_web.drawing_new.drawing import draw_pipeline
from gcloud.utils.strings import standardize_pipeline_node_name
from gcloud.utils.validate import ObjectJsonBodyValidator
from gcloud.apigw.views.utils import logger


class FastCreateTaskValidator(ObjectJsonBodyValidator):
    def validate(self, request, *args, **kwargs):
        valid, err = super().validate(request, *args, **kwargs)
        if not valid:
            return valid, err

        try:
            params = json.loads(request.body)
        except Exception:
            return False, "invalid json format"

        try:
            pipeline_tree = params["pipeline_tree"]
            standardize_pipeline_node_name(pipeline_tree)
            pipeline_tree.setdefault("gateways", {})
            pipeline_tree.setdefault("constants", {})
            pipeline_tree.setdefault("outputs", [])
            draw_pipeline(pipeline_tree)
            validate_web_pipeline_tree(pipeline_tree)
        except Exception as e:
            message = "[API] fast_create_task get invalid pipeline_tree: %s" % str(e)
            logger.warning(message)
            return False, message

        # 校验流程树中子流程是否在当前项目下
        has_common_subprocess = params.get("has_common_subprocess", False)
        templates_in_task = set()
        pipeline_tree = params["pipeline_tree"]
        for activity in pipeline_tree["activities"].values():
            if "template_id" in activity:
                templates_in_task.add(activity["template_id"])
        if not has_common_subprocess:
            project_templates = set(
                TaskTemplate.objects.filter(project_id=request.project.id).values_list("id", flat=True)
            )
            if not templates_in_task.issubset(project_templates):
                invalid_template_ids = [str(template) for template in list(templates_in_task - project_templates)]
                message = (
                    "[API] fast_create_task get invalid template_id: {}, template_id "
                    "should belong to current project.".format(",".join(invalid_template_ids))
                )
                logger.warning(message)
                return False, message

        setattr(request, "params_json", params)
        return True, ""
