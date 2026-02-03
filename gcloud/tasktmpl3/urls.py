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

from django.urls import re_path

from gcloud.tasktmpl3.apis.django import api
from gcloud.tasktmpl3.apis.drf.viewsets.batch_form_with_schemes import BatchTemplateFormWithSchemesView
from gcloud.tasktmpl3.apis.drf.viewsets.form_with_schemes import TemplateFormWithSchemesView
from gcloud.tasktmpl3.apis.drf.viewsets.variable_field_explain import VariableFieldExplainView

urlpatterns = [
    # [deprecated] this api will be instead of form_with_schemes
    re_path(r"^api/form/(?P<project_id>\d+)/$", api.form),
    # [deprecated] this api will be instead of batch_form_with_schemes
    re_path(r"^api/batch_form/(?P<project_id>\d+)/$", api.batch_form),
    re_path(r"^api/export/(?P<project_id>\d+)/$", api.export_templates),
    re_path(r"^api/fetch_pipeline_tree/$", api.fetch_pipeline_tree),
    re_path(r"^api/import/(?P<project_id>\d+)/$", api.import_templates),
    re_path(r"^api/import_check/(?P<project_id>\d+)/$", api.check_before_import),
    re_path(r"^api/replace_node_id/$", api.replace_all_templates_tree_node_id),
    re_path(r"^api/draw_pipeline/$", api.draw_pipeline),
    re_path(r"^api/get_template_count/(?P<project_id>\d+)/$", api.get_template_count),
    re_path(
        r"^api/get_templates_with_expired_subprocess/(?P<project_id>\d+)/$", api.get_templates_with_expired_subprocess
    ),
    re_path(r"^api/get_constant_preview_result/$", api.get_constant_preview_result),
    re_path(r"^api/analysis_constants_ref/$", api.analysis_constants_ref),
    re_path(r"^api/parents/(?P<project_id>\d+)/$", api.parents),
    re_path(r"^api/variable_field_explain/$", VariableFieldExplainView.as_view()),
    re_path(r"^api/form_with_schemes/", TemplateFormWithSchemesView.as_view()),
    re_path(r"^api/batch_form_with_schemes/", BatchTemplateFormWithSchemesView.as_view()),
]
