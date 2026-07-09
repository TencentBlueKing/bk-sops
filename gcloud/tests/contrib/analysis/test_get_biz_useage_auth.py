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

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.test import TestCase
from iam.exceptions import AuthFailedException

from gcloud.contrib.analysis.views import get_biz_useage

IAM_IS_ALLOWED = "gcloud.iam_auth.view_interceptors.statistics.iam.is_allowed"


class GetBizUseageAuthTestCase(TestCase):
    """BAC: get_biz_useage 返回平台级业务使用聚合数据，必须与其它统计接口一致校验 STATISTICS_VIEW。"""

    def _request(self):
        return SimpleNamespace(method="GET", user=SimpleNamespace(username="tester"))

    def test_denied_without_statistics_view(self):
        with patch(IAM_IS_ALLOWED, MagicMock(return_value=False)):
            with self.assertRaises(AuthFailedException):
                get_biz_useage(self._request(), "template")
