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

from gcloud.contrib.appmaker import models
from django.contrib import admin


@admin.register(models.AppMaker)
class AppMakerAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'code', 'business', 'task_template', 'is_deleted']
    list_filter = ('business', 'is_deleted')
    search_fields = ['name', 'code']
    raw_id_fields = ['business', 'task_template']
