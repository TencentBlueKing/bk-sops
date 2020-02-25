# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from django.conf.urls import url

from gcloud.tasktmpl3 import api

urlpatterns = [
    url(r'^api/form/(?P<project_id>\d+)/$', api.form),
    url(r'^api/collect/(?P<project_id>\d+)/$', api.collect),
    url(r'^api/export/(?P<project_id>\d+)/$', api.export_templates),
    url(r'^api/import/(?P<project_id>\d+)/$', api.import_templates),
    url(r'^api/import_check/(?P<project_id>\d+)/$', api.check_before_import),
    url(r'^api/replace_node_id/$', api.replace_all_templates_tree_node_id),
    url(r'^api/draw_pipeline/$', api.draw_pipeline),
    url(r'^api/import_and_replace_job_id/(?P<project_id>\d+)/$', api.import_preset_template_and_replace_job_id),
    url(r'^api/get_template_count/(?P<project_id>\d+)/$', api.get_template_count),
    url(r'^api/get_collect_template/(?P<project_id>\d+)/$', api.get_collect_template),
    url(r'^api/get_templates_with_expired_subprocess/(?P<project_id>\d+)/$', api.get_templates_with_expired_subprocess)
]
