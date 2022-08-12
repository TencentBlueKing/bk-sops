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
import json
import logging

import requests
from requests import HTTPError

from gcloud.taskflow3.domains.dispatchers import NodeCommandDispatcher
from gcloud.taskflow3.models import TaskCallBackRecord

logger = logging.getLogger("root")


class TaskCallBacker:
    def __init__(self, task_id, *args, **kwargs):
        self.task_id = task_id
        self.record = TaskCallBackRecord.objects.filter(task_id=self.task_id).first()
        self.extra_info = {"task_id": self.task_id, **json.loads(self.record.extra_info), **kwargs}

    def check_record_existence(self):
        return True if self.record else False

    def update_record(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self.record, key, value)
        self.record.save(update_fields=list(kwargs.keys()))

    def callback(self):
        if self.record.url:
            return self._url_callback()
        return self._local_callback()

    def _local_callback(self):
        try:
            node_id, version, engine_ver = (
                self.extra_info["node_id"],
                self.extra_info["node_version"],
                self.extra_info["engine_ver"],
            )
            dispatcher = NodeCommandDispatcher(engine_ver=engine_ver, node_id=node_id, taskflow_id=self.task_id)
            dispatcher.dispatch(command="callback", operator="", version=version, data=self.extra_info)
        except Exception as e:
            message = f"[TaskCallBacker _local_callback] data: {self.record.extra_info}, error: {e}"
            logger.exception(message)
            return False
        logger.info(f"[TaskCallBacker _local_callback] data: {self.record.extra_info}, callback success.")
        return True

    def _url_callback(self):
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
