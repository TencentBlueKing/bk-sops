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

from abc import ABCMeta, abstractmethod


class Manager(object):

    __metaclass__ = ABCMeta

    def __init__(self, storage):
        self.storage = storage

    def save(self, name, content, shims=None, max_length=None):
        """
        content {object} -- [a proper File object or any python file-like object]
        This method should return a file tag, which will mark the file info for this type of manager:
        {'type': 'manager_type', 'tags': {...}}
        """
        raise NotImplementedError()

    @abstractmethod
    def push_files_to_ips(
            self,
            esb_client,
            bk_biz_id,
            file_tags,
            target_path,
            ips,
            account,
            callback_url=None):
        raise NotImplementedError()

    @abstractmethod
    def get_push_job_state(self, esb_client, job_id):
        raise NotImplementedError()
