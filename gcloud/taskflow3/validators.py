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

import ujson as json

from gcloud.utils.validate import RequestValidator, ObjectJsonBodyValidator


class StatusValidator(RequestValidator):
    def validate(self, request, *args, **kwargs):
        instance_id = request.GET.get("instance_id")
        subprocess_id = request.GET.get("subprocess_id")

        if not (instance_id or subprocess_id):
            return False, "instance_id and subprocess_id can not both be empty"

        return True, ""


class DataValidator(RequestValidator):
    def validate(self, request, *args, **kwargs):
        task_id = request.GET.get("instance_id")
        node_id = request.GET.get("node_id")

        if not task_id:
            return False, "instance_id can not be empty"

        if not node_id:
            return False, "node_id can not be empty"

        subprocess_stack = request.GET.get("subprocess_stack", "[]")

        try:
            subprocess_stack = json.loads(subprocess_stack)
        except Exception:
            return False, "subprocess_stack is not a valid json string"

        if not isinstance(subprocess_stack, list):
            return False, "subprocess_stack must be a list"

        return True, ""


class DetailValidator(RequestValidator):
    def validate(self, request, *args, **kwargs):
        task_id = request.GET.get("instance_id")
        node_id = request.GET.get("node_id")

        if not task_id:
            return False, "instance_id can not be empty"

        if not node_id:
            return False, "node_id can not be empty"

        try:
            subprocess_stack = json.loads(request.GET.get("subprocess_stack", "[]"))
        except Exception:
            return False, "subprocess_stack is not a valid json string"

        if not isinstance(subprocess_stack, list):
            return False, "subprocess_stack must be a list"

        return True, ""


class GetJobInstanceLogValidator(RequestValidator):
    def validate(self, request, *args, **kwargs):
        job_instance_id = request.GET.get("job_instance_id")

        if not job_instance_id:
            return False, "job_instance_id can not be empty"

        return True, ""


class TaskActionValidator(ObjectJsonBodyValidator):
    def validate(self, request, *args, **kwargs):
        valid, err = super().validate(request, *args, **kwargs)

        if not valid:
            return valid, err

        task_id = self.data.get("instance_id")

        if not task_id:
            return False, "instance_id can not be empty"

        return True, ""


class NodesActionValidator(ObjectJsonBodyValidator):
    def validate(self, request, *args, **kwargs):

        valid, err = super().validate(request, *args, **kwargs)

        if not valid:
            return valid, err

        if not self.data.get("instance_id"):
            return False, "instance_id can not be empty"

        if not self.data.get("node_id"):
            return False, "node_id can not be empty"

        if not isinstance(self.data.get("data", {}), dict):
            return False, "data must be a object"

        if not isinstance(self.data.get("inputs", {}), dict):
            return False, "inputs must be a object"

        return True, ""


class SpecNodesTimerResetValidator(ObjectJsonBodyValidator):
    def validate(self, request, *args, **kwargs):

        valid, err = super().validate(request, *args, **kwargs)

        if not valid:
            return valid, err

        if not self.data.get("instance_id"):
            return False, "instance_id can not be empty"

        if not self.data.get("node_id"):
            return False, "node_id can not be empty"

        if not isinstance(self.data.get("inputs", {}), dict):
            return False, "inputs must be a object"

        return True, ""


class TaskCloneValidator(ObjectJsonBodyValidator):
    def validate(self, request, *args, **kwargs):

        valid, err = super().validate(request, *args, **kwargs)

        if not valid:
            return valid, err

        if not self.data.get("instance_id"):
            return False, "instance_id can not be empty"

        return True, ""


class TaskModifyInputsValidator(ObjectJsonBodyValidator):
    def validate(self, request, *args, **kwargs):

        valid, err = super().validate(request, *args, **kwargs)

        if not valid:
            return valid, err

        if not self.data.get("instance_id"):
            return False, "instance_id can not be empty"

        if not self.data.get("constants"):
            return False, "constants can not be empty"

        if not isinstance(self.data["constants"], dict):
            return False, "constants must be a object"

        return True, ""


class TaskFuncClaimValidator(ObjectJsonBodyValidator):
    def validate(self, request, *args, **kwargs):

        valid, err = super().validate(request, *args, **kwargs)

        if not valid:
            return valid, err

        if not self.data.get("instance_id"):
            return False, "instance_id can not be empty"

        if self.data.get("constants") is None:
            return False, "constants can not be empty"

        if not isinstance(self.data["constants"], dict):
            return False, "constants must be a object"

        return True, ""


class PreviewTaskTreeValidator(ObjectJsonBodyValidator):
    def validate(self, request, *args, **kwargs):

        valid, err = super().validate(request, *args, **kwargs)

        if not valid:
            return valid, err

        if not self.data.get("template_id"):
            return False, "template_id can not be empty"

        if not isinstance(self.data.get("exclude_task_nodes_id", []), list):
            return False, "exclude_task_nodes_id must be a list"

        return True, ""


class QueryTaskCountValidator(ObjectJsonBodyValidator):
    def validate(self, request, *args, **kwargs):

        valid, err = super().validate(request, *args, **kwargs)

        if not valid:
            return valid, err

        if not isinstance(self.data.get("conditions", {}), dict):
            return False, "conditions must be a object"

        if self.data.get("group_by") not in ["category", "create_method", "flow_type", "status"]:
            return False, "group_by is invalid"

        return True, ""


class GetNodeLogValidator(RequestValidator):
    def validate(self, request, *args, **kwargs):

        if not request.GET.get("instance_id"):
            return False, "instance_id can not be empty"

        return True, ""
