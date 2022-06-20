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

from django.contrib import admin

from gcloud.template_base.models import DefaultTemplateScheme
from pipeline.models import TemplateScheme


@admin.register(DefaultTemplateScheme)
class DefaultTemplateSchemeAdmin(admin.ModelAdmin):
    list_display = ["id", "project_id", "template_id", "default_scheme_ids"]
    search_fields = ["project_id", "template_id"]


@admin.register(TemplateScheme)
class TemplateSchemeAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "unique_id", "template_id", "edit_time", "data"]
    search_fields = ["name", "template_id", "unique_id"]
