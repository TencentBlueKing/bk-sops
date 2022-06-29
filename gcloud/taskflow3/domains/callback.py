# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import logging

import requests
from requests import HTTPError

from gcloud.taskflow3.models import TaskCallBackRecord

logger = logging.getLogger("root")


class TaskCallBacker:
    def __init__(self, task_id, *args, **kwargs):
        self.task_id = task_id
        self.extra_info = {**kwargs, "task_id": self.task_id}
        self.record = TaskCallBackRecord.objects.filter(task_id=self.task_id).first()

    def callback(self):
        url = self.record.url
        response = None
        try:
            response = requests.post(url, data=self.extra_info)
            response.raise_for_status()
        except HTTPError as e:
            message = (
                f"[TaskCallBacker call_back] {url}, data: {self.extra_info}, "
                f"response: {getattr(response, 'content', None)}, error: {e}"
            )
            logger.exception(message)
            return False
        return True
