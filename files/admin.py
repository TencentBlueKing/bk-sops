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

from django.contrib import admin, messages

from files import models
from files.models import BKJobFileCredential, BKJobFileSource
from gcloud.conf import settings

get_client_by_user = settings.ESB_GET_CLIENT_BY_USER


@admin.register(models.UploadModuleFileTag)
class UploadModuleFileTagAdmin(admin.ModelAdmin):
    list_display = ["id", "source_ip", "file_name", "file_path"]
    search_fields = ["id", "source_ip", "file_name", "file_path"]


@admin.register(models.UploadTicket)
class UploadTicketAdmin(admin.ModelAdmin):
    list_display = ["id", "code", "applicant", "apply_from", "created_at", "is_available", "used_at"]
    search_fields = ["id", "code", "applicant", "apply_from"]
    list_filter = ["is_available"]


@admin.register(models.BKJobFileCredential)
class BKJobFileCredentialAdmin(admin.ModelAdmin):
    list_display = ["bk_biz_id", "credential_id"]
    search_fields = ["bk_biz_id", "credential_id"]
    actions = ["register_credential"]

    def register_credential(self, request, queryset):
        """手动新注册JOB凭证"""
        esb_client = get_client_by_user(settings.SYSTEM_USE_API_ACCOUNT)
        for bk_biz_id in queryset.values_list("bk_biz_id", flat=True):
            BKJobFileCredential.objects.register_credential(bk_biz_id, esb_client)


@admin.register(models.BKJobFileSource)
class BKJobFileSourceAdmin(admin.ModelAdmin):
    list_display = ["bk_biz_id", "file_source_id"]
    search_fields = ["bk_biz_id", "file_source_id"]
    actions = ["register_file_source"]

    def register_file_source(self, request, queryset):
        """手动新注册JOB文件源"""
        esb_client = get_client_by_user(settings.SYSTEM_USE_API_ACCOUNT)
        bk_biz_ids = queryset.values_list("bk_biz_id", flat=True)
        credentials = BKJobFileCredential.objects.filter(bk_biz_id__in=bk_biz_ids).values("bk_biz_id", "credential_id")
        if len(bk_biz_ids) != len(credentials):
            messages.error(request, "All selected bk_biz_id should have credential_id in BKJobFileCredential")
            return
        for info in credentials:
            BKJobFileSource.objects.register_file_source(info["bk_biz_id"], info["credential_id"], esb_client)
