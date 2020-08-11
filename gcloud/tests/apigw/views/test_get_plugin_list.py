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


import ujson as json

from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa

from .utils import APITest


TEST_PROJECT_ID = "123"
TEST_PROJECT_NAME = "biz name"
TEST_BIZ_CC_ID = "123"


class GetPluginListAPITest(APITest):
    def url(self):
        return "/apigw/get_plugin_list/{project_id}/"

    @mock.patch(
        PROJECT_GET,
        MagicMock(
            return_value=MockProject(
                project_id=TEST_PROJECT_ID, name=TEST_PROJECT_NAME, bk_biz_id=TEST_BIZ_CC_ID, from_cmdb=True,
            )
        ),
    )
    def test_get_component_list(self):
        comp_model = MockComponentModel(code="code_token")
        comp = MockComponent(
            inputs="inputs_token",
            outputs="outputs_token",
            desc="desc_token",
            code="code_token",
            name="name_token",
            group_name="group_name",
        )

        mock_exclude = MagicMock()
        mock_exclude.exclude = MagicMock(return_value=[comp_model])
        mock_filter = MagicMock(return_value=mock_exclude)
        with mock.patch(APIGW_GET_PLUGIN_LIST_COMPONENT_MODEL_FILTER, mock_filter):
            with mock.patch(
                APIGW_GET_PLUGIN_LIST_COMPONENT_LIBRARY_GET_COMPONENT_CLS, MagicMock(return_value=comp),
            ):
                assert_data = [
                    {
                        "inputs": comp.inputs_format(),
                        "outputs": comp.outputs_format(),
                        "desc": comp.desc,
                        "code": comp.code,
                        "name": comp.name,
                        "group_name": comp.group_name,
                        "version": comp.version,
                    }
                ]

                response = self.client.get(path=self.url().format(project_id=TEST_PROJECT_ID))

                self.assertEqual(response.status_code, 200)

                data = json.loads(response.content)

                self.assertTrue(data["result"], msg=data)
                self.assertEqual(data["data"], assert_data)
