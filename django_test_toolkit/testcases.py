# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
from django.test import TestCase
from rest_framework.test import APIClient

from .mixins.base import LifeCycleHooksMixin


class ToolkitTestCase(TestCase):
    """继承django.test.TestCase, 需要前置继承于相关生命周期Mixin"""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls._activate_mixin_hook(obj=cls, is_class=True, hook="setUpTestData")

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._activate_mixin_hook(obj=cls, is_class=True, hook="setUpClass")

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls._activate_mixin_hook(obj=cls, is_class=True, hook="tearDownClass")

    def setUp(self):
        super().setUp()
        self._activate_mixin_hook(obj=self, is_class=False, hook="setUp")

    def tearDown(self):
        super().tearDown()
        self._activate_mixin_hook(obj=self, is_class=False, hook="tearDown")

    @staticmethod
    def _activate_mixin_hook(obj, is_class, hook):
        """
        执行对应生命周期中各个Mixin的钩子函数
        :param obj: 调用者，类对象或实例对象
        :param is_class: 调用者是否为类对象
        :param hook: 对应生命周期钩子名称
        :return: None
        """
        cls = obj if is_class else obj.__class__
        for mixin in cls.__bases__:
            if issubclass(mixin, LifeCycleHooksMixin):
                getattr(mixin, hook)() if is_class else getattr(mixin, hook)(obj)


class ToolkitApiTestCase(ToolkitTestCase):
    client_class = APIClient
