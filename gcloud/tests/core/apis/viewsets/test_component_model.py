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

import random
import typing
from unittest.mock import patch
from urllib.parse import urlencode

from django.urls import reverse
from django_test_toolkit.mixins.account import SuperUserMixin
from django_test_toolkit.mixins.blueking import (
    LoginExemptMixin,
    StandardResponseAssertionMixin,
)
from django_test_toolkit.mixins.drf import DrfPermissionExemptMixin
from django_test_toolkit.testcases import ToolkitApiTestCase
from pipeline.component_framework.models import ComponentModel

from gcloud.core.models import DisabledComponent


class ComponentModelTestCase(
    ToolkitApiTestCase,
    SuperUserMixin,
    LoginExemptMixin,
    DrfPermissionExemptMixin,
    StandardResponseAssertionMixin,
):
    VIEWSET_PATH = "gcloud.core.apis.drf.viewsets.component_model.ComponentModelSetViewSet"

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.components = [
            ComponentModel.objects.create(code="bk_http_request", version="v1.0", name="蓝鲸服务(BK)-HTTP 请求"),
            ComponentModel.objects.create(code="sleep_timer", version="legacy", name="蓝鲸服务(BK)-定时"),
        ]

    @classmethod
    def tearDownClass(cls):
        ComponentModel.objects.all().delete()
        super().tearDownClass()

    def call_by_action(self, action: str, query_params: typing.Optional[typing.Dict[str, str]] = None, **kwargs):

        url = reverse(f"component-{action}", kwargs=kwargs)
        if query_params:
            url = f"{url}?{urlencode(query_params)}"

        # sqlite3 不支持 CONVERT(SUBSTRING_INDEX(name, '-', -1) USING gbk) 的语法，需要 mock queryset 去除
        with patch(f"{self.VIEWSET_PATH}.queryset", ComponentModel.objects.all()):
            response = self.client.get(url)

        self.assertStandardSuccessResponse(response)
        return response.data

    def test_list(self):
        result = self.call_by_action("list")
        self.assertEqual(len(result["data"]), len(self.components))

    def test_list__disable(self):
        disable_component_obj = DisabledComponent.objects.create(
            component_code=random.choice(self.components).code,
            action=DisabledComponent.ACTION_TYPE_LIST,
            scope=DisabledComponent.SCOPE_TYPE_FLOW,
        )

        cases = [
            {
                "action": DisabledComponent.ACTION_TYPE_LIST,
                "scope": DisabledComponent.SCOPE_TYPE_FLOW,
                "query_scope": DisabledComponent.SCOPE_TYPE_FLOW,
                "len": len(self.components) - 1,
            },
            {
                "action": DisabledComponent.ACTION_TYPE_LIST,
                "scope": DisabledComponent.SCOPE_TYPE_FLOW,
                "query_scope": DisabledComponent.SCOPE_TYPE_TASK,
                "len": len(self.components),
            },
            {
                "action": DisabledComponent.ACTION_TYPE_LIST,
                "scope": DisabledComponent.SCOPE_TYPE_ALL,
                "query_scope": DisabledComponent.SCOPE_TYPE_FLOW,
                "len": len(self.components) - 1,
            },
            {
                "action": DisabledComponent.ACTION_TYPE_RETRIEVE,
                "scope": DisabledComponent.SCOPE_TYPE_FLOW,
                "query_scope": DisabledComponent.SCOPE_TYPE_FLOW,
                "len": len(self.components),
            },
        ]

        for case in cases:
            disable_component_obj.scope = case["scope"]
            disable_component_obj.action = case["action"]
            disable_component_obj.save()
            self.assertEqual(
                len(self.call_by_action("list", query_params={"scope": case["query_scope"]})["data"]), case["len"]
            )

    def test_retrieve(self):
        for component in self.components:
            result = self.call_by_action("detail", code=component.code)
            self.assertEqual(result["data"]["code"], component.code)

    def test_retrieve__disable(self):

        disable_component_obj = DisabledComponent.objects.create(
            component_code=random.choice(self.components).code,
            action=DisabledComponent.ACTION_TYPE_RETRIEVE,
            scope=DisabledComponent.SCOPE_TYPE_FLOW,
        )
        cases = [
            {
                "action": DisabledComponent.ACTION_TYPE_RETRIEVE,
                "scope": DisabledComponent.SCOPE_TYPE_FLOW,
                "query_scope": DisabledComponent.SCOPE_TYPE_FLOW,
                "not_found": True,
            },
            {
                "action": DisabledComponent.ACTION_TYPE_RETRIEVE,
                "scope": DisabledComponent.SCOPE_TYPE_FLOW,
                "query_scope": DisabledComponent.SCOPE_TYPE_TASK,
                "not_found": False,
            },
            {
                "action": DisabledComponent.ACTION_TYPE_RETRIEVE,
                "scope": DisabledComponent.SCOPE_TYPE_ALL,
                "query_scope": DisabledComponent.SCOPE_TYPE_FLOW,
                "not_found": True,
            },
            {
                "action": DisabledComponent.ACTION_TYPE_LIST,
                "scope": DisabledComponent.SCOPE_TYPE_FLOW,
                "query_scope": DisabledComponent.SCOPE_TYPE_FLOW,
                "not_found": False,
            },
        ]

        for case in cases:
            disable_component_obj.scope = case["scope"]
            disable_component_obj.action = case["action"]
            disable_component_obj.save()

            try:
                code = self.call_by_action(
                    "detail", query_params={"scope": case["query_scope"]}, code=disable_component_obj.component_code
                )["data"]["code"]
            except AssertionError:
                self.assertTrue(case["not_found"], True)
                continue

            self.assertEqual(code, disable_component_obj.component_code)
