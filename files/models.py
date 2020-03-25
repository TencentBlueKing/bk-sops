# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
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
