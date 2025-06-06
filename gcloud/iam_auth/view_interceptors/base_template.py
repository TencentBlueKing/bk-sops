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
from gcloud.iam_auth import IAMMeta
from gcloud.iam_auth.intercept import ViewInterceptor
from gcloud.iam_auth.utils import iam_multi_resource_auth_or_raise, iam_resource_auth_or_raise


class YamlImportInterceptor(ViewInterceptor):
    def process(self, request, *args, **kwargs):
        data = request.data
        template_type = data["template_type"]
        override_template_ids = list(data.get("override_mappings", {}).values())
        refer_templates = list(data.get("refer_mappings", {}).values())
        username = request.user.username
        tenant_id = request.user.tenant_id
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

        iam_resource_auth_or_raise(username, project_action, tenant_id, project_resource_id, project_get_resource_func)
        if override_template_ids:
            iam_multi_resource_auth_or_raise(
                username, template_action, override_template_ids, template_get_resource_func, tenant_id
            )

        if refer_templates:
            common_refer_template_ids = [
                refer_template["template_id"]
                for refer_template in refer_templates
                if refer_template["template_type"] == "common"
            ]
            project_refer_template_ids = [
                refer_template["template_id"]
                for refer_template in refer_templates
                if refer_template["template_type"] == "project"
            ]
            if common_refer_template_ids:
                iam_multi_resource_auth_or_raise(
                    username,
                    IAMMeta.COMMON_FLOW_VIEW_ACTION,
                    common_refer_template_ids,
                    "resources_list_for_common_flows",
                    tenant_id,
                )
            if project_refer_template_ids:
                iam_multi_resource_auth_or_raise(
                    username,
                    IAMMeta.FLOW_VIEW_ACTION,
                    project_refer_template_ids,
                    "resources_list_for_flows",
                    tenant_id,
                )


class YamlExportInterceptor(ViewInterceptor):
    def process(self, request, *args, **kwargs):
        data = request.data
        template_type = data["template_type"]
        template_ids = data["template_id_list"]
        tenant_id = request.user.tenant_id
        if template_type == "project":
            template_action = IAMMeta.FLOW_VIEW_ACTION
            template_get_resource_func = "resources_list_for_flows"
        else:
            template_action = IAMMeta.COMMON_FLOW_VIEW_ACTION
            template_get_resource_func = "resources_list_for_common_flows"

        iam_multi_resource_auth_or_raise(
            request.user.username, template_action, template_ids, template_get_resource_func, tenant_id
        )
