# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import os
import uuid
import socket

from django.core.files.storage import FileSystemStorage

from .base import Manager
from ..exceptions import InvalidOperationError


class HostNFSManager(Manager):

    type = "host_nfs"

    def __init__(self, location, server_location):
        self.location = location
        self.server_location = server_location
        super(HostNFSManager, self).__init__(storage=FileSystemStorage(location=location))

    def _uniqid(self):
        return uuid.uuid3(uuid.uuid1(), uuid.uuid4().hex).hex

    def _get_host_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("10.0.0.1", 1))
        return s.getsockname()[0]

    def _get_file_path(self, location, name, uid, shims):
        path_args = [location, uid, name] if not shims else [location, shims, uid, name]
        return os.path.join(*path_args)

    def save(self, name, content, shims=None, max_length=None, **kwargs):
        uid = self._uniqid()

        self.storage.save(
            name=self._get_file_path(self.location, name, uid, shims), content=content, max_length=max_length
        )

        return {"type": "host_nfs", "tags": {"uid": uid, "shims": shims, "name": name}}

    def push_files_to_ips(self, esb_client, bk_biz_id, file_tags, target_path, ips, account, callback_url=None):

        if not all([tag["type"] == "host_nfs" for tag in file_tags]):
            raise InvalidOperationError("can not do files push operation on different types files")

        host_ip = self._get_host_ip()

        file_source = [
            {
                "files": [
                    self._get_file_path(
                        self.server_location, tag["tags"]["name"], tag["tags"]["uid"], tag["tags"]["shims"]
                    )
                    for tag in file_tags
                ],
                "account": "root",
                "ip_list": [{"bk_cloud_id": 0, "ip": host_ip}],
            }
        ]

        job_kwargs = {
            "bk_biz_id": bk_biz_id,
            "account": account,
            "file_target_path": target_path,
            "file_source": file_source,
            "ip_list": ips,
        }

        if callback_url:
            job_kwargs["bk_callback_url"] = callback_url

        job_result = esb_client.job.fast_push_file(job_kwargs)

        if not job_result["result"]:
            return {"result": job_result["result"], "message": job_result["message"]}

        return {"result": job_result["result"], "data": {"job_id": job_result["data"]["job_instance_id"]}}

    def get_push_job_state(self, esb_client, job_id):
        raise NotImplementedError()
