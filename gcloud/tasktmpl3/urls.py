# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import importlib

from django.conf.urls import url
from django.conf import settings

from gcloud.tasktmpl3 import api

import_data = importlib.import_module('gcloud.tasktmpl3.sites.%s.import_data' % settings.RUN_VER)
import_v2_data = importlib.import_module('gcloud.tasktmpl3.sites.%s.import_data_2_to_3' % settings.RUN_VER)

urlpatterns = [
    url(r'^api/form/(?P<biz_cc_id>\d+)/$', api.form),
    url(r'^api/collect/(?P<biz_cc_id>\d+)/$', api.collect),
    url(r'^api/get_perms/(?P<biz_cc_id>\d+)/$', api.get_perms),
    url(r'^api/save_perms/(?P<biz_cc_id>\d+)/$', api.save_perms),
    url(r'^api/import_v1/(?P<biz_cc_id>\d+)/$', import_data.import_v1),
    url(r'^api/import_v2/$', import_v2_data.import_v2),
    url(r'^api/export/(?P<biz_cc_id>\d+)/$', api.export_templates),
    url(r'^api/import/(?P<biz_cc_id>\d+)/$', api.import_templates),
    url(r'^api/import_check/(?P<biz_cc_id>\d+)/$', api.check_before_import),
    url(r'^api/replace_node_id/$', api.replace_all_templates_tree_node_id),
    url(r'^api/import_and_replace_job_id/(?P<biz_cc_id>\d+)/$', api.import_preset_template_and_replace_job_id),
    url(r'^api/get_template_count/(?P<biz_cc_id>\d+)/$', api.get_template_count),
    url(r'^api/get_collect_template/(?P<biz_cc_id>\d+)/$', api.get_collect_template),
]
