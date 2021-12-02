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

# Start the celery clock service from the Django management command.
from __future__ import absolute_import, unicode_literals

from optparse import make_option as Option

from celery.bin import beat

from blueapps.contrib.bk_commands.management.app import app
from blueapps.contrib.bk_commands.management.base import CeleryCommand

beat = beat.beat(app=app)


class Command(CeleryCommand):
    """Run the celery periodic task scheduler."""

    help = 'Old alias to the "celery beat" command.'
    options = (
        Option("-A", "--app", default=None),
        Option("--broker", default=None),
        Option("--loader", default=None),
        Option("--config", default=None),
        Option("--workdir", default=None, dest="working_directory"),
        Option("--result-backend", default=None),
        Option("--no-color", "-C", action="store_true", default=None),
        Option("--quiet", "-q", action="store_true"),
    )
    if beat.get_options() is not None:
        options = options + CeleryCommand.options + beat.get_options()

    def handle(self, *args, **options):
        beat.run(*args, **options)
