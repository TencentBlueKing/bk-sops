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

import logging
import traceback

from celery.decorators import periodic_task

from gcloud import exceptions
from gcloud.core.project import sync_projects_from_cmdb

from pipeline.contrib.periodic_task.djcelery.tzcrontab import TzAwareCrontab

loggger = logging.getLogger('celery')


@periodic_task(run_every=TzAwareCrontab(minute='*/2'))
def cmdb_business_sync_task(task_id):
    loggger.info('Start sync business from cmdb...')
    try:
        sync_projects_from_cmdb(use_cache=False)
    except exceptions.APIError as e:
        loggger.error('An error occurred when sync cmdb business, message: {msg}, trace: {trace}'.format(
            msg=e.message,
            trace=traceback.format_exc()))
