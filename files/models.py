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

import uuid

from django.db import models
from django.utils import timezone

from files import env


class UploadTicketManager(models.Manager):
    def apply(self, applicant, apply_from=""):
        return self.create(
            code=uuid.uuid3(uuid.uuid1(), uuid.uuid4().hex).hex, applicant=applicant, apply_from=apply_from
        )

    def check_ticket(self, code):
        try:
            ticket = self.get(code=code)
        except UploadTicket.DoesNotExist:
            return False, "invalid ticket"

        if not ticket.is_available:
            return False, "ticket is not available"

        ticket.is_available = False
        ticket.used_at = timezone.now()
        ticket.save()

        return True, "success"


class UploadTicket(models.Model):
    code = models.CharField("unique code", max_length=32)
    applicant = models.CharField("which user apply this ticket", max_length=128)
    apply_from = models.CharField("which ip apply this ticket", max_length=128)
    created_at = models.DateTimeField("ticket create time", auto_now_add=True)
    is_available = models.BooleanField("wether this ticket is available", default=True)
    used_at = models.DateTimeField("ticket use time", null=True)

    objects = UploadTicketManager()


class UploadModuleFileTag(models.Model):
    source_ip = models.CharField("file locate ip", max_length=128)
    file_name = models.TextField("file name")
    file_path = models.TextField("file locate path")


class BKJobFileCredentialManager(models.Manager):
    def register_credential(self, bk_biz_id, esb_client):
        job_kwargs = {
            "bk_biz_id": bk_biz_id,
            "name": env.JOB_CREDENTIAL_NAME,
            "type": "USERNAME_PASSWORD",
            "credential_username": env.BKREPO_USERNAME,
            "credential_password": env.BKREPO_PASSWORD,
        }
        result = esb_client.jobv3.create_credential(job_kwargs)
        if not result["result"]:
            return {"result": False, "data": None, "message": result["message"]}
        credential_id = result["data"]["id"]
        self.update_or_create(bk_biz_id=bk_biz_id, defaults={"credential_id": credential_id})
        return {"result": True, "data": credential_id, "message": None}

    def get_or_create_credential(self, bk_biz_id, esb_client):
        qs = self.filter(bk_biz_id=bk_biz_id)
        if qs.exists():
            return {"result": True, "data": qs.first().credential_id, "message": None}
        return self.register_credential(bk_biz_id, esb_client)


class BKJobFileCredential(models.Model):
    bk_biz_id = models.IntegerField("CC business id", primary_key=True)
    credential_id = models.CharField("JOB credential id", max_length=128)
    objects = BKJobFileCredentialManager()


class BKJobFileSourceManager(models.Manager):
    def register_file_source(self, bk_biz_id, credential_id, esb_client):
        job_kwargs = {
            "bk_biz_id": bk_biz_id,
            "code": env.JOB_FILE_SOURCE_CODE,
            "alias": env.JOB_FILE_SOURCE_ALIAS,
            "type": "BLUEKING_ARTIFACTORY",
            "access_params": {"base_url": env.BKREPO_ENDPOINT_URL},
            "credential_id": credential_id,
        }
        result = esb_client.jobv3.create_file_source(job_kwargs)
        if not result["result"]:
            return {"result": False, "data": None, "message": result["message"]}
        file_source_id = result["data"]["id"]
        self.update_or_create(bk_biz_id=bk_biz_id, defaults={"file_source_id": file_source_id})
        return {"result": True, "data": file_source_id, "message": None}

    def get_or_create_file_source(self, bk_biz_id, credential_id, esb_client):
        qs = self.filter(bk_biz_id=bk_biz_id)
        if qs.exists():
            return {"result": True, "data": qs.first().file_source_id, "message": None}
        return self.register_file_source(bk_biz_id, credential_id, esb_client)


class BKJobFileSource(models.Model):
    bk_biz_id = models.IntegerField("CC business id", primary_key=True)
    file_source_id = models.IntegerField("JOB file source id")
    objects = BKJobFileSourceManager()
