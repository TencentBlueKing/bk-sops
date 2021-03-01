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

from django.contrib import admin

from gcloud.contrib.operate_record import models


@admin.register(models.TaskOperateRecord)
class TaskOperateRecordAdmin(admin.ModelAdmin):
    list_display = [
        "operator",
        "operate_type",
        "operate_source",
        "project_id",
        "instance_id",
        "node_id",
        "operate_date",
    ]
    search_fields = ["operator", "operate_type", "operate_source", "project_id", "instance_id", "node_id"]


@admin.register(models.TemplateOperateRecord)
class TemplateOperateRecordAdmin(admin.ModelAdmin):
    list_display = ["operator", "operate_type", "operate_source", "project_id", "instance_id", "operate_date"]
    search_fields = ["operator", "operate_type", "operate_source", "project_id", "instance_id"]
