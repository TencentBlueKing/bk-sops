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

from gcloud.analysis_statistics.data_migrate.models import MigrateLog


@admin.register(MigrateLog)
class TemplateNodeStatisticsAdmin(admin.ModelAdmin):
    list_display = (
        "migrate_switch",
        "migrate_num_once",
    )
    readonly_fields = (
        "desc",
        "template_in_pipeline_migrated",
        "component_in_template_migrated",
        "instance_in_pipeline_migrated",
        "component_execute_data_migrated",
        "template_in_pipeline_finished",
        "component_in_template_finished",
        "instance_in_pipeline_finished",
        "component_execute_data_finished",
        "template_in_pipeline_start",
        "component_in_template_start",
        "instance_in_pipeline_start",
        "component_execute_data_start",
        "template_in_pipeline_end",
        "component_in_template_end",
        "instance_in_pipeline_end",
        "component_execute_data_end",
        "template_in_pipeline_count",
        "component_in_template_count",
        "instance_in_pipeline_count",
        "component_execute_data_count",
    )
