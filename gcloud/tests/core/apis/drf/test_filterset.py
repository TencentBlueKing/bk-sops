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

from unittest.mock import MagicMock, patch

from django.test import TestCase

from gcloud.core.apis.drf.filtersets import PropertyFilterSet
from gcloud.core.apis.drf.filters import BooleanFilter
from gcloud.core.apis.drf.viewsets.task_template import TaskTemplateFilter
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


class TestTaskTemplateFilter(TestCase):
    def _assert_filtered_by_label_ids(self, value, expected_label_ids):
        query = MockQuerySet(filter_result="filtered")
        relation_queryset = MagicMock()
        relation_queryset.values_list.return_value = [11, 12]

        with patch(
            "gcloud.core.apis.drf.viewsets.task_template.TemplateLabelRelation.objects.filter",
            return_value=relation_queryset,
        ) as mock_filter:
            result = TaskTemplateFilter().filter_by_label_ids(query, "label_ids", value)

        mock_filter.assert_called_once_with(label_id__in=expected_label_ids)
        relation_queryset.values_list.assert_called_once_with("template_id", flat=True)
        query.filter.assert_called_once_with(id__in=[11, 12])
        self.assertEqual(result, "filtered")

    def test_filter_by_single_label_id(self):
        self._assert_filtered_by_label_ids("2", [2])

    def test_filter_by_pipe_separated_label_ids(self):
        self._assert_filtered_by_label_ids("2|18", [2, 18])

    def test_filter_by_comma_separated_label_ids(self):
        self._assert_filtered_by_label_ids("2,18", [2, 18])

    def test_filter_by_mixed_separators_and_blank_parts(self):
        self._assert_filtered_by_label_ids(" 2 , |18,", [2, 18])

    def test_filter_by_empty_label_id_parts(self):
        self._assert_filtered_by_label_ids("|", [])
