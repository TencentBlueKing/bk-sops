# -*- coding: utf-8 -*-
from django.test import TestCase
from mock import MagicMock, patch
from pipeline.component_framework.test import (
    ComponentTestCase,
    ComponentTestMixin,
    ExecuteAssertion,
    Patcher,
    ScheduleAssertion,
)

from gcloud.core.models import EngineConfig
from pipeline_plugins.components.collections.subprocess_plugin.v1_0_0 import (
    SubprocessPluginComponent,
    SubprocessPluginService,
)


class CustomPatcher:
    def __init__(self, target, new=None, side_effect=None, return_value=None):
        self.target = target
        self.new = new
        self.side_effect = side_effect
        self.return_value = return_value

    def mock_patcher(self):
        if self.new:
            return patch(target=self.target, new=self.new)
        return patch(target=self.target, new=MagicMock(return_value=self.return_value, side_effect=self.side_effect))


class MockTaskFlowInstance:
    DoesNotExist = Exception

    def __init__(self, id=1, engine_ver=EngineConfig.ENGINE_VER_V2):
        self.id = id
        self.engine_ver = engine_ver
        self.pipeline_tree = {"constants": {}}
        self.category = "category"
        self.template_id = "template_id"
        self.template_source = "project"
        self.create_method = "create_method"
        self.create_info = "create_info"
        self.flow_type = "flow_type"
        self.current_flow = "current_flow"
        self.recorded_executor_proxy = False
        self.executor = "executor"
        self.project_id = 1
        self.pipeline_instance = MagicMock()
        self.pipeline_instance.instance_id = "subprocess_pipeline_id"
        self.pipeline_instance.execution_data = {"constants": {}}
        self.url = "http://url"
        self.name = "task_name"

    def task_action(self, action, executor):
        pass


VALID_INPUTS = {
    "subprocess": {"subprocess_name": "sub", "pipeline": {"constants": {}}, "template_id": "tpl_id"},
    "project_id": 1,
}

PARENT_DATA = {"task_id": 1, "project_id": 1}

EXECUTE_SUCCESS_ASSERTION = ExecuteAssertion(
    success=True, outputs={"task_id": 100, "task_url": "http://url", "task_name": "task_name"}
)

EXECUTE_OUTPUTS = {"task_id": 100, "task_url": "http://url", "task_name": "task_name"}


class TestSubprocessPluginService(SubprocessPluginService):
    version = "1.0.0"

    @property
    def top_pipeline_id(self):
        # ComponentTestCase injects root_pipeline_id, we map it to top_pipeline_id
        return getattr(self, "root_pipeline_id", "default_id")


def SUBPROCESS_EXECUTE_FAIL_PARENT_NOT_FOUND_CASE():
    mock_tf_instance_cls = MagicMock()
    mock_tf_instance_cls.DoesNotExist = Exception
    mock_tf_instance_cls.objects.get.side_effect = Exception("parent task 999 not found")

    return ComponentTestCase(
        name="SubprocessPlugin execute fail parent not found",
        inputs=VALID_INPUTS,
        parent_data={"task_id": 999},
        execute_assertion=ExecuteAssertion(success=False, outputs={"ex_data": "parent task 999 not found"}),
        schedule_assertion=None,
        patchers=[
            CustomPatcher(
                target="pipeline_plugins.components.collections.subprocess_plugin.v1_0_0.TaskFlowInstance",
                new=mock_tf_instance_cls,
            ),
        ],
    )


def SUBPROCESS_SCHEDULE_SUCCESS_CASE():
    subprocess_task = MockTaskFlowInstance(id=100)
    mock_runtime = MagicMock()
    mock_runtime.get_context_key_references.return_value = set()
    mock_runtime.get_context_values.return_value = []
    mock_runtime.get_data_inputs.return_value = {}
    mock_runtime.get_execution_data_outputs.return_value = {"key1": "value1"}
    mock_runtime.get_data_outputs.return_value = {"key1": "default"}

    parent_task = MockTaskFlowInstance()

    expected_outputs = EXECUTE_OUTPUTS.copy()
    expected_outputs.update({"key1": "value1"})

    return ComponentTestCase(
        name="SubprocessPlugin schedule success",
        inputs=VALID_INPUTS,
        parent_data=PARENT_DATA,
        execute_assertion=EXECUTE_SUCCESS_ASSERTION,
        schedule_assertion=ScheduleAssertion(
            success=True,
            schedule_finished=True,
            callback_data={"task_success": True, "task_id": 100},
            outputs=expected_outputs,
        ),
        patchers=[
            Patcher(
                target="pipeline_plugins.components.collections.subprocess_plugin.v1_0_0.TaskFlowInstance.objects.get",
                side_effect=[parent_task, subprocess_task],
            ),
            Patcher(
                target="pipeline_plugins.components.collections.subprocess_plugin.v1_0_0."
                "TaskFlowInstance.objects.create",
                return_value=MockTaskFlowInstance(id=100),
            ),
            Patcher(
                target="pipeline_plugins.components.collections.subprocess_plugin.v1_0_0."
                "TaskFlowInstance.objects.create_pipeline_instance",
                return_value=MagicMock(),
            ),
            Patcher(
                target="pipeline_plugins.components.collections.subprocess_plugin.v1_0_0."
                "TaskFlowRelation.objects.get",
                return_value=MagicMock(root_task_id=1),
            ),
            Patcher(
                target="pipeline_plugins.components.collections.subprocess_plugin.v1_0_0."
                "TaskFlowRelation.objects.create",
                return_value=None,
            ),
            Patcher(
                target="pipeline_plugins.components.collections.subprocess_plugin.v1_0_0."
                "TaskCallBackRecord.objects.create",
                return_value=None,
            ),
            Patcher(
                target="pipeline_plugins.components.collections.subprocess_plugin.v1_0_0.AutoRetryNodeStrategyCreator",
                return_value=MagicMock(),
            ),
            Patcher(
                target="pipeline_plugins.components.collections.subprocess_plugin.v1_0_0."
                "TimeoutNodeConfig.objects.batch_create_node_timeout_config",
                return_value=None,
            ),
            Patcher(
                target="pipeline_plugins.components.collections.subprocess_plugin.v1_0_0.operate_record_signal.send",
                return_value=None,
            ),
            Patcher(
                target="pipeline_plugins.components.collections.subprocess_plugin.v1_0_0.Project.objects.filter",
                return_value=MagicMock(first=MagicMock(return_value=MagicMock(time_zone="Asia/Shanghai"))),
            ),
            Patcher(
                target="pipeline_plugins.components.collections.subprocess_plugin.v1_0_0."
                "PipelineTemplate.objects.filter",
                return_value=MagicMock(first=MagicMock(return_value=MagicMock(name="tpl_name"))),
            ),
            Patcher(
                target="pipeline_plugins.components.collections.subprocess_plugin.v1_0_0.CommonTemplate",
                return_value=MagicMock(),
            ),
            Patcher(
                target="pipeline_plugins.components.collections.subprocess_plugin.v1_0_0.TaskTemplate",
                return_value=MagicMock(),
            ),
            CustomPatcher(
                target="pipeline_plugins.components.collections.subprocess_plugin.v1_0_0."
                "SubprocessPluginService.runtime",
                new=mock_runtime,
            ),
        ],
    )


def SUBPROCESS_SCHEDULE_FAIL_CASE():
    parent_task = MockTaskFlowInstance()
    mock_runtime = MagicMock()
    mock_runtime.get_context_key_references.return_value = set()
    mock_runtime.get_context_values.return_value = []
    mock_runtime.get_data_inputs.return_value = {}

    expected_outputs = EXECUTE_OUTPUTS.copy()
    expected_outputs.update({"ex_data": "failed"})

    return ComponentTestCase(
        name="SubprocessPlugin schedule fail",
        inputs=VALID_INPUTS,
        parent_data=PARENT_DATA,
        execute_assertion=EXECUTE_SUCCESS_ASSERTION,
        schedule_assertion=ScheduleAssertion(
            success=False,
            schedule_finished=True,
            callback_data={"task_success": False, "ex_data": "failed"},
            outputs=expected_outputs,
        ),
        patchers=[
            Patcher(
                target="pipeline_plugins.components.collections.subprocess_plugin.v1_0_0.TaskFlowInstance.objects.get",
                return_value=parent_task,
            ),
            Patcher(
                target="pipeline_plugins.components.collections.subprocess_plugin.v1_0_0."
                "TaskFlowInstance.objects.create",
                return_value=MockTaskFlowInstance(id=100),
            ),
            Patcher(
                target="pipeline_plugins.components.collections.subprocess_plugin.v1_0_0."
                "TaskFlowInstance.objects.create_pipeline_instance",
                return_value=MagicMock(),
            ),
            Patcher(
                target="pipeline_plugins.components.collections.subprocess_plugin.v1_0_0."
                "TaskFlowRelation.objects.get",
                return_value=MagicMock(root_task_id=1),
            ),
            Patcher(
                target="pipeline_plugins.components.collections.subprocess_plugin.v1_0_0."
                "TaskFlowRelation.objects.create",
                return_value=None,
            ),
            Patcher(
                target="pipeline_plugins.components.collections.subprocess_plugin.v1_0_0."
                "TaskCallBackRecord.objects.create",
                return_value=None,
            ),
            Patcher(
                target="pipeline_plugins.components.collections.subprocess_plugin.v1_0_0.AutoRetryNodeStrategyCreator",
                return_value=MagicMock(),
            ),
            Patcher(
                target="pipeline_plugins.components.collections.subprocess_plugin.v1_0_0."
                "TimeoutNodeConfig.objects.batch_create_node_timeout_config",
                return_value=None,
            ),
            Patcher(
                target="pipeline_plugins.components.collections.subprocess_plugin.v1_0_0.operate_record_signal.send",
                return_value=None,
            ),
            Patcher(
                target="pipeline_plugins.components.collections.subprocess_plugin.v1_0_0.Project.objects.filter",
                return_value=MagicMock(first=MagicMock(return_value=MagicMock(time_zone="Asia/Shanghai"))),
            ),
            Patcher(
                target="pipeline_plugins.components.collections.subprocess_plugin.v1_0_0."
                "PipelineTemplate.objects.filter",
                return_value=MagicMock(first=MagicMock(return_value=MagicMock(name="tpl_name"))),
            ),
            Patcher(
                target="pipeline_plugins.components.collections.subprocess_plugin.v1_0_0.CommonTemplate",
                return_value=MagicMock(),
            ),
            Patcher(
                target="pipeline_plugins.components.collections.subprocess_plugin.v1_0_0.TaskTemplate",
                return_value=MagicMock(),
            ),
            CustomPatcher(
                target="pipeline_plugins.components.collections.subprocess_plugin.v1_0_0."
                "SubprocessPluginService.runtime",
                new=mock_runtime,
            ),
        ],
    )


def SUBPROCESS_SCHEDULE_TASK_NOT_FOUND_CASE():
    mock_tf_instance_cls = MagicMock()
    mock_tf_instance_cls.DoesNotExist = Exception
    mock_tf_instance_cls.objects.get.side_effect = [MockTaskFlowInstance(), Exception("DoesNotExist")]
    mock_tf_instance_cls.objects.create.return_value = MockTaskFlowInstance(id=100)
    mock_tf_instance_cls.objects.create_pipeline_instance.return_value = MagicMock()

    mock_runtime = MagicMock()
    mock_runtime.get_context_key_references.return_value = set()
    mock_runtime.get_context_values.return_value = []
    mock_runtime.get_data_inputs.return_value = {}

    expected_outputs = EXECUTE_OUTPUTS.copy()
    expected_outputs.update({"ex_data": "子任务[100]不存在"})

    return ComponentTestCase(
        name="SubprocessPlugin schedule task not found",
        inputs=VALID_INPUTS,
        parent_data=PARENT_DATA,
        execute_assertion=EXECUTE_SUCCESS_ASSERTION,
        schedule_assertion=ScheduleAssertion(
            success=False,
            schedule_finished=True,
            callback_data={"task_success": True, "task_id": 999},
            outputs=expected_outputs,
        ),
        patchers=[
            CustomPatcher(
                target="pipeline_plugins.components.collections.subprocess_plugin.v1_0_0.TaskFlowInstance",
                new=mock_tf_instance_cls,
            ),
            Patcher(
                target="pipeline_plugins.components.collections.subprocess_plugin.v1_0_0.TaskFlowRelation.objects.get",
                return_value=MagicMock(root_task_id=1),
            ),
            Patcher(
                target="pipeline_plugins.components.collections.subprocess_plugin.v1_0_0."
                "TaskFlowRelation.objects.create",
                return_value=None,
            ),
            Patcher(
                target="pipeline_plugins.components.collections.subprocess_plugin.v1_0_0."
                "TaskCallBackRecord.objects.create",
                return_value=None,
            ),
            Patcher(
                target="pipeline_plugins.components.collections.subprocess_plugin.v1_0_0.AutoRetryNodeStrategyCreator",
                return_value=MagicMock(),
            ),
            Patcher(
                target="pipeline_plugins.components.collections.subprocess_plugin.v1_0_0."
                "TimeoutNodeConfig.objects.batch_create_node_timeout_config",
                return_value=None,
            ),
            Patcher(
                target="pipeline_plugins.components.collections.subprocess_plugin.v1_0_0.operate_record_signal.send",
                return_value=None,
            ),
            Patcher(
                target="pipeline_plugins.components.collections.subprocess_plugin.v1_0_0.Project.objects.filter",
                return_value=MagicMock(first=MagicMock(return_value=MagicMock(time_zone="Asia/Shanghai"))),
            ),
            Patcher(
                target="pipeline_plugins.components.collections.subprocess_plugin.v1_0_0."
                "PipelineTemplate.objects.filter",
                return_value=MagicMock(first=MagicMock(return_value=MagicMock(name="tpl_name"))),
            ),
            Patcher(
                target="pipeline_plugins.components.collections.subprocess_plugin.v1_0_0.CommonTemplate",
                return_value=MagicMock(),
            ),
            Patcher(
                target="pipeline_plugins.components.collections.subprocess_plugin.v1_0_0.TaskTemplate",
                return_value=MagicMock(),
            ),
            CustomPatcher(
                target="pipeline_plugins.components.collections.subprocess_plugin.v1_0_0."
                "SubprocessPluginService.runtime",
                new=mock_runtime,
            ),
        ],
    )


class SubprocessPluginComponentTest(TestCase, ComponentTestMixin):
    def setUp(self):
        self.original_service = SubprocessPluginComponent.bound_service
        SubprocessPluginComponent.bound_service = TestSubprocessPluginService

    def tearDown(self):
        SubprocessPluginComponent.bound_service = self.original_service

    def component_cls(self):
        return SubprocessPluginComponent

    def cases(self):
        return [
            SUBPROCESS_EXECUTE_FAIL_PARENT_NOT_FOUND_CASE(),
            SUBPROCESS_SCHEDULE_SUCCESS_CASE(),
            SUBPROCESS_SCHEDULE_FAIL_CASE(),
            SUBPROCESS_SCHEDULE_TASK_NOT_FOUND_CASE(),
        ]
