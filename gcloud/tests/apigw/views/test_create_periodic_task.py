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


import ujson as json
import jsonschema


from gcloud.core.utils import format_datetime
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.periodictask.models import PeriodicTask
from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa

from .utils import APITest


TEST_PROJECT_ID = '123'
TEST_PROJECT_NAME = 'biz name'
TEST_BIZ_CC_ID = '123'
TEST_TEMPLATE_ID = '1'


class CreatePeriodicTaskAPITest(APITest):
    def url(self):
        return '/apigw/create_periodic_task/{template_id}/{project_id}/'

    @mock.patch(TASKINSTANCE_PREVIEW_TREE, MagicMock())
    @mock.patch(APIGW_CREATE_PERIODIC_TASK_JSON_SCHEMA_VALIDATE, MagicMock())
    def test_create_periodic_task__success(self):
        task = MockPeriodicTask()
        assert_data = {
            'id': task.id,
            'name': task.name,
            'template_id': task.template_id,
            'template_source': 'project',
            'creator': task.creator,
            'cron': task.cron,
            'enabled': task.enabled,
            'last_run_at': format_datetime(task.last_run_at),
            'total_run_count': task.total_run_count,
            'form': task.form,
            'pipeline_tree': task.pipeline_tree
        }
        proj = MockProject(project_id=TEST_PROJECT_ID,
                           name=TEST_PROJECT_NAME,
                           bk_biz_id=TEST_BIZ_CC_ID,
                           from_cmdb=True)
        template = MockTaskTemplate()
        replace_template_id_mock = MagicMock()

        with mock.patch(TASKTEMPLATE_GET, MagicMock(return_value=template)):
            with mock.patch(PROJECT_GET, MagicMock(return_value=proj)):
                with mock.patch(PERIODIC_TASK_CREATE, MagicMock(return_value=task)):
                    with mock.patch(APIGW_CREATE_PERIODIC_TASK_REPLACE_TEMPLATE_ID, replace_template_id_mock):
                        response = self.client.post(path=self.url().format(
                            template_id=TEST_TEMPLATE_ID,
                            project_id=TEST_PROJECT_ID),
                            data=json.dumps({'name': task.name,
                                             'cron': task.cron,
                                             'template_source': 'project',
                                             'exclude_task_nodes_id': 'exclude_task_nodes_id'}),
                            content_type='application/json')

                        TaskFlowInstance.objects.preview_pipeline_tree_exclude_task_nodes.assert_called_with(
                            template.pipeline_tree,
                            'exclude_task_nodes_id'
                        )

                        PeriodicTask.objects.create.assert_called_once_with(
                            project=proj,
                            template=template,
                            template_source='project',
                            name=task.name,
                            cron=task.cron,
                            pipeline_tree=template.pipeline_tree,
                            creator=''
                        )

                        data = json.loads(response.content)

                        replace_template_id_mock.assert_called_once_with(TaskTemplate, template.pipeline_tree)

                        self.assertTrue(data['result'], msg=data)
                        self.assertEqual(data['data'], assert_data)

    @mock.patch(TASKINSTANCE_PREVIEW_TREE, MagicMock())
    @mock.patch(APIGW_CREATE_PERIODIC_TASK_JSON_SCHEMA_VALIDATE, MagicMock())
    def test_create_periodic_task__common_template(self):
        task = MockPeriodicTask(template_source='common')
        assert_data = {
            'id': task.id,
            'name': task.name,
            'template_id': task.template_id,
            'template_source': 'common',
            'creator': task.creator,
            'cron': task.cron,
            'enabled': task.enabled,
            'last_run_at': format_datetime(task.last_run_at),
            'total_run_count': task.total_run_count,
            'form': task.form,
            'pipeline_tree': task.pipeline_tree
        }
        proj = MockProject(project_id=TEST_PROJECT_ID,
                           name=TEST_PROJECT_NAME,
                           bk_biz_id=TEST_BIZ_CC_ID,
                           from_cmdb=True)
        template = MockCommonTemplate()
        replace_template_id_mock = MagicMock()

        with mock.patch(COMMONTEMPLATE_GET, MagicMock(return_value=template)):
            with mock.patch(PROJECT_GET, MagicMock(return_value=proj)):
                with mock.patch(PERIODIC_TASK_CREATE, MagicMock(return_value=task)):
                    with mock.patch(APIGW_CREATE_PERIODIC_TASK_REPLACE_TEMPLATE_ID, replace_template_id_mock):
                        response = self.client.post(path=self.url().format(
                            template_id=TEST_TEMPLATE_ID,
                            project_id=TEST_PROJECT_ID),
                            data=json.dumps({'name': task.name,
                                             'cron': task.cron,
                                             'template_source': 'common',
                                             'exclude_task_nodes_id': 'exclude_task_nodes_id'}),
                            content_type='application/json')

                        TaskFlowInstance.objects.preview_pipeline_tree_exclude_task_nodes.assert_called_with(
                            template.pipeline_tree,
                            'exclude_task_nodes_id'
                        )

                        PeriodicTask.objects.create.assert_called_once_with(
                            project=proj,
                            template=template,
                            template_source='common',
                            name=task.name,
                            cron=task.cron,
                            pipeline_tree=template.pipeline_tree,
                            creator=''
                        )

                        data = json.loads(response.content)

                        replace_template_id_mock.assert_called_once_with(TaskTemplate, template.pipeline_tree)

                        self.assertTrue(data['result'], msg=data)
                        self.assertEqual(data['data'], assert_data)

    @mock.patch(TASKTEMPLATE_GET, MagicMock(side_effect=TaskTemplate.DoesNotExist()))
    def test_create_periodic_task__template_does_not_exist(self):
        response = self.client.post(path=self.url().format(template_id=TEST_TEMPLATE_ID,
                                                           project_id=TEST_PROJECT_ID),
                                    content_type='application/json')

        data = json.loads(response.content)

        self.assertFalse(data['result'])
        self.assertTrue('message' in data)

    @mock.patch(TASKTEMPLATE_GET, MagicMock(return_value=MockTaskTemplate()))
    @mock.patch(APIGW_CREATE_PERIODIC_TASK_JSON_SCHEMA_VALIDATE, MagicMock(side_effect=jsonschema.ValidationError('')))
    def test_create_periodic_task__params_validate_fail(self):
        response = self.client.post(path=self.url().format(template_id=TEST_TEMPLATE_ID,
                                                           project_id=TEST_PROJECT_ID),
                                    content_type='application/json')

        data = json.loads(response.content)

        self.assertFalse(data['result'])
        self.assertTrue('message' in data)

    @mock.patch(TASKTEMPLATE_GET, MagicMock(return_value=MockTaskTemplate()))
    @mock.patch(APIGW_CREATE_PERIODIC_TASK_JSON_SCHEMA_VALIDATE, MagicMock())
    @mock.patch(TASKINSTANCE_PREVIEW_TREE, MagicMock(side_effect=Exception()))
    def test_create_periodic_task__preview_pipeline_fail(self):
        response = self.client.post(path=self.url().format(template_id=TEST_TEMPLATE_ID,
                                                           project_id=TEST_PROJECT_ID),
                                    content_type='application/json')

        data = json.loads(response.content)

        self.assertFalse(data['result'])
        self.assertTrue('message' in data)

    @mock.patch(PROJECT_GET, MagicMock(return_value=MockProject(project_id=TEST_PROJECT_ID,
                                                                name=TEST_PROJECT_NAME,
                                                                bk_biz_id=TEST_BIZ_CC_ID,
                                                                from_cmdb=True)))
    @mock.patch(TASKTEMPLATE_GET, MagicMock(return_value=MockTaskTemplate()))
    @mock.patch(APIGW_CREATE_PERIODIC_TASK_JSON_SCHEMA_VALIDATE, MagicMock())
    @mock.patch(TASKINSTANCE_PREVIEW_TREE, MagicMock())
    @mock.patch(APIGW_CREATE_PERIODIC_TASK_REPLACE_TEMPLATE_ID, MagicMock(side_effect=Exception))
    def test_create_periodic_task__replace_template_id_fail(self):
        response = self.client.post(path=self.url().format(template_id=TEST_TEMPLATE_ID,
                                                           project_id=TEST_PROJECT_ID),
                                    data=json.dumps({'name': 'name',
                                                     'cron': 'cron'}),
                                    content_type='application/json')

        data = json.loads(response.content)
        self.assertFalse(data['result'])
        self.assertTrue('message' in data)

    @mock.patch(PROJECT_GET, MagicMock(return_value=MockProject(project_id=TEST_PROJECT_ID,
                                                                name=TEST_PROJECT_NAME,
                                                                bk_biz_id=TEST_BIZ_CC_ID,
                                                                from_cmdb=True)))
    @mock.patch(TASKTEMPLATE_GET, MagicMock(return_value=MockTaskTemplate()))
    @mock.patch(APIGW_CREATE_PERIODIC_TASK_JSON_SCHEMA_VALIDATE, MagicMock())
    @mock.patch(TASKINSTANCE_PREVIEW_TREE, MagicMock())
    @mock.patch(PERIODIC_TASK_CREATE, MagicMock(side_effect=Exception()))
    @mock.patch(APIGW_CREATE_PERIODIC_TASK_REPLACE_TEMPLATE_ID, MagicMock())
    def test_create_periodic_task__periodic_task_create_fail(self):
        response = self.client.post(path=self.url().format(template_id=TEST_TEMPLATE_ID,
                                                           project_id=TEST_PROJECT_ID),
                                    data=json.dumps({'name': 'name',
                                                     'cron': 'cron'}),
                                    content_type='application/json')

        data = json.loads(response.content)

        self.assertFalse(data['result'])
        self.assertTrue('message' in data)
