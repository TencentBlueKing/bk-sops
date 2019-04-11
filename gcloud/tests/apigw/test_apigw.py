# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from __future__ import absolute_import

import copy
import json
import logging
import jsonschema

from django.test import TestCase, Client

from pipeline.exceptions import PipelineException

from gcloud.core.utils import strftime_with_timezone
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.commons.template.models import CommonTemplate
from gcloud.periodictask.models import PeriodicTask

from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa

logger = logging.getLogger('root')


def dummy_params_wrapper(perm):
    def inner_dummy_wrapper(func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return inner_dummy_wrapper


def dummy_wrapper(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


TEST_BIZ_CC_ID = '123'  # do not change this to non number
TEST_BIZ_CC_NAME = 'biz name'
TEST_APP_CODE = 'app_code'
TEST_TEMPLATE_ID = '1'  # do not change this to non number
TEST_TASKFLOW_ID = '2'  # do not change this to non number
TEST_TASKFLOW_URL = 'url'
TEST_TASKFLOW_PIPELINE_TREE = 'pipeline_tree'
TEST_PERIODIC_TASK_ID = '3'  # do not change to this non number
TEST_DATA = 'data'
TEST_NODE_ID = 'node_id'
TEST_CALLBACK_DATA = 'callback_data'
TEST_COMPONENT_CODE = 'component_code'
TEST_SUBPROCESS_STACK = '[1, 2, 3]'


class APITest(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.GET_TEMPLATE_LIST_URL = '/apigw/get_template_list/{biz_cc_id}/'
        cls.GET_TEMPLATE_INFO_URL = '/apigw/get_template_info/{template_id}/{bk_biz_id}/'
        cls.CREATE_TASK_URL = '/apigw/create_task/{template_id}/{bk_biz_id}/'
        cls.START_TASK_URL = '/apigw/start_task/{task_id}/{bk_biz_id}/'
        cls.OPERATE_TASK_URL = '/apigw/operate_task/{task_id}/{bk_biz_id}/'
        cls.GET_TASK_STATUS_URL = '/apigw/get_task_status/{task_id}/{bk_biz_id}/'
        cls.QUERY_TASK_COUNT_URL = '/apigw/query_task_count/{bk_biz_id}/'
        cls.GET_PERIODIC_TASK_LIST_URL = '/apigw/get_periodic_task_list/{bk_biz_id}/'
        cls.GET_PERIODIC_TASK_INFO_URL = '/apigw/get_periodic_task_info/{task_id}/{bk_biz_id}/'
        cls.CREATE_PERIODIC_TASK_URL = '/apigw/create_periodic_task/{template_id}/{bk_biz_id}/'
        cls.SET_PERIODIC_TASK_ENABLED_URL = '/apigw/set_periodic_task_enabled/{task_id}/{bk_biz_id}/'
        cls.MODIFY_PERIODIC_TASK_CRON_URL = '/apigw/modify_cron_for_periodic_task/{task_id}/{bk_biz_id}/'
        cls.MODIFY_PERIODIC_TASK_CONSTANTS_URL = '/apigw/modify_constants_for_periodic_task/{task_id}/{bk_biz_id}/'
        cls.GET_TASK_DETAIL = '/apigw/get_task_detail/{task_id}/{bk_biz_id}/'
        cls.GET_TASK_NODE_DETAIL = '/apigw/get_task_node_detail/{task_id}/{bk_biz_id}/'
        cls.NODE_CALLBACK = '/apigw/node_callback/{task_id}/{bk_biz_id}/'

        super(APITest, cls).setUpClass()

    def setUp(self):
        self.white_list_patcher = mock.patch(APIGW_DECORATOR_CHECK_WHITE_LIST, MagicMock(return_value=True))

        self.dummy_user = MagicMock()
        self.dummy_user.username = ''
        self.user_cls = MagicMock()
        self.user_cls.objects = MagicMock()
        self.user_cls.objects.get_or_create = MagicMock(return_value=(self.dummy_user, False))

        self.get_user_model_patcher = mock.patch(APIGW_DECORATOR_GET_USER_MODEL, MagicMock(return_value=self.user_cls))
        self.prepare_user_business_patcher = mock.patch(APIGW_DECORATOR_PREPARE_USER_BUSINESS, MagicMock())
        self.business_exist_patcher = mock.patch(APIGW_DECORATOR_BUSINESS_EXIST, MagicMock(return_value=True))

        self.white_list_patcher.start()
        self.get_user_model_patcher.start()
        self.prepare_user_business_patcher.start()
        self.business_exist_patcher.start()

        self.client = Client()

    def tearDown(self):
        self.white_list_patcher.stop()
        self.get_user_model_patcher.stop()
        self.prepare_user_business_patcher.stop()
        self.business_exist_patcher.stop()

    @mock.patch(BUSINESS_GET, MagicMock(return_value=MockBusiness(cc_id=TEST_BIZ_CC_ID, cc_name=TEST_BIZ_CC_NAME)))
    def test_get_template_list__for_business_template(self):
        pt1 = MockPipelineTemplate(id=1,
                                   name='pt1')
        pt2 = MockPipelineTemplate(id=2,
                                   name='pt2')

        task_tmpl1 = MockTaskTemplate(id=1, pipeline_template=pt1)
        task_tmpl2 = MockTaskTemplate(id=2, pipeline_template=pt2)

        task_templates = [task_tmpl1, task_tmpl2]

        with mock.patch(TASKTEMPLATE_SELECT_RELATE, MagicMock(return_value=MockQuerySet(filter_result=task_templates))):
            assert_data = [
                {
                    'id': tmpl.id,
                    'name': tmpl.pipeline_template.name,
                    'creator': tmpl.pipeline_template.creator,
                    'create_time': strftime_with_timezone(tmpl.pipeline_template.create_time),
                    'editor': tmpl.pipeline_template.editor,
                    'edit_time': strftime_with_timezone(tmpl.pipeline_template.edit_time),
                    'category': tmpl.category,
                    'bk_biz_id': TEST_BIZ_CC_ID,
                    'bk_biz_name': TEST_BIZ_CC_NAME
                } for tmpl in task_templates
            ]

            response = self.client.get(path=self.GET_TEMPLATE_LIST_URL.format(biz_cc_id=TEST_BIZ_CC_ID))

            self.assertEqual(response.status_code, 200)

            data = json.loads(response.content)

            self.assertTrue(data['result'])
            self.assertEqual(data['data'], assert_data)

        with mock.patch(TASKTEMPLATE_SELECT_RELATE, MagicMock(return_value=MockQuerySet(filter_result=[]))):
            assert_data = []

            response = self.client.get(path=self.GET_TEMPLATE_LIST_URL.format(biz_cc_id=TEST_BIZ_CC_ID))

            data = json.loads(response.content)

            self.assertTrue(data['result'])
            self.assertEqual(data['data'], assert_data)

    @mock.patch(BUSINESS_GET, MagicMock(return_value=MockBusiness(cc_id=TEST_BIZ_CC_ID, cc_name=TEST_BIZ_CC_NAME)))
    def test_get_template_list__for_common_template(self):
        pt1 = MockPipelineTemplate(id=1,
                                   name='pt1')
        pt2 = MockPipelineTemplate(id=2,
                                   name='pt2')

        task_tmpl1 = MockCommonTemplate(id=1, pipeline_template=pt1)
        task_tmpl2 = MockCommonTemplate(id=2, pipeline_template=pt2)

        task_templates = [task_tmpl1, task_tmpl2]

        with mock.patch(COMMONTEMPLATE_SELECT_RELATE, MagicMock(
                return_value=MockQuerySet(filter_result=task_templates))):
            assert_data = [
                {
                    'id': tmpl.id,
                    'name': tmpl.pipeline_template.name,
                    'creator': tmpl.pipeline_template.creator,
                    'create_time': strftime_with_timezone(tmpl.pipeline_template.create_time),
                    'editor': tmpl.pipeline_template.editor,
                    'edit_time': strftime_with_timezone(tmpl.pipeline_template.edit_time),
                    'category': tmpl.category,
                    'bk_biz_id': TEST_BIZ_CC_ID,
                    'bk_biz_name': TEST_BIZ_CC_NAME
                } for tmpl in task_templates
            ]

            response = self.client.get(path=self.GET_TEMPLATE_LIST_URL.format(biz_cc_id=TEST_BIZ_CC_ID),
                                       data={'template_source': 'common'})

            self.assertEqual(response.status_code, 200)

            data = json.loads(response.content)

            self.assertTrue(data['result'])
            self.assertEqual(data['data'], assert_data)

        with mock.patch(COMMONTEMPLATE_SELECT_RELATE, MagicMock(return_value=MockQuerySet(filter_result=[]))):
            assert_data = []

            response = self.client.get(path=self.GET_TEMPLATE_LIST_URL.format(biz_cc_id=TEST_BIZ_CC_ID),
                                       data={'template_source': 'common'})

            data = json.loads(response.content)

            self.assertTrue(data['result'])
            self.assertEqual(data['data'], assert_data)

    @mock.patch(BUSINESS_GET, MagicMock(return_value=MockBusiness(cc_id=TEST_BIZ_CC_ID, cc_name=TEST_BIZ_CC_NAME)))
    def test_get_template_info__for_business_template(self):
        pt1 = MockPipelineTemplate(id=1,
                                   name='pt1')

        tmpl = MockTaskTemplate(id=1, pipeline_template=pt1)

        with mock.patch(TASKTEMPLATE_SELECT_RELATE, MagicMock(return_value=MockQuerySet(get_result=tmpl))):
            pipeline_tree = copy.deepcopy(tmpl.pipeline_tree)
            pipeline_tree.pop('line')
            pipeline_tree.pop('location')
            assert_data = {
                'id': tmpl.id,
                'name': tmpl.pipeline_template.name,
                'creator': tmpl.pipeline_template.creator,
                'create_time': strftime_with_timezone(tmpl.pipeline_template.create_time),
                'editor': tmpl.pipeline_template.editor,
                'edit_time': strftime_with_timezone(tmpl.pipeline_template.edit_time),
                'category': tmpl.category,
                'bk_biz_id': TEST_BIZ_CC_ID,
                'bk_biz_name': TEST_BIZ_CC_NAME,
                'pipeline_tree': pipeline_tree
            }

            response = self.client.get(path=self.GET_TEMPLATE_INFO_URL.format(template_id=TEST_TEMPLATE_ID,
                                                                              bk_biz_id=TEST_BIZ_CC_ID))

            data = json.loads(response.content)

            self.assertTrue(data['result'])
            self.assertEqual(assert_data, data['data'])

    @mock.patch(TASKTEMPLATE_SELECT_RELATE,
                MagicMock(return_value=MockQuerySet(get_raise=TaskTemplate.DoesNotExist())))
    @mock.patch(BUSINESS_GET, MagicMock(return_value=MockBusiness(cc_id=TEST_BIZ_CC_ID, cc_name=TEST_BIZ_CC_NAME)))
    def test_get_template_info__for_business_template_does_not_exists(self):
        response = self.client.get(path=self.GET_TEMPLATE_INFO_URL.format(template_id=TEST_TEMPLATE_ID,
                                                                          bk_biz_id=TEST_BIZ_CC_ID), )

        data = json.loads(response.content)

        self.assertFalse(data['result'])
        self.assertTrue('message' in data)

    @mock.patch(BUSINESS_GET, MagicMock(return_value=MockBusiness(cc_id=TEST_BIZ_CC_ID, cc_name=TEST_BIZ_CC_NAME)))
    def test_get_template_info__for_common_template(self):
        pt1 = MockPipelineTemplate(id=1,
                                   name='pt1')

        tmpl = MockCommonTemplate(id=1, pipeline_template=pt1)

        with mock.patch(COMMONTEMPLATE_SELECT_RELATE, MagicMock(return_value=MockQuerySet(get_result=tmpl))):
            pipeline_tree = copy.deepcopy(tmpl.pipeline_tree)
            pipeline_tree.pop('line')
            pipeline_tree.pop('location')
            assert_data = {
                'id': tmpl.id,
                'name': tmpl.pipeline_template.name,
                'creator': tmpl.pipeline_template.creator,
                'create_time': strftime_with_timezone(tmpl.pipeline_template.create_time),
                'editor': tmpl.pipeline_template.editor,
                'edit_time': strftime_with_timezone(tmpl.pipeline_template.edit_time),
                'category': tmpl.category,
                'bk_biz_id': TEST_BIZ_CC_ID,
                'bk_biz_name': TEST_BIZ_CC_NAME,
                'pipeline_tree': pipeline_tree
            }

            response = self.client.get(path=self.GET_TEMPLATE_INFO_URL.format(template_id=TEST_TEMPLATE_ID,
                                                                              bk_biz_id=TEST_BIZ_CC_ID),
                                       data={'template_source': 'common'})

            data = json.loads(response.content)

            self.assertTrue(data['result'])
            self.assertEqual(assert_data, data['data'])

    @mock.patch(COMMONTEMPLATE_SELECT_RELATE,
                MagicMock(return_value=MockQuerySet(get_raise=CommonTemplate.DoesNotExist())))
    @mock.patch(BUSINESS_GET, MagicMock(return_value=MockBusiness(cc_id=TEST_BIZ_CC_ID, cc_name=TEST_BIZ_CC_NAME)))
    def test_get_template_info__for_common_template_does_not_exists(self):
        response = self.client.get(path=self.GET_TEMPLATE_INFO_URL.format(template_id=TEST_TEMPLATE_ID,
                                                                          bk_biz_id=TEST_BIZ_CC_ID),
                                   data={'template_source': 'common'})

        data = json.loads(response.content)

        self.assertFalse(data['result'])
        self.assertTrue('message' in data)

    @mock.patch(TASKINSTANCE_CREATE_PIPELINE, MagicMock(return_value=(True, TEST_DATA)))
    @mock.patch(TASKINSTANCE_CREATE, MagicMock(return_value=MockTaskFlowInstance(id=TEST_TASKFLOW_ID)))
    @mock.patch(APIGW_VIEW_JSON_SCHEMA_VALIDATE, MagicMock())
    def test_create_task__success(self):
        pt1 = MockPipelineTemplate(id=1, name='pt1')

        tmpl = MockTaskTemplate(id=1, pipeline_template=pt1)
        biz = MockBusiness(cc_id=TEST_BIZ_CC_ID, cc_name=TEST_BIZ_CC_NAME)

        with mock.patch(BUSINESS_GET, MagicMock(return_value=biz)):
            with mock.patch(TASKTEMPLATE_SELECT_RELATE, MagicMock(return_value=MockQuerySet(get_result=tmpl))):
                assert_data = {'task_id': TEST_TASKFLOW_ID,
                               'task_url': TEST_TASKFLOW_URL,
                               'pipeline_tree': TEST_TASKFLOW_PIPELINE_TREE}
                response = self.client.post(path=self.CREATE_TASK_URL.format(template_id=TEST_TEMPLATE_ID,
                                                                             bk_biz_id=TEST_BIZ_CC_ID),
                                            data=json.dumps({'name': 'name',
                                                             'constants': 'constants',
                                                             'exclude_task_nodes_id': 'exclude_task_nodes_id',
                                                             'flow_type': 'common'}),
                                            content_type="application/json",
                                            HTTP_BK_APP_CODE=TEST_APP_CODE)

                TaskFlowInstance.objects.create_pipeline_instance_exclude_task_nodes.assert_called_once_with(
                    tmpl,
                    {'name': 'name', 'creator': ''},
                    'constants',
                    'exclude_task_nodes_id')

                TaskFlowInstance.objects.create.assert_called_once_with(
                    business=biz,
                    category=tmpl.category,
                    pipeline_instance=TEST_DATA,
                    template_id=TEST_TEMPLATE_ID,
                    create_method='api',
                    create_info=TEST_APP_CODE,
                    flow_type='common',
                    current_flow='execute_task'
                )

                data = json.loads(response.content)

                self.assertTrue(data['result'])
                self.assertEqual(data['data'], assert_data)

                TaskFlowInstance.objects.create_pipeline_instance_exclude_task_nodes.reset_mock()
                TaskFlowInstance.objects.create.reset_mock()

            pt1 = MockPipelineTemplate(id=1,
                                       name='pt1')

            tmpl = MockCommonTemplate(id=1, pipeline_template=pt1)

            with mock.patch(COMMONTEMPLATE_SELECT_RELATE, MagicMock(return_value=MockQuerySet(get_result=tmpl))):
                assert_data = {'task_id': TEST_TASKFLOW_ID,
                               'task_url': TEST_TASKFLOW_URL,
                               'pipeline_tree': TEST_TASKFLOW_PIPELINE_TREE}
                response = self.client.post(path=self.CREATE_TASK_URL.format(template_id=TEST_TEMPLATE_ID,
                                                                             bk_biz_id=TEST_BIZ_CC_ID),
                                            data=json.dumps({'name': 'name',
                                                             'constants': 'constants',
                                                             'exclude_task_nodes_id': 'exclude_task_nodes_id',
                                                             'template_source': 'common',
                                                             'flow_type': 'common'}),
                                            content_type="application/json",
                                            HTTP_BK_APP_CODE=TEST_APP_CODE)

                TaskFlowInstance.objects.create_pipeline_instance_exclude_task_nodes.assert_called_once_with(
                    tmpl,
                    {'name': 'name', 'creator': ''},
                    'constants',
                    'exclude_task_nodes_id')

                TaskFlowInstance.objects.create.assert_called_once_with(
                    business=biz,
                    category=tmpl.category,
                    pipeline_instance=TEST_DATA,
                    template_id=TEST_TEMPLATE_ID,
                    create_method='api',
                    create_info=TEST_APP_CODE,
                    flow_type='common',
                    current_flow='execute_task'
                )

                data = json.loads(response.content)

                self.assertTrue(data['result'])
                self.assertEqual(data['data'], assert_data)

    @mock.patch(BUSINESS_GET, MagicMock(return_value=MockBusiness(cc_id=TEST_BIZ_CC_ID, cc_name=TEST_BIZ_CC_NAME)))
    @mock.patch(TASKTEMPLATE_SELECT_RELATE, MagicMock(return_value=MockQuerySet()))
    @mock.patch(COMMONTEMPLATE_SELECT_RELATE, MagicMock(return_value=MockQuerySet()))
    @mock.patch(APIGW_VIEW_JSON_SCHEMA_VALIDATE, MagicMock(side_effect=jsonschema.ValidationError('')))
    def test_create_task__validate_fail(self):
        response = self.client.post(path=self.CREATE_TASK_URL.format(template_id=TEST_TEMPLATE_ID,
                                                                     bk_biz_id=TEST_BIZ_CC_ID),
                                    data=json.dumps({'constants': 'constants',
                                                     'exclude_task_node_id': 'exclude_task_node_id'}),
                                    content_type="application/json")

        data = json.loads(response.content)

        self.assertFalse(data['result'])
        self.assertTrue('message' in data)

        response = self.client.post(path=self.CREATE_TASK_URL.format(template_id=TEST_TEMPLATE_ID,
                                                                     bk_biz_id=TEST_BIZ_CC_ID),
                                    data=json.dumps({'constants': 'constants',
                                                     'exclude_task_node_id': 'exclude_task_node_id',
                                                     'template_source': 'common'}),
                                    content_type="application/json")

        data = json.loads(response.content)

        self.assertFalse(data['result'])
        self.assertTrue('message' in data)

    @mock.patch(BUSINESS_GET, MagicMock(return_value=MockBusiness(cc_id=TEST_BIZ_CC_ID, cc_name=TEST_BIZ_CC_NAME)))
    @mock.patch(TASKTEMPLATE_SELECT_RELATE, MagicMock(return_value=MockQuerySet()))
    @mock.patch(COMMONTEMPLATE_SELECT_RELATE, MagicMock(return_value=MockQuerySet()))
    @mock.patch(APIGW_VIEW_JSON_SCHEMA_VALIDATE, MagicMock())
    def test_create_task__without_app_code(self):
        response = self.client.post(path=self.CREATE_TASK_URL.format(template_id=TEST_TEMPLATE_ID,
                                                                     bk_biz_id=TEST_BIZ_CC_ID),
                                    data=json.dumps({'constants': 'constants',
                                                     'exclude_task_node_id': 'exclude_task_node_id'}),
                                    content_type="application/json")

        data = json.loads(response.content)

        self.assertFalse(data['result'])
        self.assertTrue('message' in data)

        response = self.client.post(path=self.CREATE_TASK_URL.format(template_id=TEST_TEMPLATE_ID,
                                                                     bk_biz_id=TEST_BIZ_CC_ID),
                                    data=json.dumps({'constants': 'constants',
                                                     'exclude_task_node_id': 'exclude_task_node_id',
                                                     'template_source': 'common'}),
                                    content_type="application/json")

        data = json.loads(response.content)

        self.assertFalse(data['result'])
        self.assertTrue('message' in data)

    @mock.patch(BUSINESS_GET, MagicMock(return_value=MockBusiness(cc_id=TEST_BIZ_CC_ID, cc_name=TEST_BIZ_CC_NAME)))
    @mock.patch(TASKINSTANCE_CREATE_PIPELINE, MagicMock(side_effect=PipelineException()))
    @mock.patch(APIGW_VIEW_JSON_SCHEMA_VALIDATE, MagicMock())
    def test_create_task__create_pipeline_raise(self):
        pt1 = MockPipelineTemplate(id=1,
                                   name='pt1')

        tmpl = MockTaskTemplate(id=1, pipeline_template=pt1)

        with mock.patch(TASKTEMPLATE_SELECT_RELATE, MagicMock(return_value=MockQuerySet(get_result=tmpl))):
            response = self.client.post(path=self.CREATE_TASK_URL.format(template_id=TEST_TEMPLATE_ID,
                                                                         bk_biz_id=TEST_BIZ_CC_ID),
                                        data=json.dumps({'name': 'name',
                                                         'constants': 'constants',
                                                         'exclude_task_node_id': 'exclude_task_node_id'}),
                                        content_type="application/json",
                                        HTTP_BK_APP_CODE=TEST_APP_CODE)

            data = json.loads(response.content)

            self.assertFalse(data['result'])
            self.assertTrue('message' in data)

        pt1 = MockPipelineTemplate(id=1,
                                   name='pt1')

        tmpl = MockCommonTemplate(id=1, pipeline_template=pt1)

        with mock.patch(COMMONTEMPLATE_SELECT_RELATE, MagicMock(return_value=MockQuerySet(get_result=tmpl))):
            response = self.client.post(path=self.CREATE_TASK_URL.format(template_id=TEST_TEMPLATE_ID,
                                                                         bk_biz_id=TEST_BIZ_CC_ID),
                                        data=json.dumps({'name': 'name',
                                                         'constants': 'constants',
                                                         'exclude_task_node_id': 'exclude_task_node_id',
                                                         'template_source': 'common'}),
                                        content_type="application/json",
                                        HTTP_BK_APP_CODE=TEST_APP_CODE)

            data = json.loads(response.content)

            self.assertFalse(data['result'])
            self.assertTrue('message' in data)

    @mock.patch(BUSINESS_GET, MagicMock(return_value=MockBusiness(cc_id=TEST_BIZ_CC_ID, cc_name=TEST_BIZ_CC_NAME)))
    @mock.patch(TASKINSTANCE_CREATE_PIPELINE, MagicMock(return_value=(False, '')))
    @mock.patch(APIGW_VIEW_JSON_SCHEMA_VALIDATE, MagicMock())
    def test_create_task__create_pipeline_fail(self):
        pt1 = MockPipelineTemplate(id=1,
                                   name='pt1')

        tmpl = MockTaskTemplate(id=1, pipeline_template=pt1)

        with mock.patch(TASKTEMPLATE_SELECT_RELATE, MagicMock(return_value=MockQuerySet(get_result=tmpl))):
            response = self.client.post(path=self.CREATE_TASK_URL.format(template_id=TEST_TEMPLATE_ID,
                                                                         bk_biz_id=TEST_BIZ_CC_ID),
                                        data=json.dumps({'name': 'name',
                                                         'constants': 'constants',
                                                         'exclude_task_node_id': 'exclude_task_node_id'}),
                                        content_type="application/json",
                                        HTTP_BK_APP_CODE=TEST_APP_CODE)

            data = json.loads(response.content)

            self.assertFalse(data['result'])
            self.assertTrue('message' in data)

        pt1 = MockPipelineTemplate(id=1,
                                   name='pt1')

        tmpl = MockCommonTemplate(id=1, pipeline_template=pt1)

        with mock.patch(COMMONTEMPLATE_SELECT_RELATE, MagicMock(return_value=MockQuerySet(get_result=tmpl))):
            response = self.client.post(path=self.CREATE_TASK_URL.format(template_id=TEST_TEMPLATE_ID,
                                                                         bk_biz_id=TEST_BIZ_CC_ID),
                                        data=json.dumps({'name': 'name',
                                                         'constants': 'constants',
                                                         'exclude_task_node_id': 'exclude_task_node_id',
                                                         'template_source': 'common'}),
                                        content_type="application/json",
                                        HTTP_BK_APP_CODE=TEST_APP_CODE)

            data = json.loads(response.content)

            self.assertFalse(data['result'])
            self.assertTrue('message' in data)

    def test_start_task(self):
        assert_return = {'result': True}
        task = MockTaskFlowInstance(task_action_return=assert_return)

        with mock.patch(TASKINSTANCE_GET, MagicMock(return_value=task)):
            response = self.client.post(path=self.START_TASK_URL.format(task_id=TEST_TASKFLOW_ID,
                                                                        bk_biz_id=TEST_BIZ_CC_ID))

            task.task_action.assert_called_once_with('start', '')

            data = json.loads(response.content)

            self.assertEqual(data, assert_return)

    def test_operate_task(self):
        assert_return = {'result': True}
        assert_action = 'any_action'
        task = MockTaskFlowInstance(task_action_return=assert_return)

        with mock.patch(TASKINSTANCE_GET, MagicMock(return_value=task)):
            response = self.client.post(path=self.OPERATE_TASK_URL.format(task_id=TEST_TASKFLOW_ID,
                                                                          bk_biz_id=TEST_BIZ_CC_ID),
                                        data=json.dumps({'action': assert_action}),
                                        content_type='application/json')

            task.task_action.assert_called_once_with(assert_action, '')

            data = json.loads(response.content)

            self.assertEqual(data, assert_return)

    def test_get_task_status__success(self):
        task = MockTaskFlowInstance(get_status_return=TEST_DATA)

        with mock.patch(TASKINSTANCE_GET, MagicMock(return_value=task)):
            response = self.client.get(path=self.GET_TASK_STATUS_URL.format(task_id=TEST_TASKFLOW_ID,
                                                                            bk_biz_id=TEST_BIZ_CC_ID))

            data = json.loads(response.content)
            self.assertTrue(data['result'])
            self.assertEqual(data['data'], TEST_DATA)

    def test_get_task_status__raise(self):
        task = MockTaskFlowInstance(get_status_raise=Exception())

        with mock.patch(TASKINSTANCE_GET, MagicMock(return_value=task)):
            response = self.client.get(path=self.GET_TASK_STATUS_URL.format(task_id=TEST_TASKFLOW_ID,
                                                                            bk_biz_id=TEST_BIZ_CC_ID))

            data = json.loads(response.content)
            self.assertFalse(data['result'])
            self.assertTrue('message' in data)

    @mock.patch(TASKINSTANCE_FORMAT_STATUS, MagicMock())
    @mock.patch(APIGW_VIEW_PIPELINE_API_GET_STATUS_TREE, MagicMock(return_value=TEST_DATA))
    def test_get_task_status__is_subprocess(self):
        task = MockTaskFlowInstance(get_status_raise=TaskFlowInstance.DoesNotExist())

        with mock.patch(TASKINSTANCE_GET, MagicMock(return_value=task)):
            response = self.client.get(path=self.GET_TASK_STATUS_URL.format(task_id=TEST_TASKFLOW_ID,
                                                                            bk_biz_id=TEST_BIZ_CC_ID))

            TaskFlowInstance.format_pipeline_status.assert_called_once_with(TEST_DATA)

            data = json.loads(response.content)
            self.assertTrue(data['result'])
            self.assertEqual(data['data'], TEST_DATA)

    @mock.patch(APIGW_VIEW_PIPELINE_API_GET_STATUS_TREE, MagicMock(return_value=TEST_DATA))
    def test_get_task_status__is_subprocess_raise(self):
        task = MockTaskFlowInstance(get_status_raise=TaskFlowInstance.DoesNotExist())

        with mock.patch(TASKINSTANCE_GET, MagicMock(return_value=task)):
            with mock.patch(APIGW_VIEW_PIPELINE_API_GET_STATUS_TREE, MagicMock(side_effect=Exception())):
                response = self.client.get(path=self.GET_TASK_STATUS_URL.format(task_id=TEST_TASKFLOW_ID,
                                                                                bk_biz_id=TEST_BIZ_CC_ID))

                data = json.loads(response.content)
                self.assertFalse(data['result'])
                self.assertTrue('message' in data)

            with mock.patch(TASKINSTANCE_FORMAT_STATUS, MagicMock(side_effect=Exception())):
                response = self.client.get(path=self.GET_TASK_STATUS_URL.format(task_id=TEST_TASKFLOW_ID,
                                                                                bk_biz_id=TEST_BIZ_CC_ID))

                data = json.loads(response.content)
                self.assertFalse(data['result'])
                self.assertTrue('message' in data)

    @mock.patch(TASKINSTANCE_EXTEN_CLASSIFIED_COUNT, MagicMock(return_value=(True, TEST_DATA)))
    def test_query_task_count__success(self):
        response = self.client.post(path=self.QUERY_TASK_COUNT_URL.format(bk_biz_id=TEST_BIZ_CC_ID),
                                    data=json.dumps({'group_by': 'category'}),
                                    content_type='application/json')

        data = json.loads(response.content)
        self.assertTrue(data['result'])
        self.assertEqual(data['data'], TEST_DATA)

    def test_query_task_count__conditions_is_not_dict(self):
        response = self.client.post(path=self.QUERY_TASK_COUNT_URL.format(bk_biz_id=TEST_BIZ_CC_ID),
                                    data=json.dumps({'conditions': []}),
                                    content_type='application/json')

        data = json.loads(response.content)
        self.assertFalse(data['result'])
        self.assertTrue('message' in data)

    def test_query_task_count__group_by_is_not_valid(self):
        response = self.client.post(path=self.QUERY_TASK_COUNT_URL.format(bk_biz_id=TEST_BIZ_CC_ID),
                                    data=json.dumps({'group_by': 'invalid_value'}),
                                    content_type='application/json')

        data = json.loads(response.content)
        self.assertFalse(data['result'])
        self.assertTrue('message' in data)

    @mock.patch(TASKINSTANCE_EXTEN_CLASSIFIED_COUNT, MagicMock(return_value=(False, '')))
    def test_query_task_count__extend_classified_count_fail(self):
        response = self.client.post(path=self.QUERY_TASK_COUNT_URL.format(bk_biz_id=TEST_BIZ_CC_ID),
                                    data=json.dumps({'group_by': 'category'}),
                                    content_type='application/json')

        TaskFlowInstance.objects.extend_classified_count.assert_called_once_with('category',
                                                                                 {'business__cc_id': TEST_BIZ_CC_ID,
                                                                                  'is_deleted': False})

        data = json.loads(response.content)
        self.assertFalse(data['result'])
        self.assertTrue('message' in data)

    def test_get_periodic_task_list(self):
        pt1 = MockPeriodicTask(id='1')
        pt2 = MockPeriodicTask(id='2')
        pt3 = MockPeriodicTask(id='3')

        periodic_tasks = [pt1, pt2, pt3]

        assert_data = [{
            'id': task.id,
            'name': task.name,
            'template_id': task.template_id,
            'creator': task.creator,
            'cron': task.cron,
            'enabled': task.enabled,
            'last_run_at': strftime_with_timezone(task.last_run_at),
            'total_run_count': task.total_run_count,
        } for task in periodic_tasks]

        with mock.patch(PERIODIC_TASK_FILTER, MagicMock(return_value=periodic_tasks)):
            response = self.client.get(path=self.GET_PERIODIC_TASK_LIST_URL.format(bk_biz_id=TEST_BIZ_CC_ID))

            data = json.loads(response.content)

            self.assertTrue(data['result'])
            self.assertEqual(data['data'], assert_data)

    def test_get_periodic_task_info__success(self):
        task = MockPeriodicTask()
        assert_data = {
            'id': task.id,
            'name': task.name,
            'template_id': task.template_id,
            'creator': task.creator,
            'cron': task.cron,
            'enabled': task.enabled,
            'last_run_at': strftime_with_timezone(task.last_run_at),
            'total_run_count': task.total_run_count,
            'form': task.form,
            'pipeline_tree': task.pipeline_tree
        }

        with mock.patch(PERIODIC_TASK_GET, MagicMock(return_value=task)):
            response = self.client.get(path=self.GET_PERIODIC_TASK_INFO_URL.format(task_id=TEST_PERIODIC_TASK_ID,
                                                                                   bk_biz_id=TEST_BIZ_CC_ID))

            data = json.loads(response.content)

            self.assertTrue(data['result'])
            self.assertEqual(data['data'], assert_data)

    @mock.patch(PERIODIC_TASK_GET, MagicMock(side_effect=PeriodicTask.DoesNotExist))
    def test_periodic_task_info__task_does_not_exist(self):
        response = self.client.get(path=self.GET_PERIODIC_TASK_INFO_URL.format(task_id=TEST_PERIODIC_TASK_ID,
                                                                               bk_biz_id=TEST_BIZ_CC_ID))

        data = json.loads(response.content)

        self.assertFalse(data['result'])
        self.assertTrue('message' in data)

    @mock.patch(TASKINSTANCE_PREVIEW_TREE, MagicMock())
    @mock.patch(APIGW_VIEW_JSON_SCHEMA_VALIDATE, MagicMock())
    def test_create_periodic_task__success(self):
        task = MockPeriodicTask()
        assert_data = {
            'id': task.id,
            'name': task.name,
            'template_id': task.template_id,
            'creator': task.creator,
            'cron': task.cron,
            'enabled': task.enabled,
            'last_run_at': strftime_with_timezone(task.last_run_at),
            'total_run_count': task.total_run_count,
            'form': task.form,
            'pipeline_tree': task.pipeline_tree
        }
        biz = MockBusiness(cc_id=TEST_BIZ_CC_ID, cc_name=TEST_BIZ_CC_NAME)
        template = MockTaskTemplate()

        with mock.patch(TASKTEMPLATE_GET, MagicMock(return_value=template)):
            with mock.patch(BUSINESS_GET, MagicMock(return_value=biz)):
                with mock.patch(PERIODIC_TASK_CREATE, MagicMock(return_value=task)):
                    response = self.client.post(path=self.CREATE_PERIODIC_TASK_URL.format(template_id=TEST_TEMPLATE_ID,
                                                                                          bk_biz_id=TEST_BIZ_CC_ID),
                                                data=json.dumps({'name': task.name,
                                                                 'cron': task.cron,
                                                                 'exclude_task_nodes_id': 'exclude_task_nodes_id'}),
                                                content_type='application/json')

                    TaskFlowInstance.objects.preview_pipeline_tree_exclude_task_nodes.assert_called_with(
                        template.pipeline_tree,
                        'exclude_task_nodes_id'
                    )

                    PeriodicTask.objects.create.assert_called_once_with(
                        business=biz,
                        template=template,
                        name=task.name,
                        cron=task.cron,
                        pipeline_tree=template.pipeline_tree,
                        creator=''
                    )

                    data = json.loads(response.content)

                    self.assertTrue(data['result'])
                    self.assertEqual(data['data'], assert_data)

    @mock.patch(TASKTEMPLATE_GET, MagicMock(side_effect=TaskTemplate.DoesNotExist()))
    def test_create_periodic_task__template_does_not_exist(self):
        response = self.client.post(path=self.CREATE_PERIODIC_TASK_URL.format(template_id=TEST_TEMPLATE_ID,
                                                                              bk_biz_id=TEST_BIZ_CC_ID),
                                    content_type='application/json')

        data = json.loads(response.content)

        self.assertFalse(data['result'])
        self.assertTrue('message' in data)

    @mock.patch(TASKTEMPLATE_GET, MagicMock(return_value=MockTaskTemplate()))
    @mock.patch(APIGW_VIEW_JSON_SCHEMA_VALIDATE, MagicMock(side_effect=jsonschema.ValidationError('')))
    def test_create_periodic_task__params_validate_fail(self):
        response = self.client.post(path=self.CREATE_PERIODIC_TASK_URL.format(template_id=TEST_TEMPLATE_ID,
                                                                              bk_biz_id=TEST_BIZ_CC_ID),
                                    content_type='application/json')

        data = json.loads(response.content)

        self.assertFalse(data['result'])
        self.assertTrue('message' in data)

    @mock.patch(TASKTEMPLATE_GET, MagicMock(return_value=MockTaskTemplate()))
    @mock.patch(APIGW_VIEW_JSON_SCHEMA_VALIDATE, MagicMock())
    @mock.patch(TASKINSTANCE_PREVIEW_TREE, MagicMock(side_effect=Exception()))
    def test_create_periodic_task__preview_pipeline_fail(self):
        response = self.client.post(path=self.CREATE_PERIODIC_TASK_URL.format(template_id=TEST_TEMPLATE_ID,
                                                                              bk_biz_id=TEST_BIZ_CC_ID),
                                    content_type='application/json')

        data = json.loads(response.content)

        self.assertFalse(data['result'])
        self.assertTrue('message' in data)

    @mock.patch(BUSINESS_GET, MagicMock(return_value=MockBusiness(cc_id=TEST_BIZ_CC_ID, cc_name=TEST_BIZ_CC_NAME)))
    @mock.patch(TASKTEMPLATE_GET, MagicMock(return_value=MockTaskTemplate()))
    @mock.patch(APIGW_VIEW_JSON_SCHEMA_VALIDATE, MagicMock())
    @mock.patch(TASKINSTANCE_PREVIEW_TREE, MagicMock())
    @mock.patch(PERIODIC_TASK_CREATE, MagicMock(side_effect=Exception()))
    def test_create_periodic_task__periodic_task_create_fail(self):
        response = self.client.post(path=self.CREATE_PERIODIC_TASK_URL.format(template_id=TEST_TEMPLATE_ID,
                                                                              bk_biz_id=TEST_BIZ_CC_ID),
                                    data=json.dumps({'name': 'name',
                                                     'cron': 'cron'}),
                                    content_type='application/json')

        data = json.loads(response.content)

        self.assertFalse(data['result'])
        self.assertTrue('message' in data)

    @mock.patch(BUSINESS_GET, MagicMock(return_value=MockBusiness()))
    def test_set_periodic_task_enabled__success(self):
        task = MockPeriodicTask()
        with mock.patch(PERIODIC_TASK_GET, MagicMock(return_value=task)):
            response = self.client.post(path=self.SET_PERIODIC_TASK_ENABLED_URL.format(task_id=TEST_PERIODIC_TASK_ID,
                                                                                       bk_biz_id=TEST_BIZ_CC_ID),
                                        data=json.dumps({'enabled': True}),
                                        content_type='application/json')

            task.set_enabled.assert_called_once_with(True)

            data = json.loads(response.content)

            self.assertTrue(data['result'])
            self.assertEqual(data['data'], {
                'enabled': task.enabled
            })

    @mock.patch(PERIODIC_TASK_GET, MagicMock(side_effect=PeriodicTask.DoesNotExist))
    def test_set_periodic_task_enabled__task_does_not_exist(self):
        response = self.client.post(path=self.SET_PERIODIC_TASK_ENABLED_URL.format(task_id=TEST_PERIODIC_TASK_ID,
                                                                                   bk_biz_id=TEST_BIZ_CC_ID),
                                    data=json.dumps({'enabled': True}),
                                    content_type='application/json')

        data = json.loads(response.content)

        self.assertFalse(data['result'])
        self.assertTrue('message' in data)

    def test_modify_cron_for_periodic_task__success(self):
        biz = MockBusiness()
        task = MockPeriodicTask()
        cron = {'minute': '*/1'}

        with mock.patch(BUSINESS_GET, MagicMock(return_value=biz)):
            with mock.patch(PERIODIC_TASK_GET, MagicMock(return_value=task)):
                response = self.client.post(
                    path=self.MODIFY_PERIODIC_TASK_CRON_URL.format(task_id=TEST_PERIODIC_TASK_ID,
                                                                   bk_biz_id=TEST_BIZ_CC_ID),
                    data=json.dumps({'cron': cron}),
                    content_type='application/json')

                task.modify_cron.assert_called_once_with(cron, biz.time_zone)

                data = json.loads(response.content)

                self.assertTrue(data['result'])
                self.assertEqual(data['data'], {'cron': task.cron})

    @mock.patch(BUSINESS_GET, MagicMock(return_value=MockBusiness()))
    @mock.patch(PERIODIC_TASK_GET, MagicMock(side_effect=PeriodicTask.DoesNotExist))
    def test_modify_cron_for_periodic_task__task_does_not_exist(self):
        response = self.client.post(path=self.MODIFY_PERIODIC_TASK_CRON_URL.format(task_id=TEST_PERIODIC_TASK_ID,
                                                                                   bk_biz_id=TEST_BIZ_CC_ID),
                                    data=json.dumps({'enabled': True}),
                                    content_type='application/json')

        data = json.loads(response.content)

        self.assertFalse(data['result'])
        self.assertTrue('message' in data)

    def test_modify_cron_for_periodic_task__modify_raise(self):
        biz = MockBusiness()
        task = MockPeriodicTask()
        task.modify_cron = MagicMock(side_effect=Exception())
        cron = {'minute': '*/1'}

        with mock.patch(BUSINESS_GET, MagicMock(return_value=biz)):
            with mock.patch(PERIODIC_TASK_GET, MagicMock(return_value=task)):
                response = self.client.post(
                    path=self.MODIFY_PERIODIC_TASK_CRON_URL.format(task_id=TEST_PERIODIC_TASK_ID,
                                                                   bk_biz_id=TEST_BIZ_CC_ID),
                    data=json.dumps({'cron': cron}),
                    content_type='application/json')

                data = json.loads(response.content)

                self.assertFalse(data['result'])
                self.assertTrue('message' in data)

    def test_modify_constants_for_periodic_task__success(self):
        biz = MockBusiness()
        task = MockPeriodicTask()
        constants = {'k': 'v'}

        with mock.patch(BUSINESS_GET, MagicMock(return_value=biz)):
            with mock.patch(PERIODIC_TASK_GET, MagicMock(return_value=task)):
                response = self.client.post(
                    path=self.MODIFY_PERIODIC_TASK_CONSTANTS_URL.format(task_id=TEST_PERIODIC_TASK_ID,
                                                                        bk_biz_id=TEST_BIZ_CC_ID),
                    data=json.dumps({'constants': constants}),
                    content_type='application/json')

                task.modify_constants.assert_called_once_with(constants)

                data = json.loads(response.content)

                self.assertTrue(data['result'])
                self.assertEqual(data['data'], task.modify_constants.return_value)

    @mock.patch(PERIODIC_TASK_GET, MagicMock(side_effect=PeriodicTask.DoesNotExist))
    def test_modify_constants_for_periodic_task__task_does_not_exist(self):
        response = self.client.post(path=self.MODIFY_PERIODIC_TASK_CONSTANTS_URL.format(task_id=TEST_PERIODIC_TASK_ID,
                                                                                        bk_biz_id=TEST_BIZ_CC_ID),
                                    content_type='application/json')

        data = json.loads(response.content)

        self.assertFalse(data['result'])
        self.assertTrue('message' in data)

    def test_modify_constants_for_periodic_task__modify_constants_raise(self):
        biz = MockBusiness()
        task = MockPeriodicTask()
        task.modify_constants = MagicMock(side_effect=Exception())

        with mock.patch(BUSINESS_GET, MagicMock(return_value=biz)):
            with mock.patch(PERIODIC_TASK_GET, MagicMock(return_value=task)):
                response = self.client.post(
                    path=self.MODIFY_PERIODIC_TASK_CONSTANTS_URL.format(task_id=TEST_PERIODIC_TASK_ID,
                                                                        bk_biz_id=TEST_BIZ_CC_ID),
                    content_type='application/json')

                data = json.loads(response.content)

                self.assertFalse(data['result'])
                self.assertTrue('message' in data)

    def test_get_task_detail__success(self):
        mock_taskflow = MockTaskFlowInstance(get_task_detail_return=TEST_DATA)
        with mock.patch(TASKINSTANCE_GET, MagicMock(return_value=mock_taskflow)):
            assert_data = TEST_DATA
            response = self.client.get(path=self.GET_TASK_DETAIL.format(task_id=TEST_TASKFLOW_ID,
                                                                        bk_biz_id=TEST_BIZ_CC_ID))

            data = json.loads(response.content)

            self.assertTrue(data['result'])
            self.assertEqual(data['data'], assert_data)

    @mock.patch(TASKINSTANCE_GET, MagicMock(side_effect=TaskFlowInstance.DoesNotExist()))
    def test_get_task_detail__success__taskflow_does_not_exists(self):
        response = self.client.get(path=self.GET_TASK_DETAIL.format(task_id=TEST_TASKFLOW_ID,
                                                                    bk_biz_id=TEST_BIZ_CC_ID))

        data = json.loads(response.content)

        self.assertFalse(data['result'])
        self.assertTrue('message' in data)

    def test_get_task_node_detail__success(self):
        mock_taskflow = MockTaskFlowInstance(get_node_detail_return={'result': True, 'data': TEST_DATA})
        with mock.patch(TASKINSTANCE_GET, MagicMock(return_value=mock_taskflow)):
            assert_data = TEST_DATA
            response = self.client.get(path=self.GET_TASK_NODE_DETAIL.format(task_id=TEST_TASKFLOW_ID,
                                                                             bk_biz_id=TEST_BIZ_CC_ID),
                                       data={'node_id': TEST_NODE_ID,
                                             'component_code': TEST_COMPONENT_CODE,
                                             'subprocess_stack': TEST_SUBPROCESS_STACK})

            data = json.loads(response.content)

            self.assertTrue(data['result'])
            self.assertEqual(data['data'], assert_data)
            mock_taskflow.get_node_detail.assert_called_once_with(TEST_NODE_ID,
                                                                  TEST_COMPONENT_CODE,
                                                                  json.loads(TEST_SUBPROCESS_STACK))

    @mock.patch(TASKINSTANCE_GET, MagicMock(side_effect=TaskFlowInstance.DoesNotExist()))
    def test_get_task_node_detail__taskflow_doest_not_exist(self):
        response = self.client.get(path=self.GET_TASK_NODE_DETAIL.format(task_id=TEST_TASKFLOW_ID,
                                                                         bk_biz_id=TEST_BIZ_CC_ID),
                                   data={'node_id': TEST_NODE_ID,
                                         'component_code': TEST_COMPONENT_CODE,
                                         'subprocess_stack': TEST_SUBPROCESS_STACK})

        data = json.loads(response.content)
        self.assertFalse(data['result'])
        self.assertTrue('message' in data)

    def test_get_task_node_detail__with_invalid_subprocess_stack(self):
        response = self.client.get(path=self.GET_TASK_NODE_DETAIL.format(task_id=TEST_TASKFLOW_ID,
                                                                         bk_biz_id=TEST_BIZ_CC_ID),
                                   data={'node_id': TEST_NODE_ID,
                                         'component_code': TEST_COMPONENT_CODE,
                                         'subprocess_stack': 'abcdefg'})

        data = json.loads(response.content)
        self.assertFalse(data['result'])
        self.assertTrue('message' in data)

    def test_node_callback__success(self):
        mock_instance = MockTaskFlowInstance()
        with mock.patch(TASKINSTANCE_GET, MagicMock(return_value=mock_instance)):
            response = self.client.post(path=self.NODE_CALLBACK.format(task_id=TEST_TASKFLOW_ID,
                                                                       bk_biz_id=TEST_BIZ_CC_ID),
                                        data=json.dumps({
                                            'node_id': TEST_NODE_ID,
                                            'callback_data': TEST_CALLBACK_DATA
                                        }),
                                        content_type='application/json')

            data = json.loads(response.content)

            self.assertTrue(data['result'])
            mock_instance.callback.assert_called_once_with(TEST_NODE_ID, TEST_CALLBACK_DATA)

    @mock.patch(TASKINSTANCE_GET, MagicMock(side_effect=TaskFlowInstance.DoesNotExist()))
    def test_node_callback__taskflow_does_not_exists(self):
        response = self.client.post(path=self.NODE_CALLBACK.format(task_id=TEST_TASKFLOW_ID,
                                                                   bk_biz_id=TEST_BIZ_CC_ID),
                                    data=json.dumps({
                                        'node_id': TEST_NODE_ID,
                                        'callback_data': TEST_CALLBACK_DATA
                                    }),
                                    content_type='application/json')

        data = json.loads(response.content)

        self.assertFalse(data['result'])
        self.assertTrue('message' in data)
