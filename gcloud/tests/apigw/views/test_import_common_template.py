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


from gcloud.commons.template.models import CommonTemplate
from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa

from .utils import APITest


TEST_PROJECT_ID = '123'
TEST_PROJECT_NAME = 'biz name'
TEST_BIZ_CC_ID = '123'


class ImportCommonTemplateAPITest(APITest):
    def url(self):
        return '/apigw/import_common_template/'

    @mock.patch(APIGW_DECORATOR_CHECK_WHITE_LIST, MagicMock(return_value=False))
    @mock.patch(APIGW_IMPORT_COMMON_TEMPLATE_READ_ENCODED_TEMPLATE_DATA, MagicMock())
    def test_import_common_template__app_has_no_permission(self):
        response = self.client.post(path=self.url())

        data = json.loads(response.content)

        self.assertFalse(data['result'])
        self.assertTrue('message' in data)

    @mock.patch(APIGW_DECORATOR_CHECK_WHITE_LIST, MagicMock(return_value=True))
    @mock.patch(
        APIGW_IMPORT_COMMON_TEMPLATE_READ_ENCODED_TEMPLATE_DATA,
        MagicMock(return_value={'result': False, 'message': 'token'})
    )
    def test_import_common_template__read_template_data_file_error(self):
        response = self.client.post(path=self.url(),
                                    data=json.dumps({
                                        'override': False,
                                        'template_data': 'xxx'
                                    }),
                                    content_type='application/json')

        data = json.loads(response.content)

        self.assertFalse(data['result'])
        self.assertEqual(data['message'], 'token')

    @mock.patch(APIGW_DECORATOR_CHECK_WHITE_LIST, MagicMock(return_value=True))
    @mock.patch(
        APIGW_IMPORT_COMMON_TEMPLATE_READ_ENCODED_TEMPLATE_DATA,
        MagicMock(return_value={'result': True,
                                'data': {'template_data': 'token'}}))
    @mock.patch(COMMONTEMPLATE_IMPORT_TEMPLATES, MagicMock(side_effect=Exception()))
    def test_import_common_template__import_templates_error(self):
        response = self.client.post(path=self.url(),
                                    data=json.dumps({
                                        'override': False,
                                        'template_data': 'xxx'
                                    }),
                                    content_type='application/json')

        data = json.loads(response.content)

        self.assertFalse(data['result'])
        self.assertTrue('message' in data)

    @mock.patch(APIGW_DECORATOR_CHECK_WHITE_LIST, MagicMock(return_value=True))
    @mock.patch(
        APIGW_IMPORT_COMMON_TEMPLATE_READ_ENCODED_TEMPLATE_DATA,
        MagicMock(return_value={'result': True,
                                'data': {'template_data': 'token'}}))
    @mock.patch(COMMONTEMPLATE_IMPORT_TEMPLATES, MagicMock(return_value={'result': False, 'message': 'token'}))
    def test_import_common_template__import_templates_fail(self):
        response = self.client.post(path=self.url(),
                                    data=json.dumps({
                                        'override': False,
                                        'template_data': 'xxx'
                                    }),
                                    content_type='application/json')

        data = json.loads(response.content)

        self.assertFalse(data['result'])
        self.assertEqual(data['message'], 'token')

    @mock.patch(APIGW_DECORATOR_CHECK_WHITE_LIST, MagicMock(return_value=True))
    @mock.patch(
        APIGW_IMPORT_COMMON_TEMPLATE_READ_ENCODED_TEMPLATE_DATA,
        MagicMock(return_value={'result': True,
                                'data': {'template_data': 'token'}}))
    @mock.patch(COMMONTEMPLATE_IMPORT_TEMPLATES, MagicMock(return_value={'result': True, 'message': 'token'}))
    def test_import_common_template__success(self):
        response = self.client.post(path=self.url(),
                                    data=json.dumps({
                                        'override': True,
                                        'template_data': 'xxx'
                                    }),
                                    content_type='application/json')

        data = json.loads(response.content)

        self.assertTrue(data['result'], msg=data)
        self.assertEqual(data['message'], 'token')

        CommonTemplate.objects.import_templates.assert_called_once_with('token', True)
