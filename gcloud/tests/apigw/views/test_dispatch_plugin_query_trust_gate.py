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

from unittest.mock import MagicMock, patch

import ujson as json

from gcloud import err_code

from .utils import APITest


class DispatchPluginQueryTrustGateTest(APITest):
    """BAC: dispatch_plugin_query 会解析并直接调用任意可路由的内部视图，
    必须仅允许 APIGW 信任名单(is_trust)应用调用，否则拒绝且不得触达 resolve/视图分发。"""

    def url(self):
        return "/apigw/dispatch_plugin_query/"

    @patch("gcloud.apigw.decorators.check_white_apps", MagicMock(return_value=False))
    def test_untrusted_app_is_forbidden(self):
        with patch("gcloud.apigw.views.plugin_proxy.resolve") as mock_resolve:
            response = self.client.post(
                path=self.url(),
                data=json.dumps({"url": "/pipeline/whatever/", "method": "GET"}),
                content_type="application/json",
            )
        data = json.loads(response.content)
        self.assertFalse(data["result"])
        self.assertEqual(data["code"], err_code.REQUEST_FORBIDDEN_INVALID.code)
        # 拒绝路径上绝不能触达内部视图解析
        mock_resolve.assert_not_called()

    @patch("gcloud.apigw.decorators.check_white_apps", MagicMock(return_value=True))
    def test_trusted_app_passes_gate(self):
        fake_view = MagicMock(return_value={"result": True, "data": "ok", "code": err_code.SUCCESS.code})
        fake_match = MagicMock(func=fake_view, kwargs={})
        with patch("gcloud.apigw.views.plugin_proxy.resolve", MagicMock(return_value=fake_match)):
            response = self.client.post(
                path=self.url(),
                data=json.dumps({"url": "/pipeline/whatever/", "method": "GET"}),
                content_type="application/json",
            )
        data = json.loads(response.content)
        self.assertTrue(data["result"], msg=data)
        fake_view.assert_called_once()
