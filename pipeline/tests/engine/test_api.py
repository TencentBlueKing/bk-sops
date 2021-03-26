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

from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from redis.exceptions import ConnectionError as RedisConnectionError

from pipeline.constants import PIPELINE_DEFAULT_PRIORITY, PIPELINE_MAX_PRIORITY, PIPELINE_MIN_PRIORITY
from pipeline.core.flow.activity import ServiceActivity
from pipeline.core.flow.gateway import ExclusiveGateway, ParallelGateway
from pipeline.engine import api, exceptions, states
from pipeline.engine.models import (
    Data,
    NodeRelationship,
    PipelineModel,
    PipelineProcess,
    ProcessCeleryTask,
    ScheduleService,
    Status,
)
from pipeline.engine.utils import calculate_elapsed_time
from pipeline.tests.mock import *  # noqa
from pipeline.tests.mock_settings import *  # noqa


def dummy_wrapper(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


class TestEngineAPIDecorator(TestCase):
    def test__node_existence_check(self):
        @api._node_existence_check
        def test_func(id):
            return True

        with patch(PIPELINE_STATUS_GET, MagicMock()):
            self.assertTrue(test_func("id"))

        with patch(PIPELINE_STATUS_GET, MagicMock(side_effect=Status.DoesNotExist)):
            act_result = test_func("id")
            self.assertFalse(act_result.result)

    def test__frozen_check(self):
        @api._frozen_check
        def test_func():
            return True

        with patch(PIPELINE_FUNCTION_SWITCH_IS_FROZEN, MagicMock(return_value=False)):
            self.assertTrue(test_func())

        with patch(PIPELINE_FUNCTION_SWITCH_IS_FROZEN, MagicMock(return_value=True)):
            act_result = test_func()
            self.assertFalse(act_result.result)

    @mock.patch(DJCELERY_APP_CURRENT_APP_CONNECTION, mock.MagicMock())
    def test__worker_check(self):
        @api._worker_check
        def test_func():
            return True

        with patch(PIPELINE_ENGINE_API_WORKERS, MagicMock(return_value=[1, 2, 3])):
            self.assertTrue(test_func())

        with patch(PIPELINE_ENGINE_API_WORKERS, MagicMock(return_value=[])):
            act_result = test_func()
            self.assertFalse(act_result.result)

        with patch(PIPELINE_ENGINE_API_WORKERS, MagicMock(side_effect=exceptions.RabbitMQConnectionError)):
            act_result = test_func()
            self.assertFalse(act_result.result)

        with patch(PIPELINE_ENGINE_API_WORKERS, MagicMock(side_effect=RedisConnectionError)):
            act_result = test_func()
            self.assertFalse(act_result.result)


class TestEngineAPI(TestCase):
    def setUp(self):
        self.pipeline_id = uniqid()
        self.node_id = uniqid()
        self.version = uniqid()
        self.dummy_return = uniqid()
        self.maxDiff = None

    @patch(PIPELINE_STATUS_GET, MagicMock())
    @patch(PIPELINE_FUNCTION_SWITCH_IS_FROZEN, MagicMock(return_value=False))
    @patch(PIPELINE_ENGINE_API_WORKERS, MagicMock(return_value=True))
    @patch(PIPELINE_STATUS_PREPARE_FOR_PIPELINE, MagicMock())
    @patch(PIPELINE_PIPELINE_MODEL_PREPARE_FOR_PIPELINE, MagicMock())
    @patch(PIPELINE_PIPELINE_MODEL_PIPELINE_READY, MagicMock())
    @mock.patch(DJCELERY_APP_CURRENT_APP_CONNECTION, mock.MagicMock())
    def test_start_pipeline(self):
        process = MockPipelineProcess()
        pipeline_instance = "pipeline_instance"
        with patch(PIPELINE_PROCESS_PREPARE_FOR_PIPELINE, MagicMock(return_value=process)):
            act_result = api.start_pipeline(pipeline_instance)

            self.assertTrue(act_result.result)

            Status.objects.prepare_for_pipeline.assert_called_once_with(pipeline_instance)

            PipelineProcess.objects.prepare_for_pipeline.assert_called_once_with(pipeline_instance)

            PipelineModel.objects.prepare_for_pipeline.assert_called_once_with(
                pipeline_instance, process, PIPELINE_DEFAULT_PRIORITY, queue=""
            )

            PipelineModel.objects.pipeline_ready.assert_called_once_with(process_id=process.id)

    @patch(PIPELINE_FUNCTION_SWITCH_IS_FROZEN, MagicMock(return_value=False))
    @patch(PIPELINE_ENGINE_API_WORKERS, MagicMock(return_value=True))
    @mock.patch(DJCELERY_APP_CURRENT_APP_CONNECTION, mock.MagicMock())
    def test_start_pipeline__raise_invalid_operation(self):
        pipeline_instance = "pipeline_instance"

        self.assertRaises(
            exceptions.InvalidOperationException,
            api.start_pipeline,
            pipeline_instance,
            priority=PIPELINE_MAX_PRIORITY + 1,
        )
        self.assertRaises(
            exceptions.InvalidOperationException,
            api.start_pipeline,
            pipeline_instance,
            priority=PIPELINE_MIN_PRIORITY - 1,
        )

    @patch(PIPELINE_FUNCTION_SWITCH_IS_FROZEN, MagicMock(return_value=False))
    @patch(PIPELINE_STATUS_TRANSIT, MagicMock(return_value=MockActionResult(result=True)))
    def test_pause_pipeline(self):
        act_result = api.pause_pipeline(self.pipeline_id)

        Status.objects.transit.assert_called_once_with(
            id=self.pipeline_id, to_state=states.SUSPENDED, is_pipeline=True, appoint=True
        )

        self.assertTrue(act_result.result)

    @patch(PIPELINE_FUNCTION_SWITCH_IS_FROZEN, MagicMock(return_value=False))
    @patch(PIPELINE_ENGINE_API_WORKERS, MagicMock(return_value=True))
    @patch(PIPELINE_STATUS_TRANSIT, MagicMock(return_value=MockActionResult(result=False)))
    @mock.patch(DJCELERY_APP_CURRENT_APP_CONNECTION, mock.MagicMock())
    def test_resume_pipeline__transit_fail(self):
        act_result = api.resume_pipeline(self.pipeline_id)

        self.assertFalse(act_result.result)

    @patch(PIPELINE_FUNCTION_SWITCH_IS_FROZEN, MagicMock(return_value=False))
    @patch(PIPELINE_ENGINE_API_WORKERS, MagicMock(return_value=True))
    @patch(PIPELINE_STATUS_TRANSIT, MagicMock(return_value=MockActionResult(result=True)))
    @patch(PIPELINE_PROCESS_BATCH_PROCESS_READY, MagicMock())
    @patch(PIPELINE_ENGINE_API_GET_PROCESS_TO_BE_WAKED, MagicMock())
    @mock.patch(DJCELERY_APP_CURRENT_APP_CONNECTION, mock.MagicMock())
    def test_resume_pipeline__transit_success(self):
        pipeline_model = MockPipelineModel()

        with patch(PIPELINE_PIPELINE_MODEL_GET, MagicMock(return_value=pipeline_model)):
            act_result = api.resume_pipeline(self.pipeline_id)

            self.assertTrue(act_result.result)

            api._get_process_to_be_waked.assert_called_once_with(pipeline_model.process, [])

            PipelineProcess.objects.batch_process_ready.assert_called_once_with(
                process_id_list=[], pipeline_id=self.pipeline_id
            )

    @patch(PIPELINE_FUNCTION_SWITCH_IS_FROZEN, MagicMock(return_value=False))
    @patch(PIPELINE_STATUS_TRANSIT, MagicMock(return_value=MockActionResult(result=False)))
    def test_revoke_pipeline__transit_fail(self):
        act_result = api.revoke_pipeline(self.pipeline_id)

        self.assertFalse(act_result.result)

    @patch(PIPELINE_FUNCTION_SWITCH_IS_FROZEN, MagicMock(return_value=False))
    @patch(PIPELINE_STATUS_TRANSIT, MagicMock(return_value=MockActionResult(result=True)))
    def test_revoke_pipeline__process_is_none(self):
        pipeline_model = MockPipelineModel(process=None)

        with patch(PIPELINE_PIPELINE_MODEL_GET, MagicMock(return_value=pipeline_model)):
            act_result = api.revoke_pipeline(self.pipeline_id)

            self.assertFalse(act_result.result)

    @patch(PIPELINE_FUNCTION_SWITCH_IS_FROZEN, MagicMock(return_value=False))
    @patch(PIPELINE_STATUS_TRANSIT, MagicMock(return_value=MockActionResult(result=True)))
    @mock.patch(DJCELERY_APP_CURRENT_APP_CONNECTION, mock.MagicMock())
    def test_revoke_pipeline__transit_success(self):
        pipeline_model = MockPipelineModel()

        with patch(PIPELINE_PIPELINE_MODEL_GET, MagicMock(return_value=pipeline_model)):
            with mock.patch(
                PIPELINE_PROCESS_SELECT_FOR_UPDATE,
                mock.MagicMock(return_value=MockQuerySet(get_return=pipeline_model.process)),
            ):
                act_result = api.revoke_pipeline(self.pipeline_id)

                self.assertTrue(act_result.result)

                pipeline_model.process.revoke_subprocess.assert_called_once()
                pipeline_model.process.destroy_all.assert_called_once()

    @patch(PIPELINE_FUNCTION_SWITCH_IS_FROZEN, MagicMock(return_value=False))
    @patch(PIPELINE_STATUS_TRANSIT, MagicMock(return_value=MockActionResult(result=True)))
    def test_pause_node_appointment(self):
        act_result = api.pause_node_appointment(self.node_id)

        self.assertTrue(act_result.result)

        Status.objects.transit.assert_called_once_with(id=self.node_id, to_state=states.SUSPENDED, appoint=True)

    @patch(PIPELINE_STATUS_GET, MagicMock())
    @patch(PIPELINE_FUNCTION_SWITCH_IS_FROZEN, MagicMock(return_value=False))
    @patch(PIPELINE_ENGINE_API_WORKERS, MagicMock(return_value=True))
    @patch(PIPELINE_PROCESS_FILTER, MagicMock(return_value=MockQuerySet(exists_return=False)))
    @patch(
        PIPELINE_SUBPROCESS_RELATIONSHIP_GET_RELATE_PROCESS, MagicMock(return_value=MockQuerySet(exists_return=False))
    )
    @mock.patch(DJCELERY_APP_CURRENT_APP_CONNECTION, mock.MagicMock())
    def test_resume_node_appointment__fail_with_invalid_node(self):
        act_result = api.resume_node_appointment(self.node_id)

        self.assertFalse(act_result.result)

    @patch(PIPELINE_STATUS_GET, MagicMock())
    @patch(PIPELINE_FUNCTION_SWITCH_IS_FROZEN, MagicMock(return_value=False))
    @patch(PIPELINE_ENGINE_API_WORKERS, MagicMock(return_value=True))
    @patch(PIPELINE_STATUS_TRANSIT, MagicMock(return_value=MockActionResult(result=False)))
    @patch(PIPELINE_PROCESS_FILTER, MagicMock(return_value=MockQuerySet(exists_return=True)))
    @mock.patch(DJCELERY_APP_CURRENT_APP_CONNECTION, mock.MagicMock())
    def test_resume_node_appointment__resume_not_subprocess_transit_fail(self):
        act_result = api.resume_node_appointment(self.node_id)

        Status.objects.transit.assert_called_once_with(id=self.node_id, to_state=states.READY, appoint=True)

        self.assertFalse(act_result.result)

    @patch(PIPELINE_STATUS_GET, MagicMock())
    @patch(PIPELINE_FUNCTION_SWITCH_IS_FROZEN, MagicMock(return_value=False))
    @patch(PIPELINE_ENGINE_API_WORKERS, MagicMock(return_value=True))
    @patch(PIPELINE_STATUS_TRANSIT, MagicMock(return_value=MockActionResult(result=True)))
    @patch(PIPELINE_STATUS_RECOVER_FROM_BLOCK, MagicMock())
    @patch(PIPELINE_PROCESS_PROCESS_READY, MagicMock())
    @mock.patch(DJCELERY_APP_CURRENT_APP_CONNECTION, mock.MagicMock())
    def test_resume_node_appointment__resume_not_subprocess(self):
        process = MockPipelineProcess()

        with patch(
            PIPELINE_PROCESS_FILTER, MagicMock(return_value=MockQuerySet(exists_return=True, first_return=process))
        ):
            act_result = api.resume_node_appointment(self.node_id)

            self.assertTrue(act_result.result)

            Status.objects.transit.assert_called_once_with(id=self.node_id, to_state=states.READY, appoint=True)

            Status.objects.recover_from_block.assert_called_once_with(
                process.root_pipeline.id, process.subprocess_stack
            )

            PipelineProcess.objects.process_ready.assert_called_once_with(process_id=process.id)

    @patch(PIPELINE_STATUS_GET, MagicMock())
    @patch(PIPELINE_FUNCTION_SWITCH_IS_FROZEN, MagicMock(return_value=False))
    @patch(PIPELINE_ENGINE_API_WORKERS, MagicMock(return_value=True))
    @patch(PIPELINE_STATUS_TRANSIT, MagicMock(return_value=MockActionResult(result=False)))
    @patch(PIPELINE_PROCESS_FILTER, MagicMock(return_value=MockQuerySet(exists_return=False)))
    @patch(
        PIPELINE_SUBPROCESS_RELATIONSHIP_GET_RELATE_PROCESS, MagicMock(return_value=MockQuerySet(exists_return=True))
    )
    @mock.patch(DJCELERY_APP_CURRENT_APP_CONNECTION, mock.MagicMock())
    def test_resume_node_appointment__resume_subprocess_transit_fail(self):
        act_result = api.resume_node_appointment(self.node_id)

        Status.objects.transit.assert_called_once_with(
            id=self.node_id, to_state=states.RUNNING, is_pipeline=True, appoint=True
        )

        self.assertFalse(act_result.result)

    @patch(PIPELINE_STATUS_GET, MagicMock())
    @patch(PIPELINE_FUNCTION_SWITCH_IS_FROZEN, MagicMock(return_value=False))
    @patch(PIPELINE_ENGINE_API_WORKERS, MagicMock(return_value=True))
    @patch(PIPELINE_STATUS_TRANSIT, MagicMock(return_value=MockActionResult(result=True)))
    @patch(PIPELINE_PROCESS_FILTER, MagicMock(return_value=MockQuerySet(exists_return=False)))
    @patch(PIPELINE_STATUS_RECOVER_FROM_BLOCK, MagicMock())
    @patch(PIPELINE_PROCESS_BATCH_PROCESS_READY, MagicMock())
    @mock.patch(DJCELERY_APP_CURRENT_APP_CONNECTION, mock.MagicMock())
    def test_resume_node_appointment__resume_subprocess(self):
        root_pipeline = PipelineObject()

        can_be_wake_process_1 = MockPipelineProcess(can_be_waked=True, root_pipeline=root_pipeline)
        can_be_wake_process_2 = MockPipelineProcess(can_be_waked=True, root_pipeline=root_pipeline)
        can_be_wake_process_3 = MockPipelineProcess(can_be_waked=True, root_pipeline=root_pipeline)
        can_not_be_wake_process_1 = MockPipelineProcess(root_pipeline=root_pipeline)
        can_not_be_wake_process_2 = MockPipelineProcess(root_pipeline=root_pipeline)

        exists_return = [
            can_be_wake_process_1,
            can_be_wake_process_2,
            can_be_wake_process_3,
            can_not_be_wake_process_1,
            can_not_be_wake_process_2,
        ]

        subprocess_to_be_transit = {can_be_wake_process_1.id, can_be_wake_process_2.id, can_be_wake_process_3.id}

        can_be_waked_ids = [can_be_wake_process_1.id, can_be_wake_process_2.id, can_be_wake_process_3.id]

        with patch(
            PIPELINE_SUBPROCESS_RELATIONSHIP_GET_RELATE_PROCESS,
            MagicMock(
                return_value=MockQuerySet(
                    exists_return=exists_return, first_return=can_be_wake_process_1, qs=exists_return
                )
            ),
        ):
            act_result = api.resume_node_appointment(self.node_id)

            self.assertTrue(act_result.result)

            Status.objects.recover_from_block.assert_called_once_with(root_pipeline.id, subprocess_to_be_transit)

            PipelineProcess.objects.batch_process_ready.assert_called_once_with(
                process_id_list=can_be_waked_ids, pipeline_id=root_pipeline.id
            )

    @patch(PIPELINE_STATUS_GET, MagicMock())
    @patch(PIPELINE_FUNCTION_SWITCH_IS_FROZEN, MagicMock(return_value=False))
    @patch(PIPELINE_ENGINE_API_WORKERS, MagicMock(return_value=True))
    @patch(PIPELINE_PROCESS_GET, MagicMock(side_effect=PipelineProcess.DoesNotExist))
    @mock.patch(DJCELERY_APP_CURRENT_APP_CONNECTION, mock.MagicMock())
    def test_retry_node__fail_with_can_not_get_process(self):
        act_result = api.retry_node(self.node_id)

        self.assertFalse(act_result.result)

    @patch(PIPELINE_STATUS_GET, MagicMock())
    @patch(PIPELINE_FUNCTION_SWITCH_IS_FROZEN, MagicMock(return_value=False))
    @patch(PIPELINE_ENGINE_API_WORKERS, MagicMock(return_value=True))
    @mock.patch(DJCELERY_APP_CURRENT_APP_CONNECTION, mock.MagicMock())
    def test_retry_node__fail_with_invalid_node_type(self):
        top_pipeline = PipelineObject(nodes={self.node_id: ServiceActObject()})
        process = MockPipelineProcess(top_pipeline=top_pipeline)

        with patch(PIPELINE_PROCESS_GET, MagicMock(return_value=process)):
            act_result = api.retry_node(self.node_id)

            self.assertFalse(act_result.result)

    @patch(PIPELINE_STATUS_GET, MagicMock())
    @patch(PIPELINE_FUNCTION_SWITCH_IS_FROZEN, MagicMock(return_value=False))
    @patch(PIPELINE_ENGINE_API_WORKERS, MagicMock(return_value=True))
    @mock.patch(DJCELERY_APP_CURRENT_APP_CONNECTION, mock.MagicMock())
    def test_retry_node__with_node_can_not_retry(self):
        # with service activity
        top_pipeline = PipelineObject(
            nodes={self.node_id: ServiceActivity(id=self.node_id, service=None, retryable=False)}
        )
        process = MockPipelineProcess(top_pipeline=top_pipeline)

        with patch(PIPELINE_PROCESS_GET, MagicMock(return_value=process)):
            act_result = api.retry_node(self.node_id)

            self.assertFalse(act_result.result)

        # with parallel gateway
        pg = ParallelGateway(id=self.node_id, converge_gateway_id=uniqid())
        setattr(pg, "retryable", False)
        top_pipeline = PipelineObject(nodes={self.node_id: pg})
        process = MockPipelineProcess(top_pipeline=top_pipeline)

        with patch(PIPELINE_PROCESS_GET, MagicMock(return_value=process)):
            act_result = api.retry_node(self.node_id)

            self.assertFalse(act_result.result)

    @patch(PIPELINE_STATUS_GET, MagicMock())
    @patch(PIPELINE_FUNCTION_SWITCH_IS_FROZEN, MagicMock(return_value=False))
    @patch(PIPELINE_ENGINE_API_WORKERS, MagicMock(return_value=True))
    @patch(PIPELINE_STATUS_RETRY, MagicMock(return_value=MockActionResult(result=False, message="retry fail")))
    @mock.patch(DJCELERY_APP_CURRENT_APP_CONNECTION, mock.MagicMock())
    def test_retry_node__with_retry_fail(self):
        node = ServiceActivity(id=self.node_id, service=None)
        top_pipeline = PipelineObject(nodes={self.node_id: node})
        process = MockPipelineProcess(top_pipeline=top_pipeline)

        with patch(PIPELINE_PROCESS_GET, MagicMock(return_value=process)):
            act_result = api.retry_node(self.node_id)

            Status.objects.retry.assert_called_once_with(process, node, None)

            self.assertFalse(act_result.result)

    @patch(PIPELINE_STATUS_GET, MagicMock())
    @patch(PIPELINE_FUNCTION_SWITCH_IS_FROZEN, MagicMock(return_value=False))
    @patch(PIPELINE_ENGINE_API_WORKERS, MagicMock(return_value=True))
    @patch(PIPELINE_STATUS_RETRY, MagicMock(return_value=MockActionResult(result=True)))
    @patch(PIPELINE_PROCESS_PROCESS_READY, MagicMock())
    @mock.patch(DJCELERY_APP_CURRENT_APP_CONNECTION, mock.MagicMock())
    def test_retry_node__success(self):
        node = ServiceActivity(id=self.node_id, service=None)
        top_pipeline = PipelineObject(nodes={self.node_id: node})
        process = MockPipelineProcess(top_pipeline=top_pipeline)
        retry_inputs = {"id": self.node_id}

        with patch(PIPELINE_PROCESS_GET, MagicMock(return_value=process)):
            act_result = api.retry_node(self.node_id, inputs=retry_inputs)

            self.assertTrue(act_result.result)

            Status.objects.retry.assert_called_once_with(process, node, retry_inputs)

            PipelineProcess.objects.process_ready.assert_called_once_with(process_id=process.id)

    @patch(PIPELINE_STATUS_GET, MagicMock())
    @patch(PIPELINE_FUNCTION_SWITCH_IS_FROZEN, MagicMock(return_value=False))
    @patch(PIPELINE_ENGINE_API_WORKERS, MagicMock(return_value=True))
    @patch(PIPELINE_PROCESS_GET, MagicMock(side_effect=PipelineProcess.DoesNotExist))
    @mock.patch(DJCELERY_APP_CURRENT_APP_CONNECTION, mock.MagicMock())
    def test_skip_node__fail_with_can_not_get_process(self):
        act_result = api.skip_node(self.node_id)

        self.assertFalse(act_result.result)

    @patch(PIPELINE_STATUS_GET, MagicMock())
    @patch(PIPELINE_FUNCTION_SWITCH_IS_FROZEN, MagicMock(return_value=False))
    @patch(PIPELINE_ENGINE_API_WORKERS, MagicMock(return_value=True))
    @mock.patch(DJCELERY_APP_CURRENT_APP_CONNECTION, mock.MagicMock())
    def test_skip_node__fail_with_invalid_node_type(self):
        top_pipeline = PipelineObject(nodes={self.node_id: ServiceActObject()})
        process = MockPipelineProcess(top_pipeline=top_pipeline)

        with patch(PIPELINE_PROCESS_GET, MagicMock(return_value=process)):
            act_result = api.skip_node(self.node_id)

            self.assertFalse(act_result.result)

    @patch(PIPELINE_STATUS_GET, MagicMock())
    @patch(PIPELINE_FUNCTION_SWITCH_IS_FROZEN, MagicMock(return_value=False))
    @patch(PIPELINE_ENGINE_API_WORKERS, MagicMock(return_value=True))
    @mock.patch(DJCELERY_APP_CURRENT_APP_CONNECTION, mock.MagicMock())
    def test_skip_node__fail_with_node_can_not_skip(self):
        top_pipeline = PipelineObject(
            nodes={self.node_id: ServiceActivity(id=self.node_id, service=None, skippable=False)}
        )
        process = MockPipelineProcess(top_pipeline=top_pipeline)

        with patch(PIPELINE_PROCESS_GET, MagicMock(return_value=process)):
            act_result = api.skip_node(self.node_id)

            self.assertFalse(act_result.result)

    @patch(PIPELINE_STATUS_GET, MagicMock())
    @patch(PIPELINE_FUNCTION_SWITCH_IS_FROZEN, MagicMock(return_value=False))
    @patch(PIPELINE_ENGINE_API_WORKERS, MagicMock(return_value=True))
    @patch(PIPELINE_STATUS_SKIP, MagicMock(return_value=MockActionResult(result=False, message="skip fail")))
    @mock.patch(DJCELERY_APP_CURRENT_APP_CONNECTION, mock.MagicMock())
    def test_skip_node__fail_with_skip_fail(self):
        node = ServiceActivity(id=self.node_id, service=None)
        top_pipeline = PipelineObject(nodes={self.node_id: node})
        process = MockPipelineProcess(top_pipeline=top_pipeline)

        with patch(PIPELINE_PROCESS_GET, MagicMock(return_value=process)):
            act_result = api.skip_node(self.node_id)

            Status.objects.skip.assert_called_once_with(process, node)

            self.assertFalse(act_result.result)

    @patch(PIPELINE_STATUS_GET, MagicMock())
    @patch(PIPELINE_FUNCTION_SWITCH_IS_FROZEN, MagicMock(return_value=False))
    @patch(PIPELINE_ENGINE_API_WORKERS, MagicMock(return_value=True))
    @patch(PIPELINE_STATUS_SKIP, MagicMock(return_value=MockActionResult(result=True)))
    @patch(PIPELINE_PROCESS_PROCESS_READY, MagicMock())
    @mock.patch(DJCELERY_APP_CURRENT_APP_CONNECTION, mock.MagicMock())
    def test_skip_node__success(self):
        node = ServiceActivity(id=self.node_id, service=None)
        mock_next = IdentifyObject()

        def _next():
            return mock_next

        setattr(node, "next", _next)
        top_pipeline = PipelineObject(nodes={self.node_id: node}, context=MockContext())
        process = MockPipelineProcess(top_pipeline=top_pipeline)

        with patch(PIPELINE_PROCESS_GET, MagicMock(return_value=process)):
            act_result = api.skip_node(self.node_id)

            self.assertTrue(act_result.result)

            process.top_pipeline.context.extract_output.assert_called_once_with(node)

            process.save.assert_called_once()

            PipelineProcess.objects.process_ready(process_id=process.id, current_node_id=mock_next.id)

    @patch(PIPELINE_STATUS_GET, MagicMock())
    @patch(PIPELINE_FUNCTION_SWITCH_IS_FROZEN, MagicMock(return_value=False))
    @patch(PIPELINE_ENGINE_API_WORKERS, MagicMock(return_value=True))
    @patch(PIPELINE_PROCESS_GET, MagicMock(side_effect=PipelineProcess.DoesNotExist))
    @mock.patch(DJCELERY_APP_CURRENT_APP_CONNECTION, mock.MagicMock())
    def test_skip_exclusive_gateway__fail_with_can_not_get_process(self):
        act_result = api.skip_exclusive_gateway(self.node_id, uniqid())

        self.assertFalse(act_result.result)

    @patch(PIPELINE_STATUS_GET, MagicMock())
    @patch(PIPELINE_FUNCTION_SWITCH_IS_FROZEN, MagicMock(return_value=False))
    @patch(PIPELINE_ENGINE_API_WORKERS, MagicMock(return_value=True))
    @mock.patch(DJCELERY_APP_CURRENT_APP_CONNECTION, mock.MagicMock())
    def test_skip_exclusive_gateway__fail_with_invalid_node_type(self):
        top_pipeline = PipelineObject(nodes={self.node_id: ServiceActObject()})
        process = MockPipelineProcess(top_pipeline=top_pipeline)

        with patch(PIPELINE_PROCESS_GET, MagicMock(return_value=process)):
            act_result = api.skip_exclusive_gateway(self.node_id, uniqid())

            self.assertFalse(act_result.result)

    @patch(PIPELINE_STATUS_GET, MagicMock())
    @patch(PIPELINE_FUNCTION_SWITCH_IS_FROZEN, MagicMock(return_value=False))
    @patch(PIPELINE_ENGINE_API_WORKERS, MagicMock(return_value=True))
    @patch(PIPELINE_STATUS_SKIP, MagicMock(return_value=MockActionResult(result=False, message="skip fail")))
    @mock.patch(DJCELERY_APP_CURRENT_APP_CONNECTION, mock.MagicMock())
    def test_skip_exclusive_gateway__fail_with_skip_fail(self):
        eg = ExclusiveGateway(id=uniqid())
        next_node = IdentifyObject()
        setattr(eg, "target_for_sequence_flow", MagicMock(return_value=next_node))
        top_pipeline = PipelineObject(nodes={self.node_id: eg})
        process = MockPipelineProcess(top_pipeline=top_pipeline)

        with patch(PIPELINE_PROCESS_GET, MagicMock(return_value=process)):
            act_result = api.skip_exclusive_gateway(self.node_id, uniqid())

            Status.objects.skip.assert_called_once_with(process, eg)

            self.assertFalse(act_result.result)

    @patch(PIPELINE_STATUS_GET, MagicMock())
    @patch(PIPELINE_FUNCTION_SWITCH_IS_FROZEN, MagicMock(return_value=False))
    @patch(PIPELINE_ENGINE_API_WORKERS, MagicMock(return_value=True))
    @patch(PIPELINE_STATUS_SKIP, MagicMock(return_value=MockActionResult(result=True)))
    @patch(PIPELINE_PROCESS_PROCESS_READY, MagicMock())
    @mock.patch(DJCELERY_APP_CURRENT_APP_CONNECTION, mock.MagicMock())
    def test_skip_exclusive_gateway__success(self):
        eg = ExclusiveGateway(id=uniqid())
        next_node = IdentifyObject()
        setattr(eg, "target_for_sequence_flow", MagicMock(return_value=next_node))
        top_pipeline = PipelineObject(nodes={self.node_id: eg})
        process = MockPipelineProcess(top_pipeline=top_pipeline)

        with patch(PIPELINE_PROCESS_GET, MagicMock(return_value=process)):
            act_result = api.skip_exclusive_gateway(self.node_id, uniqid())

            self.assertTrue(act_result.result)

            Status.objects.skip.assert_called_once_with(process, eg)

            PipelineProcess.objects.process_ready.assert_called_once_with(
                process_id=process.id, current_node_id=next_node.id
            )

    @patch(PIPELINE_NODE_RELATIONSHIP_FILTER, MagicMock(return_value=MockQuerySet(exists_return=False)))
    def test_status_tree__with_not_exist_node(self):
        self.assertRaises(exceptions.InvalidOperationException, api.get_status_tree, self.node_id)

    def test_status_tree(self):
        s1 = Status.objects.create(
            id=uniqid(),
            name="s1",
            state=states.FINISHED,
            started_time=timezone.now(),
            archived_time=timezone.now() + timedelta(seconds=3),
        )
        s2 = Status.objects.create(
            id=uniqid(),
            name="s2",
            state=states.FINISHED,
            started_time=timezone.now(),
            archived_time=timezone.now() + timedelta(seconds=3),
        )
        s3 = Status.objects.create(
            id=uniqid(),
            name="s3",
            state=states.FINISHED,
            started_time=timezone.now(),
            archived_time=timezone.now() + timedelta(seconds=3),
        )
        s4 = Status.objects.create(
            id=uniqid(),
            name="s4",
            state=states.FINISHED,
            started_time=timezone.now(),
            archived_time=timezone.now() + timedelta(seconds=3),
        )
        s5 = Status.objects.create(
            id=uniqid(),
            name="s5",
            state=states.FINISHED,
            started_time=timezone.now(),
            archived_time=timezone.now() + timedelta(seconds=3),
        )
        s6 = Status.objects.create(
            id=uniqid(),
            name="s6",
            state=states.FINISHED,
            started_time=timezone.now(),
            archived_time=timezone.now() + timedelta(seconds=3),
        )

        NodeRelationship.objects.build_relationship(s1.id, s1.id)
        NodeRelationship.objects.build_relationship(s2.id, s2.id)
        NodeRelationship.objects.build_relationship(s3.id, s3.id)
        NodeRelationship.objects.build_relationship(s4.id, s4.id)
        NodeRelationship.objects.build_relationship(s5.id, s5.id)
        NodeRelationship.objects.build_relationship(s6.id, s6.id)

        NodeRelationship.objects.build_relationship(s1.id, s2.id)
        NodeRelationship.objects.build_relationship(s1.id, s3.id)
        NodeRelationship.objects.build_relationship(s2.id, s4.id)
        NodeRelationship.objects.build_relationship(s4.id, s5.id)
        NodeRelationship.objects.build_relationship(s4.id, s6.id)

        # refresh from db, sync datetime
        s1.refresh_from_db()
        s2.refresh_from_db()
        s3.refresh_from_db()
        s4.refresh_from_db()
        s5.refresh_from_db()
        s6.refresh_from_db()

        def get_status_dict_with_children(s, children):
            return {
                "archived_time": s.archived_time,
                "created_time": s.created_time,
                "elapsed_time": calculate_elapsed_time(s.started_time, s.archived_time),
                "error_ignorable": s.error_ignorable,
                "id": s.id,
                "loop": s.loop,
                "name": s.name,
                "retry": s.retry,
                "skip": s.skip,
                "started_time": s.started_time,
                "state": s.state,
                "version": s.version,
                "children": children,
                "state_refresh_at": None,
            }

        tree_depth_1 = get_status_dict_with_children(
            s1,
            children={
                s2.id: get_status_dict_with_children(s2, children={}),
                s3.id: get_status_dict_with_children(s3, children={}),
            },
        )

        tree = api.get_status_tree(s1.id, 1)
        self.assertDictEqual(tree, tree_depth_1)

        tree_depth_2 = get_status_dict_with_children(
            s1,
            children={
                s2.id: get_status_dict_with_children(s2, children={s4.id: get_status_dict_with_children(s4, {})}),
                s3.id: get_status_dict_with_children(s3, {}),
            },
        )

        tree = api.get_status_tree(s1.id, 2)
        self.assertDictEqual(tree, tree_depth_2)

        tree_depth_3 = get_status_dict_with_children(
            s1,
            children={
                s2.id: get_status_dict_with_children(
                    s2,
                    children={
                        s4.id: get_status_dict_with_children(
                            s4,
                            children={
                                s5.id: get_status_dict_with_children(s5, {}),
                                s6.id: get_status_dict_with_children(s6, {}),
                            },
                        )
                    },
                ),
                s3.id: get_status_dict_with_children(s3, children={}),
            },
        )  # noqa

        tree = api.get_status_tree(s1.id, 3)
        self.assertDictEqual(tree, tree_depth_3)

        tree = api.get_status_tree(s1.id, 4)
        self.assertDictEqual(tree, tree_depth_3)

    @patch(PIPELINE_FUNCTION_SWITCH_IS_FROZEN, MagicMock(return_value=False))
    @patch(PIPELINE_ENGINE_API_WORKERS, MagicMock(return_value=True))
    @patch(PIPELINE_SCHEDULE_SCHEDULE_FOR, MagicMock(side_effect=ScheduleService.DoesNotExist))
    @mock.patch(DJCELERY_APP_CURRENT_APP_CONNECTION, mock.MagicMock())
    def test_activity_callback__fail_with_schedule_not_exist(self):
        with patch(PIPELINE_STATUS_VERSION_FOR, MagicMock(return_value=self.version)):
            self.assertRaises(ScheduleService.DoesNotExist, api.activity_callback, self.node_id, None)

            ScheduleService.objects.schedule_for.assert_has_calls([mock.call(self.node_id, self.version)] * 3)

    @patch(PIPELINE_FUNCTION_SWITCH_IS_FROZEN, MagicMock(return_value=False))
    @patch(PIPELINE_ENGINE_API_WORKERS, MagicMock(return_value=True))
    @patch(PIPELINE_SCHEDULE_SCHEDULE_FOR, MagicMock())
    @mock.patch(DJCELERY_APP_CURRENT_APP_CONNECTION, mock.MagicMock())
    def test_activity_callback__fail_with_process_not_exist(self):
        with patch(PIPELINE_STATUS_VERSION_FOR, MagicMock(return_value=self.version)):
            act_result = api.activity_callback(self.node_id, None)

            ScheduleService.objects.schedule_for.assert_called_once_with(self.node_id, self.version)

            self.assertFalse(act_result.result)

    @patch(PIPELINE_FUNCTION_SWITCH_IS_FROZEN, MagicMock(return_value=False))
    @patch(PIPELINE_ENGINE_API_WORKERS, MagicMock(return_value=True))
    @patch(PIPELINE_PROCESS_GET, MagicMock(return_value=IdentifyObject()))
    @mock.patch(DJCELERY_APP_CURRENT_APP_CONNECTION, mock.MagicMock())
    def test_activity_callback__fail_with_schedule_finished(self):
        with patch(PIPELINE_STATUS_VERSION_FOR, MagicMock(return_value=self.version)):
            with patch(PIPELINE_SCHEDULE_SCHEDULE_FOR, MagicMock(return_value=MockScheduleService(is_finished=True))):
                self.assertRaises(exceptions.InvalidOperationException, api.activity_callback, self.node_id, None)

                ScheduleService.objects.schedule_for.assert_called_once_with(self.node_id, self.version)

    @patch(PIPELINE_FUNCTION_SWITCH_IS_FROZEN, MagicMock(return_value=False))
    @patch(PIPELINE_ENGINE_API_WORKERS, MagicMock(return_value=True))
    @mock.patch(DJCELERY_APP_CURRENT_APP_CONNECTION, mock.MagicMock())
    def test_activity_callback__success(self):
        process = MockPipelineProcess()
        callback_data = uniqid()

        with patch(PIPELINE_STATUS_VERSION_FOR, MagicMock(return_value=self.version)):
            with patch(PIPELINE_PROCESS_GET, MagicMock(return_value=process)):
                # schedule service get once
                service = MockScheduleService()
                with patch(PIPELINE_SCHEDULE_SCHEDULE_FOR, MagicMock(return_value=service)):
                    act_result = api.activity_callback(self.node_id, callback_data)

                    self.assertTrue(act_result.result)

                    ScheduleService.objects.schedule_for.assert_called_once_with(self.node_id, self.version)

                    service.callback.assert_called_once_with(callback_data, process.id)

                # schedule service get twice
                service = MockScheduleService()
                with patch(
                    PIPELINE_SCHEDULE_SCHEDULE_FOR, MagicMock(side_effect=[ScheduleService.DoesNotExist, service])
                ):
                    act_result = api.activity_callback(self.node_id, callback_data)

                    self.assertTrue(act_result.result)

                    ScheduleService.objects.schedule_for.assert_has_calls([mock.call(self.node_id, self.version)] * 2)

                    service.callback.assert_called_once_with(callback_data, process.id)

    def test_get_inputs(self):
        data = MockData(get_inputs_return=uniqid())
        with patch(PIPELINE_DATA_GET, MagicMock(return_value=data)):
            inputs = api.get_inputs(self.node_id)
            self.assertEqual(inputs, data.inputs)

    def test_get_outputs(self):
        data = MockData(get_inputs_return=uniqid(), get_outputs_return=uniqid())
        with patch(PIPELINE_DATA_GET, MagicMock(return_value=data)):
            outputs = api.get_outputs(self.node_id)
            self.assertEqual(outputs, {"outputs": data.outputs, "ex_data": data.ex_data})

    def test_get_batch_outputs(self):
        data1 = MockData(get_inputs_return=uniqid(), get_outputs_return=uniqid())
        data2 = MockData(get_inputs_return=uniqid(), get_outputs_return=uniqid())
        data3 = MockData(get_inputs_return=uniqid(), get_outputs_return=uniqid())
        with patch(
            PIPELINE_DATA_FILTER, MagicMock(return_value=MockQuerySet(exists_return=True, qs=[data1, data2, data3]))
        ):
            outputs = api.get_batch_outputs([data1.id, data2.id, data3.id])
            self.assertEqual(
                outputs,
                {
                    data1.id: {"outputs": data1.outputs, "ex_data": data1.ex_data},
                    data2.id: {"outputs": data2.outputs, "ex_data": data2.ex_data},
                    data3.id: {"outputs": data3.outputs, "ex_data": data3.ex_data},
                },
            )

    def test_get_activity_histories(self):
        with patch(PIPELINE_HISTORY_GET_HISTORY, MagicMock(return_value=self.dummy_return)):
            history = api.get_activity_histories(self.node_id)
            self.assertEqual(history, self.dummy_return)

    @patch(PIPELINE_STATUS_GET, MagicMock())
    @patch(PIPELINE_FUNCTION_SWITCH_IS_FROZEN, MagicMock(return_value=False))
    @patch(PIPELINE_PROCESS_GET, MagicMock(side_effect=PipelineProcess.DoesNotExist))
    def test_forced_fail__fail_with_process_do_not_exist(self):
        act_result = api.forced_fail(self.node_id)

        self.assertFalse(act_result.result)

    @patch(PIPELINE_STATUS_GET, MagicMock())
    @patch(PIPELINE_FUNCTION_SWITCH_IS_FROZEN, MagicMock(return_value=False))
    def test_forced_fail__fail_with_invalid_node_type(self):
        top_pipeline = PipelineObject(nodes={self.node_id: ServiceActObject()})
        process = MockPipelineProcess(top_pipeline=top_pipeline)

        with patch(PIPELINE_PROCESS_GET, MagicMock(return_value=process)):
            act_result = api.forced_fail(self.node_id, uniqid())

            self.assertFalse(act_result.result)

    @patch(PIPELINE_STATUS_GET, MagicMock())
    @patch(PIPELINE_FUNCTION_SWITCH_IS_FROZEN, MagicMock(return_value=False))
    @patch(PIPELINE_STATUS_TRANSIT, MagicMock(return_value=MockActionResult(result=False, message="transit fail")))
    def test_forced_fail__fail_with_transit_fail(self):
        top_pipeline = PipelineObject(nodes={self.node_id: ServiceActivity(id=self.node_id, service=None)})
        process = MockPipelineProcess(top_pipeline=top_pipeline)

        with patch(PIPELINE_PROCESS_GET, MagicMock(return_value=process)):
            act_result = api.forced_fail(self.node_id)

            self.assertFalse(act_result.result)

    @patch(PIPELINE_FUNCTION_SWITCH_IS_FROZEN, MagicMock(return_value=False))
    @patch(PIPELINE_STATUS_TRANSIT, MagicMock(return_value=MockActionResult(result=True)))
    @patch(PIPELINE_SCHEDULE_DELETE_SCHEDULE, MagicMock())
    @patch(PIPELINE_CELERYTASK_REVOKE, MagicMock())
    @patch(PIPELINE_DATA_FORCED_FAIL, MagicMock())
    def test_forced_fail__success(self):
        node = ServiceActivity(id=self.node_id, service=None)
        setattr(node, "failure_handler", MagicMock())

        top_pipeline = PipelineObject(nodes={self.node_id: node})
        process = MockPipelineProcess(top_pipeline=top_pipeline)
        status = MockStatus()
        old_version = status.version
        kill = True
        ex_data = "ex_data"

        with patch(PIPELINE_STATUS_GET, MagicMock(return_value=status)):
            with patch(PIPELINE_PROCESS_GET, MagicMock(return_value=process)):
                act_result = api.forced_fail(self.node_id, kill, ex_data)

                self.assertTrue(act_result.result)

                node.failure_handler.assert_called_once_with(process.root_pipeline.data)

                ScheduleService.objects.delete_schedule.assert_called_once_with(status.id, old_version)

                Data.objects.forced_fail.assert_called_once_with(self.node_id, ex_data)

                ProcessCeleryTask.objects.revoke.assert_called_once_with(process.id, kill)

                process.adjust_status.assert_called_once()

                self.assertTrue(process.is_sleep)

                process.save.assert_called_once()

                self.assertNotEqual(old_version, status.version)

                status.save.assert_called_once()
