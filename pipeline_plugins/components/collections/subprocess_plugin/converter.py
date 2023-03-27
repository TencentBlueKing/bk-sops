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
import copy

from django.apps import apps

from gcloud.common_template.models import CommonTemplate
from gcloud.constants import COMMON, PROJECT
from gcloud.tasktmpl3.models import TaskTemplate


class PipelineTreeSubprocessConverter:
    CONVERT_FIELDS = {
        "always_use_latest",
        "scheme_id_list",
        "template_source",
        "template_id",
        "pipeline",
    }
    REMAIN_FIELDS = {
        "id",
        "name",
        "optional",
        "outgoing",
        "stage_name",
        "labels",
        "incoming",
        "original_template_id",
        "original_template_version",
        "timeout_config",
        "auto_retry",
        "template_node_id",
    }
    DEFAULT_VALUES = {
        "error_ignorable": False,
        "auto_retry": {"enabled": False, "interval": 0, "times": 1},
        "timeout_config": {"enabled": False, "seconds": 10, "action": "forced_fail"},
        "skippable": True,
        "retryable": True,
        "type": "ServiceActivity",
        "component": {
            "code": "subprocess_plugin",
            "data": {"subprocess": {"hook": False, "need_render": False, "value": {}}},
            "version": "1.0.0",
        },
    }

    def __init__(self, pipeline_tree, constants=None):
        self.pipeline_tree = pipeline_tree
        self.constants = constants or {}

    def pre_convert(self):
        """
        在pipeline_tree转换前做一些预处理
        """
        pass

    def convert(self):
        """
        在pipeline_tree转换之后进行处理
        """
        for act_id, act in self.pipeline_tree["activities"].items():
            if act["type"] == "SubProcess":
                subprocess_converter = PipelineTreeSubprocessConverter(act["pipeline"])
                subprocess_converter.convert()
                self.pipeline_tree["activities"][act_id] = self.get_converted_subprocess(act)

                # 替换父任务变量
                if self.constants:
                    for key, constant in self.pipeline_tree["constants"]:
                        if key in self.constants:
                            constant["value"] = self.constants[key]

                # 添加原始模版id信息
                pipeline_template_id = act["template_id"]
                # 旧模版数据可能没有template_source字段
                tmpl_model_cls, candidate_tmpl_model_cls = (
                    (CommonTemplate, TaskTemplate)
                    if act.get("template_source") == COMMON
                    else (TaskTemplate, CommonTemplate)
                )
                template = (
                    tmpl_model_cls.objects.filter(pipeline_template_id=pipeline_template_id).first()
                    or candidate_tmpl_model_cls.objects.filter(pipeline_template_id=pipeline_template_id).first()
                )
                if not template:
                    raise ValueError(f"Template with pipeline_template_id: {pipeline_template_id} not found")
                subprocess_data = self.pipeline_tree["activities"][act_id]["component"]["data"]["subprocess"]["value"]
                subprocess_data["template_source"] = (
                    COMMON if isinstance(template, apps.get_model("template", "CommonTemplate")) else PROJECT
                )
                self.pipeline_tree["activities"][act_id]["original_template_id"] = str(template.id)
                self.pipeline_tree["activities"][act_id]["original_template_version"] = template.version

        for location in self.pipeline_tree["location"]:
            if location["type"] == "subflow":
                location["type"] = "tasknode"

    def get_converted_subprocess(self, original_data):
        converted_data = copy.deepcopy(self.DEFAULT_VALUES)
        convert_fields = []
        for field, value in original_data.items():
            if field in self.CONVERT_FIELDS:
                convert_fields.append(field)
            elif field in self.REMAIN_FIELDS:
                converted_data[field] = value

        component_data = converted_data["component"]["data"]["subprocess"]["value"]
        for convert_field in convert_fields:
            value = original_data[convert_field]
            if hasattr(self, f"{convert_field}_field_handler"):
                component_data[convert_field] = getattr(self, f"{convert_field}_field_handler")(value)
                continue
            component_data[convert_field] = value

        component_data["subprocess_name"] = original_data["name"]

        return converted_data
