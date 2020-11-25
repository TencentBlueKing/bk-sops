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

from django.test import TestCase

from pipeline.engine import states

from gcloud.taskflow3.models import TaskFlowInstance

from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa


class IsManualInterventionRequiredTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pipeline_instance_descriptor = TaskFlowInstance.pipeline_instance
        TaskFlowInstance.pipeline_instance = None

    @classmethod
    def tearDownClass(cls):
        TaskFlowInstance.pipeline_instance = cls.pipeline_instance_descriptor

    def _new_taskflow(self):
        taskflow = TaskFlowInstance()
        setattr(taskflow, "pipeline_instance", MagicMock())
        return taskflow

    def test_state_is_none(self):
        taskflow = self._new_taskflow()
        with patch(TASKFLOW_MODEL_PIPELINE_API_GET_STATES_TREE, MagicMock(return_value=None)):
            self.assertFalse(taskflow.is_manual_intervention_required)

    def test_root_state_in_exempts_states(self):
        for state in [states.CREATED, states.FINISHED, states.REVOKED]:
            taskflow = self._new_taskflow()
            with patch(TASKFLOW_MODEL_PIPELINE_API_GET_STATES_TREE, MagicMock(return_value={"state": state})):
                self.assertFalse(taskflow.is_manual_intervention_required)

    def test_task_is_not_started(self):
        taskflow = self._new_taskflow()
        taskflow.pipeline_instance.is_started = False
        self.assertFalse(taskflow.is_manual_intervention_required)

    def test_1_layer_nodes_has_intervention_states(self):
        taskflow = self._new_taskflow()
        state = {
            "id": "0",
            "state": states.BLOCKED,
            "children": {
                "1": {"id": "1", "state": states.RUNNING, "children": {}},
                "2": {"id": "2", "state": states.FAILED, "children": {}},
            },
        }
        with patch(TASKFLOW_MODEL_PIPELINE_API_GET_STATES_TREE, MagicMock(return_value=state)):
            self.assertTrue(taskflow.is_manual_intervention_required)

    def test_2_layer_nodes_has_intervention_states(self):
        taskflow = self._new_taskflow()
        state = {
            "id": "0",
            "state": states.BLOCKED,
            "children": {
                "1": {"id": "1", "state": states.RUNNING, "children": {}},
                "2": {
                    "id": "2",
                    "state": states.RUNNING,
                    "children": {"3": {"id": "3", "state": states.SUSPENDED, "children": {}}},
                },
            },
        }
        with patch(TASKFLOW_MODEL_PIPELINE_API_GET_STATES_TREE, MagicMock(return_value=state)):
            self.assertTrue(taskflow.is_manual_intervention_required)

    def test_3_layer_nodes_without_intervention_states(self):
        taskflow = self._new_taskflow()
        state = {
            "id": "0",
            "state": states.BLOCKED,
            "children": {
                "1": {"id": "1", "state": states.RUNNING, "children": {}},
                "2": {
                    "id": "2",
                    "state": states.RUNNING,
                    "children": {
                        "3": {
                            "id": "3",
                            "state": states.RUNNING,
                            "children": {"4": {"id": "4", "state": states.RUNNING, "children": {}}},
                        }
                    },
                },
            },
        }
        with patch(TASKFLOW_MODEL_PIPELINE_API_GET_STATES_TREE, MagicMock(return_value=state)):
            self.assertFalse(taskflow.is_manual_intervention_required)

    def test_4_layer_nodes_has_intervention_states(self):
        taskflow = self._new_taskflow()
        state = {
            "id": "0",
            "state": states.BLOCKED,
            "children": {
                "1": {"id": "1", "state": states.RUNNING, "children": {}},
                "2": {
                    "id": "2",
                    "state": states.RUNNING,
                    "children": {
                        "3": {
                            "id": "3",
                            "state": states.SUSPENDED,
                            "children": {"4": {"id": "4", "state": states.RUNNING, "children": {}}},
                        }
                    },
                },
            },
        }
        with patch(TASKFLOW_MODEL_PIPELINE_API_GET_STATES_TREE, MagicMock(return_value=state)):
            self.assertTrue(taskflow.is_manual_intervention_required)

    def test_without_running_nodes(self):
        taskflow = self._new_taskflow()
        state = {
            "id": "0",
            "state": states.REVOKED,
            "children": {
                "1": {"id": "1", "state": states.FINISHED, "children": {}},
                "2": {
                    "id": "2",
                    "state": states.FINISHED,
                    "children": {
                        "3": {
                            "id": "3",
                            "state": states.FINISHED,
                            "children": {"4": {"id": "4", "state": states.FINISHED, "children": {}}},
                        }
                    },
                },
            },
        }
        with patch(TASKFLOW_MODEL_PIPELINE_API_GET_STATES_TREE, MagicMock(return_value=state)):
            self.assertFalse(taskflow.is_manual_intervention_required)

    def test_without_running_intervention_required_nodes(self):
        taskflow = self._new_taskflow()
        taskflow.pipeline_tree
        taskflow.pipeline_instance.execution_data = {
            "activities": {
                "1": {"id": "1", "type": "ServiceActivity", "component": {"code": "sleep_timer"}},
                "2": {"id": "2", "type": "ServiceActivity", "component": {"code": "another_node"}},
            }
        }
        state = {
            "id": "0",
            "state": states.RUNNING,
            "children": {
                "1": {"id": "1", "state": states.RUNNING, "children": {}},
                "2": {"id": "2", "state": states.RUNNING, "children": {}},
            },
        }
        with patch(TASKFLOW_MODEL_PIPELINE_API_GET_STATES_TREE, MagicMock(return_value=state)):
            self.assertFalse(taskflow.is_manual_intervention_required)

    def test_has_running_intervention_required_nodes(self):
        taskflow = self._new_taskflow()
        taskflow.pipeline_tree
        taskflow.pipeline_instance.execution_data = {
            "activities": {
                "1": {"id": "1", "type": "ServiceActivity", "component": {"code": "sleep_timer"}},
                "2": {"id": "2", "type": "ServiceActivity", "component": {"code": "pause_node"}},
            }
        }
        state = {
            "id": "0",
            "state": states.RUNNING,
            "children": {
                "1": {"id": "1", "state": states.RUNNING, "children": {}},
                "2": {"id": "2", "state": states.RUNNING, "children": {}},
            },
        }
        with patch(TASKFLOW_MODEL_PIPELINE_API_GET_STATES_TREE, MagicMock(return_value=state)):
            self.assertTrue(taskflow.is_manual_intervention_required)

    def test_has_deep_running_intervention_required_nodes(self):
        taskflow = self._new_taskflow()
        taskflow.pipeline_tree
        taskflow.pipeline_instance.execution_data = {
            "activities": {
                "1": {"id": "1", "type": "ServiceActivity", "component": {"code": "sleep_timer"}},
                "2": {
                    "id": "2",
                    "type": "SubProcess",
                    "pipeline": {
                        "activities": {
                            "3": {
                                "id": "3",
                                "type": "SubProcess",
                                "pipeline": {
                                    "activities": {
                                        "4": {"id": "4", "type": "ServiceActivity", "component": {"code": "pause_node"}}
                                    }
                                },
                            }
                        }
                    },
                },
            }
        }
        state = {
            "id": "0",
            "state": states.RUNNING,
            "children": {
                "1": {"id": "1", "state": states.RUNNING, "children": {}},
                "2": {
                    "id": "2",
                    "state": states.RUNNING,
                    "children": {
                        "3": {
                            "id": "3",
                            "state": states.RUNNING,
                            "children": {"4": {"id": "4", "state": states.RUNNING, "children": {}}},
                        }
                    },
                },
            },
        }
        with patch(TASKFLOW_MODEL_PIPELINE_API_GET_STATES_TREE, MagicMock(return_value=state)):
            self.assertTrue(taskflow.is_manual_intervention_required)
