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

import traceback
from django.contrib import admin

from gcloud.analysis_statistics.models import (
    TaskflowExecutedNodeStatistics,
    TemplateNodeStatistics,
    TaskflowStatistics,
    TemplateStatistics,
    ProjectStatisticsDimension,
    TaskTmplExecuteTopN,
    TemplateVariableStatistics,
    TemplateCustomVariableSummary,
)
from gcloud.analysis_statistics.tasks import backfill_template_variable_statistics_task


@admin.register(TemplateNodeStatistics)
class TemplateNodeStatisticsAdmin(admin.ModelAdmin):
    list_display = ("id", "component_code", "template_id", "node_id", "is_sub", "version")
    search_fields = (
        "template_id__exact",
        "node_id__exact",
    )
    list_filter = ("component_code", "is_sub")


@admin.register(TaskflowExecutedNodeStatistics)
class TaskflowExecutedNodeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "component_code",
        "instance_id",
        "node_id",
        "is_sub",
        "started_time",
        "archived_time",
        "elapsed_time",
        "status",
        "is_skip",
        "is_retry",
        "version",
    )
    search_fields = (
        "instance_id__exact",
        "node_id__exact",
    )
    list_filter = (
        "component_code",
        "is_sub",
        "status",
        "is_skip",
    )


@admin.register(TemplateStatistics)
class TemplateStatisticsAdmin(admin.ModelAdmin):
    list_display = ("template_id", "atom_total", "subprocess_total", "gateways_total")

    search_fields = ("template_id__exact",)
    list_filter = ("template_id", "atom_total", "subprocess_total", "gateways_total")


@admin.register(TaskflowStatistics)
class TaskflowStatisticsAdmin(admin.ModelAdmin):
    list_display = ("instance_id", "atom_total", "subprocess_total", "gateways_total")

    search_fields = ("instance_id__exact",)
    list_filter = ("instance_id", "atom_total", "subprocess_total", "gateways_total")


@admin.register(ProjectStatisticsDimension)
class ProjectStatisticsDimensionAdmin(admin.ModelAdmin):
    list_display = ("dimension_id", "dimension_name")


@admin.register(TaskTmplExecuteTopN)
class TaskTmplExecuteTopNAdmin(admin.ModelAdmin):
    list_display = ("topn",)


@admin.register(TemplateVariableStatistics)
class TemplateVariableStatisticsAdmin(admin.ModelAdmin):
    list_display = ("template_id", "project_id", "variable_key", "variable_type", "variable_source", "refs")


@admin.register(TemplateCustomVariableSummary)
class TemplateCustomVariableSummaryAdmin(admin.ModelAdmin):
    list_display = ("variable_type", "task_template_refs", "common_template_refs")
    actions = ["backfill"]

    def backfill(modeladmin, request, queryset):
        try:
            backfill_template_variable_statistics_task.delay()
        except Exception:
            modeladmin.message_user(request, "backfill failed: {}".format(traceback.format_exc()))

    backfill.short_description = "backfill template variables statistics"
