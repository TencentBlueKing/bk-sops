# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2022 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from django.test import TestCase

from gcloud.core.apis.drf.filtersets import PropertyFilterSet
from gcloud.core.apis.drf.filters import BooleanFilter
from gcloud.tests.mock import MockQuerySet


class TestModelManager:
    def all(self):
        queryset = MockQuerySet()
        setattr(queryset, "model", TestModel)
        return queryset


class TestModel:

    _default_manager = TestModelManager()

    @property
    def test_attr(self):
        return True


class TestFilterSet(PropertyFilterSet):
    class Meta:
        model = TestModel
        property_fields = [("test_attr", BooleanFilter, ["exact"])]
        fields = []


class TestPropertyFilterSet(TestCase):
    def setUp(self):
        self.test_filterset = TestFilterSet()

    def test_build_filters_success(self):
        self.assertTrue("test_attr__exact" in self.test_filterset.base_filters.keys())
