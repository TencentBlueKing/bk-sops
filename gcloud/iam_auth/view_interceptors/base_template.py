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
from gcloud.iam_auth import IAMMeta
from gcloud.iam_auth.intercept import ViewInterceptor
from gcloud.iam_auth.utils import iam_resource_auth_or_raise, iam_multi_resource_auth_or_raise


class YamlImportInterceptor(ViewInterceptor):
    def process(self, request, *args, **kwargs):
        data = request.data
        template_type = data["template_type"]
        template_ids = list(data.get("override_mappings", {}).values())
        username = request.user.username

        if template_type == "project":
            project_resource_id = data["project_id"]
            project_get_resource_func = "resources_for_project"
            project_action = IAMMeta.FLOW_CREATE_ACTION
            template_action = IAMMeta.FLOW_EDIT_ACTION
            template_get_resource_func = "resources_list_for_flows"
        else:
            project_resource_id = None
            project_get_resource_func = None
            project_action = IAMMeta.COMMON_FLOW_CREATE_ACTION
            template_action = IAMMeta.COMMON_FLOW_EDIT_ACTION
            template_get_resource_func = "resources_list_for_common_flows"

        iam_resource_auth_or_raise(username, project_action, project_resource_id, project_get_resource_func)
        if template_ids:
            iam_multi_resource_auth_or_raise(username, template_action, template_ids, template_get_resource_func)


class YamlExportInterceptor(ViewInterceptor):
    def process(self, request, *args, **kwargs):
        data = request.data
        template_type = data["template_type"]
        template_ids = data["template_id_list"]

        if template_type == "project":
            template_action = IAMMeta.FLOW_VIEW_ACTION
            template_get_resource_func = "resources_list_for_flows"
        else:
            template_action = IAMMeta.COMMON_FLOW_VIEW_ACTION
            template_get_resource_func = "resources_list_for_common_flows"

        iam_multi_resource_auth_or_raise(
            request.user.username, template_action, template_ids, template_get_resource_func
        )
