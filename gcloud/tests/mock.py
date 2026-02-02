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

from __future__ import absolute_import

from datetime import datetime

import mock  # noqa
import ujson as json
from django.utils.timezone import now
from mock import MagicMock, call, patch  # noqa

from gcloud.tests.test_data import TEST_PIPELINE_TREE


class MockRequest(object):
    def __init__(self, method, data, username="a_user"):
        self.method = method
        setattr(self, method, data)
        self.user = MagicMock(username=username)


class MockJsonBodyRequest(object):
    def __init__(self, method, data, username="a_user"):
        self.method = method
        self.body = json.dumps(data)
        self.user = MagicMock(username=username)


class MockJsonResponse(object):
    def __call__(self, dct):
        return dct


class MockBusiness(object):
    def __init__(self, **kwargs):
        self.cc_id = kwargs.get("cc_id", "cc_id")
        self.cc_name = kwargs.get("cc_name", "cc_name")
        self.time_zone = kwargs.get("time_zone", "time_zone")


class MockProject(object):
    def __init__(self, **kwargs):
        self.id = kwargs.get("project_id", 1)
        self.name = kwargs.get("name", "name")
        self.bk_biz_id = kwargs.get("bk_biz_id", "bk_biz_id")
        self.from_cmdb = kwargs.get("from_cmdb", False)
        self.time_zone = kwargs.get("time_zone", "time_zone")


class MockPipelineTemplate(object):
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", "id")
        self.name = kwargs.get("name", "name")
        self.creator = kwargs.get("creator", "creator")
        self.edit_time = kwargs.get("edit_time", now())
        self.editor = kwargs.get("editor", "editor")
        self.create_time = kwargs.get("create_time", now())
        self.data = kwargs.get("data", TEST_PIPELINE_TREE)
        self.description = kwargs.get("description", "description")


class MockBaseTemplate(object):
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", "id")
        self.name = kwargs.get("name", "name")
        self.category = kwargs.get("category", "category")
        self.pipeline_template = kwargs.get("pipeline_template", MockPipelineTemplate())
        self.pipeline_tree = kwargs.get(
            "pipeline_tree", {"line": "line", "location": "location", "activities": {}, "constants": {}}
        )
        self.get_pipeline_tree_by_version = MagicMock(return_value=self.pipeline_tree)


class MockTaskTemplate(MockBaseTemplate):
    def __init__(self, **kwargs):
        self.project = kwargs.get("project", MockProject())
        return super().__init__(**kwargs)


class MockCommonTemplate(MockBaseTemplate):
    pass


class MockTaskFlowInstance(object):
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", "id")
        self.task_action = MagicMock(return_value=kwargs.get("task_action_return", None))
        self.get_status = MagicMock(
            **{"return_value": kwargs.get("get_status_return"), "side_effect": kwargs.get("get_status_raise")}
        )
        self.format_pipeline_status = MagicMock(
            **{
                "return_value": kwargs.get("format_pipeline_status_return"),
                "side_effect": kwargs.get("format_pipeline_status_raise"),
            }
        )
        self.url = kwargs.get("url", "url")
        self.pipeline_tree = kwargs.get("pipeline_tree", "pipeline_tree")
        self.callback = MagicMock(return_value=kwargs.get("callback_return", {"result": True, "message": "success"}))
        self.get_task_detail = MagicMock(return_value=kwargs.get("get_task_detail_return", "task_detail"))
        self.get_node_detail = MagicMock(
            return_value=kwargs.get("get_node_detail_return", {"result": True, "data": "data"})
        )
        self.name = kwargs.get("name", "name")
        self.create_time = now()
        self.start_time = now()
        self.finish_time = now()
        self.flow_type = kwargs.get("flow_type", "flow_type")
        self.current_flow = kwargs.get("current_flow", "current_flow")
        self.is_deleted = True
        self.engine_ver = kwargs.get("engine_ver", 1)
        self.pipeline_instance = kwargs.get("pipeline_instance", MagicMock())
        self.template_id = kwargs.get("template_id", 1)
        self.project = kwargs.get("project", MockProject())
        self.create_method = kwargs.get("create_method", "create_method")
        self.pipeline_instance__id = 1
        self.executor = kwargs.get("executor", "executor")
        self.executor_proxy = kwargs.get("executor_proxy", "executor_proxy")
        self.recorded_executor_proxy = kwargs.get("recorded_executor_proxy", None)
        self.record_and_get_executor_proxy = MagicMock(side_effect=self._record_and_get_executor_proxy_side_effect)
        self.save = MagicMock()

    def _record_and_get_executor_proxy_side_effect(self, value):
        return self.recorded_executor_proxy or value


class MockPeriodicTask(object):
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", "id")
        self.name = kwargs.get("name", "name")
        self.template_id = kwargs.get("template_id", "template_id")
        self.template_source = kwargs.get("template_source", "project")
        self.creator = kwargs.get("creator", "creator")
        self.cron = kwargs.get("cron", "cron")
        self.enabled = kwargs.get("enabled", False)
        self.last_run_at = kwargs.get("last_run_at", now())
        self.total_run_count = kwargs.get("total_run_count", 0)
        self.form = kwargs.get("form", "form")
        self.pipeline_tree = kwargs.get("pipeline_tre", "pipeline_tree")
        self.set_enabled = MagicMock()
        self.modify_cron = MagicMock(**{"side_effect": kwargs.get("modify_cron_raise")})
        self.modify_constants = MagicMock(
            **{
                "return_value": kwargs.get("modify_constants_return"),
                "side_effect": kwargs.get("modify_constants_raise"),
            }
        )
        self.editor = kwargs.get("editor", "editor")
        self.edit_time = kwargs.get("edit_time", now())
        self.template_version = kwargs.get("template_version", 1)
        self.template = kwargs.get("template", MockPipelineTemplate())
        self.template.version = kwargs.get("version", 1)


class MockPipelinePeriodicTaskHistory(object):
    def __init__(self, **kwargs):
        self.start_success = kwargs.get("start_success", True)
        self.periodic_task = kwargs.get("periodic_task", MagicMock())
        self.pipeline_instance = kwargs.get("pipeline_instance", MagicMock())
        self.ex_data = kwargs.get("ex_data", "ex_data")
        self.start_at = kwargs.get("start_at", "start_at")


class MockQuerySet(object):
    def __init__(self, get_result=None, get_raise=None, filter_result=None, exist_return=True):
        self.get = MagicMock(return_value=get_result) if get_result else MagicMock(side_effect=get_raise)
        self.filter = MagicMock(return_value=filter_result)
        self.exist = MagicMock(return_value=exist_return)
        self.delete = MagicMock(return_value=None)


class MockCache(object):
    def __init__(self, get_return):
        self.get_return = get_return

    def get(self, key):
        return self.get_return

    def set(self, *args, **kwargs):
        return


class MockSyncPackageSource(object):
    def __init__(self, id, type):
        self.id = id
        self.type = MagicMock(return_value=type)


class MockComponentModel(object):
    def __init__(self, code):
        self.code = code
        self.version = "version"


class MockComponent(object):
    def __init__(self, inputs, outputs, desc, code, name, group_name, version="version", form="form"):
        self.inputs = inputs
        self.outputs = outputs
        self.desc = desc
        self.code = code
        self.name = name
        self.group_name = group_name
        self.version = version
        self.form = form

    def inputs_format(self):
        return self.inputs

    def outputs_format(self):
        return self.outputs


class MockJwtClientAttr(object):
    def __init__(self, kwargs):
        self.kwargs = kwargs

    def __getattr__(self, item):
        return self.kwargs[item]


class MockJwtClient(object):
    def __init__(self, kwargs):
        self.app = MockJwtClientAttr(kwargs)
        self.user = MockJwtClientAttr(kwargs)

    @property
    def is_valid(self):
        return True


class MockTaskOperationTimesConfig(object):
    def __init__(self, kwargs):
        self.kwargs = kwargs

    def __getattr__(self, item):
        return self.kwargs[item]


class MockTaskCommandDispatcher(object):
    def __init__(self, **kwargs):
        self.engine_ver = kwargs.get("engine_ver", 1)
        self.taskflow_id = kwargs.get("taskflow_id", 1)
        self.pipeline_instance = kwargs.get("pipeline_instance", None)
        self.project_id = kwargs.get("project_id", 1)
        self.queue = kwargs.get("queue", "")


class MockPipelineInstance(object):
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", 1)
        self.instance_id = kwargs.get("instance_id", "instance_id")
        self.template = kwargs.get("template", MockPipelineTemplate())
        self.name = kwargs.get("name", "name")
        self.creator = kwargs.get("creator", "creator")
        self.create_time = kwargs.get("create_time", "create_time")
        self.executor = kwargs.get("executor", "executor")
        self.start_time = kwargs.get("start_time", datetime.now())
        self.finish_time = kwargs.get("finish_time", datetime.now())
        self.description = kwargs.get("description", "description")
        self.is_started = kwargs.get("is_started", True)
        self.is_finished = kwargs.get("is_finished", True)
        self.is_revoked = kwargs.get("is_revoked", False)
        self.is_deleted = kwargs.get("is_deleted", False)
        self.is_expired = kwargs.get("is_expired", False)
        self.execution_data = kwargs.get("execution_data", "")


class MockTemplateInPipeline(object):
    def __init__(self, **kwargs):
        self.id = kwargs.get("id", 1)
        self.atom_total = kwargs.get("atom_total", 0)
        self.subprocess_total = kwargs.get("subprocess_total", 0)
        self.gateways_total = kwargs.get("gateways_total", 0)
