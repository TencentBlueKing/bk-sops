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

from django.test import TestCase

from pipeline.engine import states
from pipeline.engine.models import NodeRelationship, Status
from pipeline.engine.utils import ActionResult
from pipeline.models import PipelineInstance, PipelineTemplate
from pipeline.service import task_service
from pipeline.tests.mock import *  # noqa
from pipeline.tests.mock_settings import *  # noqa


class TestPipelineInstance(TestCase):
    def setUp(self):
        self.data = {
            "activities": {
                "node8fe2bb234d29860981a2bc7e6077": {
                    "retryable": True,
                    "component": {"code": "sleep_timer", "data": {"bk_timing": {"hook": False, "value": "3"}}},
                    "error_ignorable": False,
                    "id": "node8fe2bb234d29860981a2bc7e6077",
                    "incoming": "line67b0e8cc895b1b9f9e0413dc50d1",
                    "isSkipped": True,
                    "loop": None,
                    "name": "\u5b9a\u65f6",
                    "optional": False,
                    "outgoing": "line73943da9f6f17601a40dc46bd229",
                    "stage_name": "\u6b65\u9aa41",
                    "type": "ServiceActivity",
                }
            },
            "constants": {
                "${ip}": {
                    "custom_type": "input",
                    "desc": "",
                    "index": 0,
                    "key": "${ip}",
                    "name": "ip",
                    "show_type": "show",
                    "source_info": {},
                    "source_tag": "",
                    "source_type": "custom",
                    "validation": "^.+$",
                    "validator": [],
                    "value": "",
                }
            },
            "end_event": {
                "id": "nodeade2061fe6e69dc5b64a588480a7",
                "incoming": "line73943da9f6f17601a40dc46bd229",
                "name": "",
                "outgoing": "",
                "type": "EmptyEndEvent",
            },
            "flows": {
                "line67b0e8cc895b1b9f9e0413dc50d1": {
                    "id": "line67b0e8cc895b1b9f9e0413dc50d1",
                    "is_default": False,
                    "source": "nodedee24d10226c975f4d2c659cc29d",
                    "target": "node8fe2bb234d29860981a2bc7e6077",
                },
                "line73943da9f6f17601a40dc46bd229": {
                    "id": "line73943da9f6f17601a40dc46bd229",
                    "is_default": False,
                    "source": "node8fe2bb234d29860981a2bc7e6077",
                    "target": "nodeade2061fe6e69dc5b64a588480a7",
                },
            },
            "gateways": {},
            "outputs": [],
            "start_event": {
                "id": "nodedee24d10226c975f4d2c659cc29d",
                "incoming": "",
                "name": "",
                "outgoing": "line67b0e8cc895b1b9f9e0413dc50d1",
                "type": "EmptyStartEvent",
            },
        }
        self.creator = "start"
        self.template = PipelineTemplate.objects.create_model(self.data, creator=self.creator, template_id="1")
        self.instance, no_use = PipelineInstance.objects.create_instance(
            self.template, exec_data=self.data, creator=self.creator, instance_id="1"
        )
        self.instance_2, no_use = PipelineInstance.objects.create_instance(
            self.template, exec_data=self.data, creator=self.creator, instance_id="2"
        )
        self.instance_3, no_use = PipelineInstance.objects.create_instance(
            self.template, exec_data=self.data, creator=self.creator, instance_id="3"
        )

    @mock.patch("pipeline.models.PipelineTemplate.objects.unfold_subprocess", mock.MagicMock())
    def test_create_instance(self):
        creator = self.creator
        instance = self.instance
        self.assertIsNotNone(instance.snapshot)
        self.assertEqual(instance.snapshot.data, instance.data)
        self.assertEqual(creator, instance.creator)
        self.assertFalse(instance.is_started)
        self.assertFalse(instance.is_finished)
        self.assertFalse(instance.is_deleted)

        # test spread
        PipelineInstance.objects.create_instance(
            self.template, exec_data=self.data, creator=self.creator, instance_id="1"
        )

        PipelineTemplate.objects.unfold_subprocess.assert_called_with(self.data)

        PipelineTemplate.objects.unfold_subprocess.reset_mock()

        PipelineInstance.objects.create_instance(
            self.template, exec_data=self.data, creator=self.creator, instance_id="1", spread=True
        )

        PipelineTemplate.objects.unfold_subprocess.assert_not_called()

    def test_create_instance__without_template(self):
        self.instance_4, no_use = PipelineInstance.objects.create_instance(
            template=None, exec_data=self.data, creator=self.creator, instance_id="4"
        )
        self.assertIsNone(self.instance_4.template)
        self.assertIsNone(self.instance_4.snapshot)
        self.assertIsNotNone(self.instance_4.execution_snapshot)

    def test_set_started(self):
        PipelineInstance.objects.set_started(self.instance.instance_id, self.creator)
        self.instance.refresh_from_db()
        self.assertTrue(self.instance.is_started)

    def test_set_finished(self):
        NodeRelationship.objects.build_relationship(self.instance.instance_id, self.instance.instance_id)
        Status.objects.create(id=self.instance.instance_id, state=states.FINISHED)
        for act_id in self.data["activities"]:
            NodeRelationship.objects.build_relationship(self.instance.instance_id, act_id)
            Status.objects.create(id=act_id, state=states.FINISHED)
        NodeRelationship.objects.build_relationship(self.instance.instance_id, self.data["start_event"]["id"])
        Status.objects.create(id=self.data["start_event"]["id"], state=states.FINISHED)
        NodeRelationship.objects.build_relationship(self.instance.instance_id, self.data["end_event"]["id"])
        Status.objects.create(id=self.data["end_event"]["id"], state=states.FINISHED)

        post_pipeline_finish = MagicMock()
        with patch(PIPELINE_MODELS_POST_PIPELINE_FINISH, post_pipeline_finish):
            PipelineInstance.objects.set_finished(self.instance.instance_id)

        self.instance.refresh_from_db()
        self.assertTrue(self.instance.is_finished)
        post_pipeline_finish.send.assert_called_once_with(
            sender=PipelineInstance, instance_id=self.instance.instance_id
        )

    def test_set_revoked(self):
        NodeRelationship.objects.build_relationship(self.instance.instance_id, self.instance.instance_id)
        Status.objects.create(id=self.instance.instance_id, state=states.REVOKED)

        post_pipeline_revoke = MagicMock()
        with patch(PIPELINE_MODELS_POST_PIPELINE_REVOKE, post_pipeline_revoke):
            PipelineInstance.objects.set_revoked(self.instance.instance_id)

        self.instance.refresh_from_db()
        self.assertTrue(self.instance.is_revoked)
        post_pipeline_revoke.send.assert_called_once_with(
            sender=PipelineInstance, instance_id=self.instance.instance_id
        )

    def test_delete_instance(self):
        PipelineInstance.objects.delete_model(self.instance.instance_id)
        i = PipelineInstance.objects.get(instance_id=self.instance.instance_id)
        self.assertTrue(i.is_deleted)
        PipelineInstance.objects.delete_model([self.instance_2.instance_id, self.instance_3.instance_id])
        i2 = PipelineInstance.objects.get(instance_id=self.instance_2.instance_id)
        i3 = PipelineInstance.objects.get(instance_id=self.instance_3.instance_id)
        self.assertTrue(i2.is_deleted)
        self.assertTrue(i3.is_deleted)

    @patch(PIPELINE_MODELS_TASK_SERVICE_RUN_PIPELINE, MagicMock(return_value=ActionResult(result=True, message="")))
    @patch(PIPELINE_PIPELINE_INSTANCE_CALCULATE_TREE_INFO, MagicMock())
    @patch(PIPELINE_PIPELINE_INSTANCE_IMPORT_STRING, MagicMock(retrun_value=MockParser))
    def test_start__success(self):
        instance, no_use = PipelineInstance.objects.create_instance(
            self.template, exec_data=self.data, creator=self.creator
        )
        executor = "token_1"
        instance.start(executor)

        instance.refresh_from_db()

        instance.calculate_tree_info.assert_called_once()
        self.assertTrue(instance.is_started)
        self.assertEqual(instance.executor, executor)
        self.assertIsNotNone(instance.start_time)

        task_service.run_pipeline.assert_called_once()

    @patch(PIPELINE_MODELS_TASK_SERVICE_RUN_PIPELINE, MagicMock(return_value=ActionResult(result=False, message="")))
    @patch(PIPELINE_PIPELINE_INSTANCE_CALCULATE_TREE_INFO, MagicMock())
    def test_start__already_started(self):
        instance, no_use = PipelineInstance.objects.create_instance(
            self.template, exec_data=self.data, creator=self.creator
        )
        instance.is_started = True
        instance.save()
        executor = "token_1"

        instance.start(executor)

        instance.calculate_tree_info.assert_not_called()
        task_service.run_pipeline.assert_not_called()

    @patch(PIPELINE_MODELS_TASK_SERVICE_RUN_PIPELINE, MagicMock(return_value=ActionResult(result=False, message="")))
    @patch(PIPELINE_PIPELINE_INSTANCE_CALCULATE_TREE_INFO, MagicMock())
    @patch(PIPELINE_PIPELINE_INSTANCE_IMPORT_STRING, MagicMock(side_effect=ImportError()))
    def test_start__parser_cls_error(self):
        instance, no_use = PipelineInstance.objects.create_instance(
            self.template, exec_data=self.data, creator=self.creator
        )
        executor = "token_1"

        instance.start(executor)

        instance.refresh_from_db()

        self.assertFalse(instance.is_started)
        self.assertEqual(instance.executor, "")
        self.assertIsNone(instance.start_time)

        instance.calculate_tree_info.assert_not_called()
        task_service.run_pipeline.assert_not_called()

    @patch(PIPELINE_MODELS_TASK_SERVICE_RUN_PIPELINE, MagicMock(return_value=ActionResult(result=False, message="")))
    @patch(PIPELINE_PIPELINE_INSTANCE_CALCULATE_TREE_INFO, MagicMock())
    @patch(PIPELINE_PIPELINE_INSTANCE_IMPORT_STRING, MagicMock(retrun_value=MockParser))
    def test_start__task_service_call_fail(self):
        instance, no_use = PipelineInstance.objects.create_instance(
            self.template, exec_data=self.data, creator=self.creator
        )
        executor = "token_1"
        instance.start(executor)

        instance.refresh_from_db()

        instance.calculate_tree_info.assert_called_once()
        task_service.run_pipeline.assert_called_once()

        self.assertFalse(instance.is_started)
        self.assertEqual(instance.executor, "")
        self.assertIsNone(instance.start_time)

    @patch(PIPELINE_MODELS_TASK_SERVICE_RUN_PIPELINE, MagicMock(return_value=ActionResult(result=False, message="")))
    @patch(PIPELINE_PIPELINE_INSTANCE_CALCULATE_TREE_INFO, MagicMock(side_effect=Exception()))
    def test_start__error_occurred_before_task_service_call(self):
        instance, no_use = PipelineInstance.objects.create_instance(
            self.template, exec_data=self.data, creator=self.creator
        )
        executor = "token_1"

        try:
            instance.start(executor)
        except Exception:
            pass

        instance.refresh_from_db()

        self.assertFalse(instance.is_started)
        self.assertEqual(instance.executor, "")
        self.assertIsNone(instance.start_time)

        task_service.run_pipeline.assert_not_called()
