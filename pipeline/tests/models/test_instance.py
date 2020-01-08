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

from __future__ import absolute_import

from django.test import TestCase

from pipeline.tests.mock import *  # noqa
from pipeline.tests.mock_settings import *  # noqa
from pipeline.engine import states
from pipeline.service import task_service
from pipeline.engine.utils import ActionResult
from pipeline.models import PipelineInstance, PipelineTemplate
from pipeline.engine.models import Status, NodeRelationship


class TestPipelineInstance(TestCase):
    def setUp(self):
        self.data = {
            u'activities': {u'node8fe2bb234d29860981a2bc7e6077': {u'can_retry': True,
                                                                  u'component': {u'code': u'sleep_timer',
                                                                                 u'data': {u'bk_timing': {
                                                                                     u'hook': False,
                                                                                     u'value': u'3'}}},
                                                                  u'error_ignorable': False,
                                                                  u'id': u'node8fe2bb234d29860981a2bc7e6077',
                                                                  u'incoming': u'line67b0e8cc895b1b9f9e0413dc50d1',
                                                                  u'isSkipped': True,
                                                                  u'loop': None,
                                                                  u'name': u'\u5b9a\u65f6',
                                                                  u'optional': False,
                                                                  u'outgoing': u'line73943da9f6f17601a40dc46bd229',
                                                                  u'stage_name': u'\u6b65\u9aa41',
                                                                  u'type': u'ServiceActivity'}},
            u'constants': {u'${ip}': {u'custom_type': u'input',
                                      u'desc': u'',
                                      u'index': 0,
                                      u'key': u'${ip}',
                                      u'name': u'ip',
                                      u'show_type': u'show',
                                      u'source_info': {},
                                      u'source_tag': u'',
                                      u'source_type': u'custom',
                                      u'validation': u'^.+$',
                                      u'validator': [],
                                      u'value': u''}},
            u'end_event': {u'id': u'nodeade2061fe6e69dc5b64a588480a7',
                           u'incoming': u'line73943da9f6f17601a40dc46bd229',
                           u'name': u'',
                           u'outgoing': u'',
                           u'type': u'EmptyEndEvent'},
            u'flows': {u'line67b0e8cc895b1b9f9e0413dc50d1': {u'id': u'line67b0e8cc895b1b9f9e0413dc50d1',
                                                             u'is_default': False,
                                                             u'source': u'nodedee24d10226c975f4d2c659cc29d',
                                                             u'target': u'node8fe2bb234d29860981a2bc7e6077'},
                       u'line73943da9f6f17601a40dc46bd229': {u'id': u'line73943da9f6f17601a40dc46bd229',
                                                             u'is_default': False,
                                                             u'source': u'node8fe2bb234d29860981a2bc7e6077',
                                                             u'target': u'nodeade2061fe6e69dc5b64a588480a7'}},
            u'gateways': {},
            u'outputs': [],
            u'start_event': {u'id': u'nodedee24d10226c975f4d2c659cc29d',
                             u'incoming': u'',
                             u'name': u'',
                             u'outgoing': u'line67b0e8cc895b1b9f9e0413dc50d1',
                             u'type': u'EmptyStartEvent'}}
        self.creator = 'start'
        self.template = PipelineTemplate.objects.create_model(self.data, creator=self.creator, template_id='1')
        self.instance = PipelineInstance.objects.create_instance(self.template, exec_data=self.data,
                                                                 creator=self.creator, instance_id='1')
        self.instance_2 = PipelineInstance.objects.create_instance(self.template, exec_data=self.data,
                                                                   creator=self.creator, instance_id='2')
        self.instance_3 = PipelineInstance.objects.create_instance(self.template, exec_data=self.data,
                                                                   creator=self.creator, instance_id='3')

    @mock.patch('pipeline.models.PipelineTemplate.objects.unfold_subprocess', mock.MagicMock())
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
        PipelineInstance.objects.create_instance(self.template, exec_data=self.data,
                                                 creator=self.creator, instance_id='1')

        PipelineTemplate.objects.unfold_subprocess.assert_called_with(self.data)

        PipelineTemplate.objects.unfold_subprocess.reset_mock()

        PipelineInstance.objects.create_instance(self.template, exec_data=self.data,
                                                 creator=self.creator, instance_id='1', spread=True)

        PipelineTemplate.objects.unfold_subprocess.assert_not_called()

    def test_set_started(self):
        PipelineInstance.objects.set_started(self.instance.instance_id, self.creator)
        self.instance.refresh_from_db()
        self.assertTrue(self.instance.is_started)

    def test_set_finished(self):
        NodeRelationship.objects.build_relationship(self.instance.instance_id, self.instance.instance_id)
        Status.objects.create(id=self.instance.instance_id, state=states.FINISHED)
        for act_id in self.data[u'activities']:
            NodeRelationship.objects.build_relationship(self.instance.instance_id, act_id)
            Status.objects.create(id=act_id, state=states.FINISHED)
        NodeRelationship.objects.build_relationship(self.instance.instance_id, self.data[u'start_event']['id'])
        Status.objects.create(id=self.data[u'start_event']['id'], state=states.FINISHED)
        NodeRelationship.objects.build_relationship(self.instance.instance_id, self.data[u'end_event']['id'])
        Status.objects.create(id=self.data[u'end_event']['id'], state=states.FINISHED)
        print '###############################'
        print NodeRelationship.objects.filter(ancestor_id=self.instance.instance_id, distance__lte=99)
        PipelineInstance.objects.set_finished(self.instance.instance_id)

        self.instance.refresh_from_db()
        self.assertTrue(self.instance.is_finished)

    def test_delete_instance(self):
        PipelineInstance.objects.delete_model(self.instance.instance_id)
        i = PipelineInstance.objects.get(instance_id=self.instance.instance_id)
        self.assertTrue(i.is_deleted)
        PipelineInstance.objects.delete_model([self.instance_2.instance_id, self.instance_3.instance_id])
        i2 = PipelineInstance.objects.get(instance_id=self.instance_2.instance_id)
        i3 = PipelineInstance.objects.get(instance_id=self.instance_3.instance_id)
        self.assertTrue(i2.is_deleted)
        self.assertTrue(i3.is_deleted)

    @patch(PIPELINE_MODELS_TASK_SERVICE_RUN_PIPELINE, MagicMock(return_value=ActionResult(result=True, message='')))
    @patch(PIPELINE_PIPELINE_INSTANCE_CALCULATE_TREE_INFO, MagicMock())
    @patch(PIPELINE_PIPELINE_INSTANCE_IMPORT_STRING, MagicMock(retrun_value=MockParser))
    def test_start__success(self):
        instance = PipelineInstance.objects.create_instance(self.template, exec_data=self.data, creator=self.creator)
        executor = 'token_1'
        instance.start(executor)

        instance.refresh_from_db()

        instance.calculate_tree_info.assert_called_once()
        self.assertTrue(instance.is_started)
        self.assertEqual(instance.executor, executor)
        self.assertIsNotNone(instance.start_time)

        task_service.run_pipeline.assert_called_once()

    @patch(PIPELINE_MODELS_TASK_SERVICE_RUN_PIPELINE, MagicMock(return_value=ActionResult(result=False, message='')))
    @patch(PIPELINE_PIPELINE_INSTANCE_CALCULATE_TREE_INFO, MagicMock())
    def test_start__already_started(self):
        instance = PipelineInstance.objects.create_instance(self.template, exec_data=self.data, creator=self.creator)
        instance.is_started = True
        instance.save()
        executor = 'token_1'

        instance.start(executor)

        instance.calculate_tree_info.assert_not_called()
        task_service.run_pipeline.assert_not_called()

    @patch(PIPELINE_MODELS_TASK_SERVICE_RUN_PIPELINE, MagicMock(return_value=ActionResult(result=False, message='')))
    @patch(PIPELINE_PIPELINE_INSTANCE_CALCULATE_TREE_INFO, MagicMock())
    @patch(PIPELINE_PIPELINE_INSTANCE_IMPORT_STRING, MagicMock(side_effect=ImportError()))
    def test_start__parser_cls_error(self):
        instance = PipelineInstance.objects.create_instance(self.template, exec_data=self.data, creator=self.creator)
        executor = 'token_1'

        instance.start(executor)

        instance.refresh_from_db()

        self.assertFalse(instance.is_started)
        self.assertEqual(instance.executor, '')
        self.assertIsNone(instance.start_time)

        instance.calculate_tree_info.assert_not_called()
        task_service.run_pipeline.assert_not_called()

    @patch(PIPELINE_MODELS_TASK_SERVICE_RUN_PIPELINE, MagicMock(return_value=ActionResult(result=False, message='')))
    @patch(PIPELINE_PIPELINE_INSTANCE_CALCULATE_TREE_INFO, MagicMock())
    @patch(PIPELINE_PIPELINE_INSTANCE_IMPORT_STRING, MagicMock(retrun_value=MockParser))
    def test_start__task_service_call_fail(self):
        instance = PipelineInstance.objects.create_instance(self.template, exec_data=self.data, creator=self.creator)
        executor = 'token_1'
        instance.start(executor)

        instance.refresh_from_db()

        instance.calculate_tree_info.assert_called_once()
        task_service.run_pipeline.assert_called_once()

        self.assertFalse(instance.is_started)
        self.assertEqual(instance.executor, '')
        self.assertIsNone(instance.start_time)

    @patch(PIPELINE_MODELS_TASK_SERVICE_RUN_PIPELINE, MagicMock(return_value=ActionResult(result=False, message='')))
    @patch(PIPELINE_PIPELINE_INSTANCE_CALCULATE_TREE_INFO, MagicMock(side_effect=Exception()))
    def test_start__error_occurred_before_task_service_call(self):
        instance = PipelineInstance.objects.create_instance(self.template, exec_data=self.data, creator=self.creator)
        executor = 'token_1'

        try:
            instance.start(executor)
        except Exception:
            pass

        instance.refresh_from_db()

        self.assertFalse(instance.is_started)
        self.assertEqual(instance.executor, '')
        self.assertIsNone(instance.start_time)

        task_service.run_pipeline.assert_not_called()
