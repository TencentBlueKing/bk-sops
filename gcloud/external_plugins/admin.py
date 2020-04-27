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

from pipeline.contrib.external_plugins.models.forms import JsonFieldModelForm

from gcloud.external_plugins.models import (
    GitRepoOriginalSource,
    S3OriginalSource,
    FileSystemOriginalSource,
    CachePackageSource,
    SyncTask
)


@admin.register(GitRepoOriginalSource)
class GitRepoOriginalSourceAdmin(admin.ModelAdmin):
    form = JsonFieldModelForm
    list_display = ['id', 'name', 'base_source_id', 'repo_address', 'repo_raw_address', 'branch']
    list_filter = []
    search_fields = ['name', 'repo_address']


@admin.register(S3OriginalSource)
class S3OriginalSourceAdmin(admin.ModelAdmin):
    form = JsonFieldModelForm
    list_display = ['id', 'name', 'base_source_id', 'service_address', 'bucket', 'access_key', 'secret_key']
    list_filter = []
    search_fields = ['name', 'service_address', 'bucket']


@admin.register(FileSystemOriginalSource)
class FileSystemOriginalSourceAdmin(admin.ModelAdmin):
    form = JsonFieldModelForm
    list_display = ['id', 'name', 'base_source_id', 'path']
    list_filter = []
    search_fields = ['name', 'path']


@admin.register(CachePackageSource)
class CachePackageSourceAdmin(admin.ModelAdmin):
    list_display = ['id', 'type', 'base_source_id']
    list_filter = ['type']
    search_fields = ['base_source_id']


@admin.register(SyncTask)
class SyncTaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'creator', 'status', 'start_time', 'finish_time']
    list_filter = ['status']
    search_fields = ['creator']
