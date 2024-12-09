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

from gcloud.common_template.apis.django import api

urlpatterns = [
    re_path(r"^api/form/$", api.form),
    re_path(r"^api/batch_form/$", api.batch_form),
    re_path(r"^api/export/$", api.export_templates),
    re_path(r"^api/import/$", api.import_templates),
    re_path(r"^api/import_check/$", api.check_before_import),
    re_path(r"^api/parents/$", api.parents),
]
