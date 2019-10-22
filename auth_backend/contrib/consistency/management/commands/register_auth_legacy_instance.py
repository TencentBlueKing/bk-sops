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

from __future__ import absolute_import, unicode_literals

import sys

from django.core.management.base import BaseCommand

from auth_backend.conf import SYSTEM_ID
from auth_backend.contrib.consistency import conf
from auth_backend.contrib.consistency.legacy import register_legacy_instances


class Command(BaseCommand):
    help = "Register Legacy Resource Instance to Permission System"
    separator = '-----------------------------------------------------'

    def handle(self, *args, **options):
        legacy_resources = conf.LEGACY_RESOURCES
        sys.stdout.write('The following resource legacy instances will be register:\n')
        sys.stdout.write(self.separator + '\n')

        for resource in legacy_resources:
            sys.stdout.write('{resource}\n'.format(resource=resource))
        sys.stdout.write(self.separator + '\n')

        register_legacy_instances(legacy_resources)

        sys.stdout.write(self.separator + '\n')
        sys.stdout.write('All legacy instances for {system} have been registered\n'.format(system=SYSTEM_ID))
