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

import ujson as json

from gcloud import err_code
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa

from .utils import TEST_APP_CODE, TEST_USERNAME, APITest

TEST_PROJECT_ID = "123"
TEST_PROJECT_NAME = "biz name"
TEST_BIZ_CC_ID = "2"
TEST_TEMPLATE_ID = "96"
TEST_PIPELINE_TEMPLATE_ID = "4"
TEST_SCHEME_NAME = "方案一"
TEST_SCHEME_NODE_ID = "node19fe67fe8e59c75a63b3a639a605d8"
TEST_REQUIRED_NODE_ID = "node_required_id"
TEST_SCHEME_DATA = json.dumps([TEST_SCHEME_NODE_ID])

TEST_PIPELINE_TREE = {
    "activities": {
        TEST_SCHEME_NODE_ID: {"id": TEST_SCHEME_NODE_ID, "optional": True},
        TEST_REQUIRED_NODE_ID: {"id": TEST_REQUIRED_NODE_ID, "optional": False},
    },
    "constants": {},
}

TEMPLATESCHEME_CREATE = "gcloud.apigw.views.create_template_scheme.TemplateScheme.objects.create"


def mock_project():
    return MockProject(
        project_id=TEST_PROJECT_ID,
        name=TEST_PROJECT_NAME,
        bk_biz_id=TEST_BIZ_CC_ID,
        from_cmdb=True,
    )


def mock_template():
    return MockTaskTemplate(
        id=TEST_TEMPLATE_ID,
        pipeline_template=MockPipelineTemplate(id=TEST_PIPELINE_TEMPLATE_ID),
        pipeline_tree=TEST_PIPELINE_TREE,
    )


def build_scheme_mock():
    scheme_mock = MagicMock(
        id=1,
        unique_id="{}-{}".format(TEST_TEMPLATE_ID, TEST_SCHEME_NAME),
        data=TEST_SCHEME_DATA,
    )
    # name 是 MagicMock 的保留参数，需通过属性赋值方式设置
    scheme_mock.name = TEST_SCHEME_NAME
    return scheme_mock


class CreateTemplateSchemeAPITest(APITest):
    def url(self):
        return "/apigw/create_template_scheme/{project_id}/{template_id}/"

    def post(self, payload, content_type="application/json"):
        return self.client.post(
            path=self.url().format(project_id=TEST_PROJECT_ID, template_id=TEST_TEMPLATE_ID),
            data=payload,
            content_type=content_type,
            HTTP_BK_APP_CODE=TEST_APP_CODE,
            HTTP_BK_USERNAME=TEST_USERNAME,
        )

    @mock.patch(PROJECT_GET, MagicMock(return_value=mock_project()))
    @mock.patch(TASKTEMPLATE_GET, MagicMock(return_value=mock_template()))
    @mock.patch(TEMPLATESCHEME_CREATE)
    def test_create_template_scheme__success(self, mock_scheme_create):
        mock_scheme_create.return_value = build_scheme_mock()

        response = self.post(json.dumps({"name": TEST_SCHEME_NAME, "data": TEST_SCHEME_DATA}))

        data = json.loads(response.content)
        self.assertTrue(data["result"], msg=data)
        self.assertEqual(data["code"], err_code.SUCCESS.code)
        self.assertEqual(data["message"], "success")
        self.assertEqual(
            data["data"],
            {
                "id": 1,
                "unique_id": "{}-{}".format(TEST_TEMPLATE_ID, TEST_SCHEME_NAME),
                "name": TEST_SCHEME_NAME,
                "data": TEST_SCHEME_DATA,
            },
        )
        mock_scheme_create.assert_called_once_with(
            template_id=TEST_PIPELINE_TEMPLATE_ID,
            unique_id="{}-{}".format(TEST_TEMPLATE_ID, TEST_SCHEME_NAME),
            name=TEST_SCHEME_NAME,
            data=TEST_SCHEME_DATA,
        )

    @mock.patch(PROJECT_GET, MagicMock(return_value=mock_project()))
    @mock.patch(TASKTEMPLATE_GET, MagicMock(return_value=mock_template()))
    @mock.patch(TEMPLATESCHEME_CREATE)
    def test_create_template_scheme__success_with_data_list(self, mock_scheme_create):
        mock_scheme_create.return_value = build_scheme_mock()

        response = self.post(json.dumps({"name": TEST_SCHEME_NAME, "data": [TEST_SCHEME_NODE_ID]}))

        data = json.loads(response.content)
        self.assertTrue(data["result"], msg=data)
        # data 传入列表时，应统一转换为 JSON 字符串后落库
        mock_scheme_create.assert_called_once_with(
            template_id=TEST_PIPELINE_TEMPLATE_ID,
            unique_id="{}-{}".format(TEST_TEMPLATE_ID, TEST_SCHEME_NAME),
            name=TEST_SCHEME_NAME,
            data=TEST_SCHEME_DATA,
        )

    @mock.patch(PROJECT_GET, MagicMock(return_value=mock_project()))
    @mock.patch(TASKTEMPLATE_GET, MagicMock())
    @mock.patch(TEMPLATESCHEME_CREATE)
    def test_create_template_scheme__invalid_json_body(self, mock_scheme_create):
        response = self.post("not a json")

        data = json.loads(response.content)
        self.assertFalse(data["result"])
        self.assertEqual(data["code"], err_code.REQUEST_PARAM_INVALID.code)
        mock_scheme_create.assert_not_called()

    @mock.patch(PROJECT_GET, MagicMock(return_value=mock_project()))
    @mock.patch(TASKTEMPLATE_GET, MagicMock())
    @mock.patch(TEMPLATESCHEME_CREATE)
    def test_create_template_scheme__non_dict_body(self, mock_scheme_create):
        # 合法 JSON 但非 dict（列表/数字/null/字符串）应返回参数错误，而不是 500
        for payload in ("[]", "123", "null", '"a string"'):
            response = self.post(payload)
            data = json.loads(response.content)
            self.assertFalse(data["result"], msg=(payload, data))
            self.assertEqual(data["code"], err_code.REQUEST_PARAM_INVALID.code, msg=(payload, data))
        mock_scheme_create.assert_not_called()

    @mock.patch(PROJECT_GET, MagicMock(return_value=mock_project()))
    @mock.patch(TASKTEMPLATE_GET, MagicMock())
    @mock.patch(TEMPLATESCHEME_CREATE)
    def test_create_template_scheme__missing_params(self, mock_scheme_create):
        response = self.post(json.dumps({"name": TEST_SCHEME_NAME}))

        data = json.loads(response.content)
        self.assertFalse(data["result"])
        self.assertEqual(data["code"], err_code.REQUEST_PARAM_INVALID.code)
        mock_scheme_create.assert_not_called()

    @mock.patch(PROJECT_GET, MagicMock(return_value=mock_project()))
    @mock.patch(TASKTEMPLATE_GET, MagicMock())
    @mock.patch(TEMPLATESCHEME_CREATE)
    def test_create_template_scheme__invalid_data(self, mock_scheme_create):
        response = self.post(json.dumps({"name": TEST_SCHEME_NAME, "data": {"key": "value"}}))

        data = json.loads(response.content)
        self.assertFalse(data["result"])
        self.assertEqual(data["code"], err_code.REQUEST_PARAM_INVALID.code)
        mock_scheme_create.assert_not_called()

    @mock.patch(PROJECT_GET, MagicMock(return_value=mock_project()))
    @mock.patch(TASKTEMPLATE_GET, MagicMock())
    @mock.patch(TEMPLATESCHEME_CREATE)
    def test_create_template_scheme__empty_data(self, mock_scheme_create):
        response = self.post(json.dumps({"name": TEST_SCHEME_NAME, "data": []}))

        data = json.loads(response.content)
        self.assertFalse(data["result"])
        self.assertEqual(data["code"], err_code.REQUEST_PARAM_INVALID.code)
        mock_scheme_create.assert_not_called()

    @mock.patch(PROJECT_GET, MagicMock(return_value=mock_project()))
    @mock.patch(TASKTEMPLATE_GET, MagicMock(return_value=mock_template()))
    @mock.patch(TEMPLATESCHEME_CREATE)
    def test_create_template_scheme__node_not_exist(self, mock_scheme_create):
        response = self.post(json.dumps({"name": TEST_SCHEME_NAME, "data": ["node_not_exist"]}))

        data = json.loads(response.content)
        self.assertFalse(data["result"])
        self.assertEqual(data["code"], err_code.REQUEST_PARAM_INVALID.code)
        self.assertIn("node_not_exist", data["message"])
        mock_scheme_create.assert_not_called()

    @mock.patch(PROJECT_GET, MagicMock(return_value=mock_project()))
    @mock.patch(TASKTEMPLATE_GET, MagicMock(return_value=mock_template()))
    @mock.patch(TEMPLATESCHEME_CREATE)
    def test_create_template_scheme__node_not_optional(self, mock_scheme_create):
        response = self.post(json.dumps({"name": TEST_SCHEME_NAME, "data": [TEST_REQUIRED_NODE_ID]}))

        data = json.loads(response.content)
        self.assertFalse(data["result"])
        self.assertEqual(data["code"], err_code.REQUEST_PARAM_INVALID.code)
        self.assertIn(TEST_REQUIRED_NODE_ID, data["message"])
        mock_scheme_create.assert_not_called()

    @mock.patch(PROJECT_GET, MagicMock(return_value=mock_project()))
    @mock.patch(TASKTEMPLATE_GET, MagicMock(side_effect=TaskTemplate.DoesNotExist))
    @mock.patch(TEMPLATESCHEME_CREATE)
    def test_create_template_scheme__template_not_exist(self, mock_scheme_create):
        response = self.post(json.dumps({"name": TEST_SCHEME_NAME, "data": TEST_SCHEME_DATA}))

        data = json.loads(response.content)
        self.assertFalse(data["result"])
        self.assertEqual(data["code"], err_code.CONTENT_NOT_EXIST.code)
        mock_scheme_create.assert_not_called()

    @mock.patch(PROJECT_GET, MagicMock(return_value=mock_project()))
    @mock.patch(TASKTEMPLATE_GET, MagicMock(return_value=mock_template()))
    @mock.patch(TEMPLATESCHEME_FILTER)
    @mock.patch(TEMPLATESCHEME_CREATE)
    def test_create_template_scheme__scheme_already_exist(self, mock_scheme_create, mock_scheme_filter):
        mock_scheme_filter.return_value.exists.return_value = True

        response = self.post(json.dumps({"name": TEST_SCHEME_NAME, "data": TEST_SCHEME_DATA}))

        data = json.loads(response.content)
        self.assertFalse(data["result"])
        self.assertEqual(data["code"], err_code.REQUEST_PARAM_INVALID.code)
        mock_scheme_filter.assert_called_once_with(
            template_id=TEST_PIPELINE_TEMPLATE_ID,
            unique_id="{}-{}".format(TEST_TEMPLATE_ID, TEST_SCHEME_NAME),
        )
        mock_scheme_create.assert_not_called()

    @mock.patch(PROJECT_GET, MagicMock(return_value=mock_project()))
    @mock.patch(TASKTEMPLATE_GET, MagicMock(return_value=mock_template()))
    @mock.patch(
        TEMPLATESCHEME_CREATE,
        MagicMock(side_effect=Exception("UNIQUE constraint failed: raw internal detail")),
    )
    def test_create_template_scheme__create_failed(self):
        response = self.post(json.dumps({"name": TEST_SCHEME_NAME, "data": TEST_SCHEME_DATA}))

        data = json.loads(response.content)
        self.assertFalse(data["result"])
        self.assertEqual(data["code"], err_code.UNKNOWN_ERROR.code)
        # 不应把底层原始异常信息透出给调用方
        self.assertEqual(data["message"], "create scheme failed")
        self.assertNotIn("raw internal detail", data["message"])
