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
from unittest.mock import patch

from django.test import TestCase
from rest_framework import status

from gcloud.contrib.collection.models import Collection
from gcloud.core.apis.drf.viewsets.collection import CollectionViewSet


class CollectionCreateUsernameOverrideTestCase(TestCase):
    """验证 CollectionViewSet.create 在落库前强制把 username 覆盖为当前登录用户，
    防御 BAC：攻击者通过请求体中伪造他人 username 在他人收藏列表中写入数据。"""

    def setUp(self):
        Collection.objects.all().delete()

    def tearDown(self):
        Collection.objects.all().delete()

    def _build_request(self, username, data):
        request = SimpleNamespace(
            user=SimpleNamespace(username=username),
            data=data,
        )
        return request

    def _build_view(self, request):
        view = CollectionViewSet()
        view.action = "create"
        view.request = request
        view.format_kwarg = None
        view.kwargs = {}
        return view

    def test_create__overrides_request_body_username_with_current_user(self):
        attacker = "attacker"
        victim = "victim"

        request = self._build_request(
            attacker,
            [
                {
                    "username": victim,
                    "category": "project",
                    "instance_id": 100,
                    "extra_info": {"id": 100, "name": "biz-100"},
                }
            ],
        )
        view = self._build_view(request)

        response = view.create(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Collection.objects.filter(username=victim).count(), 0)
        self.assertEqual(Collection.objects.filter(username=attacker).count(), 1)

    def test_create__duplicate_check_uses_current_user_not_request_username(self):
        """重复收藏检测必须基于当前登录用户的库存，攻击者不能借受害者已有的收藏记录
        判定自己的收藏为重复而短路绕过 username 锁定。"""
        attacker = "attacker"
        victim = "victim"

        Collection.objects.create(
            username=victim,
            category="project",
            instance_id=200,
            extra_info="{}",
        )

        request = self._build_request(
            attacker,
            [
                {
                    "username": victim,
                    "category": "project",
                    "instance_id": 200,
                    "extra_info": {"id": 200, "name": "biz-200"},
                }
            ],
        )
        view = self._build_view(request)

        response = view.create(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Collection.objects.filter(username=attacker, instance_id=200).count(), 1)
        self.assertEqual(Collection.objects.filter(username=victim, instance_id=200).count(), 1)

    def test_create__rejects_when_current_user_already_has_same_collection(self):
        user = "tester"
        Collection.objects.create(
            username=user,
            category="project",
            instance_id=300,
            extra_info="{}",
        )

        request = self._build_request(
            user,
            [
                {
                    "username": user,
                    "category": "project",
                    "instance_id": 300,
                    "extra_info": {"id": 300, "name": "biz-300"},
                }
            ],
        )
        view = self._build_view(request)

        with patch("gcloud.core.apis.drf.viewsets.collection.logger"):
            response = view.create(request)

        self.assertEqual(Collection.objects.filter(username=user, instance_id=300).count(), 1)
        self.assertIn("detail", response.data)
