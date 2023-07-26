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

import json
import typing

from django_test_toolkit.mixins.account import SuperUserMixin
from django_test_toolkit.mixins.blueking import (
    LoginExemptMixin,
    StandardResponseAssertionMixin,
)
from django_test_toolkit.testcases import ToolkitApiTestCase

from gcloud.core.models import ProjectBasedComponent


class ProjectBasedComponentAPITestMixin:
    def call_batch_operate_project_based_component(
        self,
        component_codes: typing.List[str],
        project_id: typing.Optional[int] = None,
        project_ids: typing.Optional[typing.List[int]] = None,
        is_deleted: bool = False,
    ):
        query_params: typing.Dict[str, typing.Any] = {"component_codes": component_codes}

        if project_id is not None:
            query_params["project_id"] = project_id

        if project_ids is not None:
            query_params["project_ids"] = project_ids

        self.client.post(
            f"/admin/batch_{('insert', 'delete')[is_deleted]}_project_based_component/",
            data=json.dumps(query_params),
            content_type="application/json",
        )


class BatchInsertProjectBasedComponentAPITest(
    ProjectBasedComponentAPITestMixin,
    ToolkitApiTestCase,
    SuperUserMixin,
    LoginExemptMixin,
    StandardResponseAssertionMixin,
):
    def test_insert_by_project_id(self):

        project_ids = ["1"]
        component_codes = ["a", "b"]

        self.call_batch_operate_project_based_component(component_codes, project_id=int(project_ids[0]))

        self.assertEqual(
            ProjectBasedComponent.objects.filter(
                project_id__in=project_ids, component_code__in=component_codes
            ).count(),
            2,
        )

    def test_insert_by_project_ids(self):
        project_ids = ["1", "2", "3"]
        component_codes = ["a", "b", "c"]

        self.call_batch_operate_project_based_component(
            component_codes, project_ids=[int(project_id) for project_id in project_ids]
        )

        self.assertEqual(
            ProjectBasedComponent.objects.filter(
                project_id__in=project_ids, component_code__in=component_codes
            ).count(),
            9,
        )

    def test_insert_with_existing_component_codes(self):

        project_ids = ["1", "2", "3"]
        component_codes = ["a", "b", "c"]

        self.call_batch_operate_project_based_component(
            component_codes[:2], project_ids=[int(project_id) for project_id in project_ids][:2]
        )

        self.assertEqual(
            ProjectBasedComponent.objects.filter(
                project_id__in=project_ids, component_code__in=component_codes
            ).count(),
            4,
        )

        self.call_batch_operate_project_based_component(
            component_codes, project_ids=[int(project_id) for project_id in project_ids]
        )

        self.assertEqual(
            ProjectBasedComponent.objects.filter(
                project_id__in=project_ids, component_code__in=component_codes
            ).count(),
            9,
        )


class BatchDeleteProjectBasedComponentAPITest(
    ProjectBasedComponentAPITestMixin,
    ToolkitApiTestCase,
    SuperUserMixin,
    LoginExemptMixin,
    StandardResponseAssertionMixin,
):
    def test_delete_by_project_id(self):

        project_ids = ["1"]
        component_codes = ["a", "b"]

        self.call_batch_operate_project_based_component(component_codes, project_id=int(project_ids[0]))

        self.call_batch_operate_project_based_component(
            component_codes, project_id=int(project_ids[0]), is_deleted=True
        )

        self.assertEqual(
            ProjectBasedComponent.objects.filter(
                project_id__in=project_ids, component_code__in=component_codes
            ).count(),
            0,
        )
