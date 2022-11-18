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

import json
import logging

from django.http import JsonResponse

from gcloud.common_template.models import CommonTemplate
from gcloud.taskflow3.models import TaskFlowInstance, TaskTemplate
from gcloud.contrib.operate_record.models import TaskOperateRecord, TemplateOperateRecord
from gcloud.contrib.operate_record.constants import OperateSource, RecordType, INSTANCE_OBJECT_KEY
from gcloud.contrib.operate_record.utils import extract_extra_info

logger = logging.getLogger("root")

RECORD_MODEL = {
    "task": TaskOperateRecord,
    "template": TemplateOperateRecord,
    "common_template": TemplateOperateRecord,
}

OPERATE_MODEL = {
    "task": TaskFlowInstance,
    "template": TaskTemplate,
    "common_template": CommonTemplate,
}


class Record(object):
    def __init__(self, record_type, action, source, result, args, kwargs):
        self.record_type = record_type
        self.action = action
        self.source = source
        self.operate_result = result
        self.args = args
        self.kwargs = kwargs

    def __call__(self):
        is_operate_success, params = getattr(self, self.action)()
        if is_operate_success:
            RECORD_MODEL[self.record_type].objects.create(**params)

    def get_instance_obj(self, instance_id=None):
        """获取记录类型的orm对象"""
        if hasattr(self.kwargs.get("bundle", {}), "obj"):
            return self.kwargs["bundle"].obj
        if hasattr(self.operate_result, "obj"):
            return self.operate_result.obj
        if instance_id:
            return OPERATE_MODEL[self.record_type].objects.filter(pk=instance_id).only("project__id").first()

    def get_request_data_from_key(self, key):
        """获取指定值"""
        default_res, source_data = "", [self.kwargs]

        # args 中数据
        if self.args:
            if hasattr(self.args[0], "body"):
                source_data.append(json.loads(self.args[0].body))

        # response 中数据
        result_key = self.result_response.get("data")
        if isinstance(result_key, dict):
            source_data.append(result_key)

        for data in source_data:
            if data.get(key):
                return data[key]

        return default_res

    @property
    def real_action(self):
        action = self.get_request_data_from_key("action")
        return self.action if not action else action

    @property
    def operator(self):
        if hasattr(self.args[0], "user"):
            return self.args[0].user.username
        if hasattr(self.operate_result, "request"):
            return getattr(self.operate_result, "request").user.username
        if hasattr(self.kwargs.get("bundle", {}), "request"):
            return self.kwargs["bundle"].request.user.username
        return ""

    @property
    def result_response(self):
        if isinstance(self.operate_result, dict):
            return self.operate_result
        if isinstance(self.operate_result, JsonResponse):
            return json.loads(self.operate_result.content)
        return {}

    def need_save_info(self, instance_obj):
        """需要记录的信息"""
        need_record_data = {
            "instance_id": instance_obj.id,
            "project_id": -1 if self.record_type == RecordType.common_template.name else instance_obj.project.id,
            "operator": self.operator,
            "operate_source": self.source,
            "operate_type": self.real_action,
        }
        if isinstance(instance_obj, TaskFlowInstance):
            constants = instance_obj.pipeline_instance.execution_data.get("constant")
            extra_info = extract_extra_info(constants)
            need_record_data.update({"extra_info": extra_info})
        return need_record_data

    def get_data_by_bundle_or_request(self, bundle_or_request, node_id=None):
        """校验操作是否成功，及返回记录数据"""

        # 校验操作是否成功
        is_operate_success, instance_id = False, None

        if bundle_or_request == "request":
            is_operate_success = self.result_response.get("result")
            if is_operate_success:
                for key in INSTANCE_OBJECT_KEY:
                    instance_id = self.get_request_data_from_key(key)
                    if instance_id:
                        break

                if not instance_id:
                    raise KeyError("func: get_data_by_bundle_or_request, error: get instance_id failed!")

        elif bundle_or_request == "bundle":
            is_operate_success = hasattr(self.operate_result, "obj") and not self.operate_result.errors

        # 获取操作对象
        if is_operate_success:
            instance_obj = self.get_instance_obj(instance_id=instance_id)
            record_params = self.need_save_info(instance_obj)

            # 记录节点ID
            if node_id:
                record_params.update({"node_id": node_id})

            return is_operate_success, record_params
        return is_operate_success, {}

    def _bundle_or_request(self, data):
        return "request" if self.source == OperateSource.api.name else data

    # 记录action
    def create(self):

        return self.get_data_by_bundle_or_request(self._bundle_or_request("bundle"))

    def update(self):
        return self.get_data_by_bundle_or_request(self._bundle_or_request("bundle"))

    def delete(self):
        instance_obj = self.get_instance_obj()
        is_operate_success = instance_obj.is_deleted
        return is_operate_success, self.need_save_info(instance_obj)

    def task_action(self):
        return self.get_data_by_bundle_or_request(self._bundle_or_request("request"))

    def task_clone(self):
        return self.get_data_by_bundle_or_request(self._bundle_or_request("request"))

    def start(self):
        return self.get_data_by_bundle_or_request(self._bundle_or_request("request"))

    def nodes_action(self):
        node_id = self.get_request_data_from_key("node_id")
        return self.get_data_by_bundle_or_request(self._bundle_or_request("request"), node_id=node_id)

    def spec_nodes_timer_reset(self):
        node_id = self.get_request_data_from_key("node_id")
        return self.get_data_by_bundle_or_request(self._bundle_or_request("request"), node_id=node_id)
