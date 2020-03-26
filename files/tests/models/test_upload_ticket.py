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

from django.test import TestCase

from files.models import UploadTicket


class UploadTicketTestCase(TestCase):
    def test_apply(self):
        applicant = "user"
        apply_from = "apply_ip"
        ticket = UploadTicket.objects.apply(applicant, apply_from)
        self.assertEqual(len(ticket.code), 32)
        self.assertEqual(ticket.applicant, applicant)
        self.assertEqual(ticket.apply_from, apply_from)
        self.assertIsNotNone(ticket.created_at)
        self.assertTrue(ticket.is_available)
        self.assertIsNone(ticket.used_at)

    def test_cehck_ticket__fail_do_not_exist(self):
        ok, err = UploadTicket.objects.check_ticket("not exist code")
        self.assertFalse(ok)

    def test_check_ticket__fail_not_available(self):
        ticket = UploadTicket.objects.apply("user", "ip")
        ticket.is_available = False
        ticket.save()

        ok, err = UploadTicket.objects.check_ticket(ticket.code)
        self.assertFalse(ok)

    def test_check_ticket__success(self):
        ticket = UploadTicket.objects.apply("user", "ip")
        ok, err = UploadTicket.objects.check_ticket(ticket.code)
        self.assertTrue(ok)
        ticket.refresh_from_db()
        self.assertFalse(ticket.is_available)
        self.assertIsNotNone(ticket.used_at)
