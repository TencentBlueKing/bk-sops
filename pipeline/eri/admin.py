# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from django.contrib import admin

from pipeline.eri import models


@admin.register(models.Process)
class ProcessAdmin(admin.ModelAdmin):
    search_fields = ["id___exact", "parent_id____exact", "current_node_id____exact", "suspended_by____exact"]


@admin.register(models.Node)
class NodeAdmin(admin.ModelAdmin):
    search_fields = ["node_id__exact"]


@admin.register(models.State)
class StateAdmin(admin.ModelAdmin):
    search_fields = ["node_id__exact", "root_id__exact", "parent_id__exact"]


@admin.register(models.Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    search_fields = ["id__exact", "node_id__exact"]


@admin.register(models.Data)
class DataAdmin(admin.ModelAdmin):
    search_fields = ["node_id__exact"]


@admin.register(models.ExecutionData)
class ExecutionDataAdmin(admin.ModelAdmin):
    search_fields = ["node_id__exact"]


@admin.register(models.CallbackData)
class CallbackDataAdmin(admin.ModelAdmin):
    search_fields = ["id__exact"]


@admin.register(models.ContextValue)
class ContextValueAdmin(admin.ModelAdmin):
    search_fields = ["pipeline_id__exact"]


@admin.register(models.ContextOutputs)
class ContextOutputsAdmin(admin.ModelAdmin):
    search_fields = ["pipeline_id__exact"]


@admin.register(models.ExecutionHistory)
class ExecutionHistoryAdmin(admin.ModelAdmin):
    search_fields = ["node_id__exact"]
