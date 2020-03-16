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


from gcloud.core.utils import format_datetime
from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa

from .utils import APITest


TEST_PROJECT_ID = '123'
TEST_PROJECT_NAME = 'biz name'
TEST_BIZ_CC_ID = '123'


class GetCommontemplateListAPITest(APITest):
    def url(self):
        return '/apigw/get_common_template_list/'

    def test_get_common_template_list(self):
        pt1 = MockPipelineTemplate(id=1, name='pt1')
        pt2 = MockPipelineTemplate(id=2, name='pt2')

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
                    'create_time': format_datetime(tmpl.pipeline_template.create_time),
                    'editor': tmpl.pipeline_template.editor,
                    'edit_time': format_datetime(tmpl.pipeline_template.edit_time),
                    'category': tmpl.category,
                } for tmpl in task_templates
            ]

            response = self.client.get(path=self.url())

            self.assertEqual(response.status_code, 200)

            data = json.loads(response.content)

            self.assertTrue(data['result'], msg=data)
            self.assertEqual(data['data'], assert_data)
