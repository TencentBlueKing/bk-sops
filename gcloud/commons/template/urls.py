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

from django.conf.urls import url

from gcloud.commons.template import api


urlpatterns = [
    url(r'^api/form/$', api.form),
    url(r'^api/get_perms/$', api.get_perms),
    url(r'^api/save_perms/$', api.save_perms),
    url(r'^api/export/$', api.export_templates),
    url(r'^api/import/$', api.import_templates),
    url(r'^api/import_check/$', api.check_before_import),
]
