# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
import importlib

from django.conf.urls import url

from pipeline.conf import settings
from pipeline.components import query

ver_url = importlib.import_module('pipeline.components.sites.%s.urls' % settings.RUN_VER)

urlpatterns = [
    url(r'^cc_get_set_list/(?P<biz_cc_id>\d+)/$', query.cc_get_set_list),
    url(r'^cc_get_module_name_list/(?P<biz_cc_id>\d+)/$', query.cc_get_module_name_list),
    url(r'^cc_get_plat_id/(?P<biz_cc_id>\d+)/$', query.cc_get_plat_id),

    url(r'^job_get_job_tasks_by_biz/(?P<biz_cc_id>\d+)/$', query.job_get_job_tasks_by_biz),
    url(r'^job_get_job_detail_by_biz/(?P<biz_cc_id>\d+)/(?P<task_id>\d+)/$', query.job_get_job_task_detail),

    url(r'^file_upload/(?P<biz_cc_id>\d+)/$', query.file_upload),
]
urlpatterns += getattr(ver_url, 'urlpatterns', [])
