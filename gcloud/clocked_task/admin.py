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

from gcloud.clocked_task.models import ClockedTask


@admin.register(ClockedTask)
class ClockedTaskAdmin(admin.ModelAdmin):
    list_display = [
        "task_id",
        "task_name",
        "project_id",
        "plan_start_time",
        "task_params",
        "template_id",
        "template_name",
        "clocked_task_id",
    ]
    search_field = ["task_name", "template_name", "task_id", "template_id"]
