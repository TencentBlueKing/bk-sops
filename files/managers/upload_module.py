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

from .base import Manager
from ..models import UploadModuleFileTag
from ..exceptions import InvalidOperationError


class UploadModuleManager(Manager):

    type = "upload_module"

    def __init__(self):
        super().__init__(None)

    def save(self, name, content, shims=None, max_length=None, **kwargs):

        tag = UploadModuleFileTag.objects.create(
            source_ip=kwargs["source_ip"], file_path=kwargs["file_path"], file_name=name
        )

        return {"type": "upload_module", "tags": {"tag_id": tag.id}}

    def push_files_to_ips(self, esb_client, bk_biz_id, file_tags, target_path, ips, account, callback_url=None):

        if not all([tag["type"] == "upload_module" for tag in file_tags]):
            raise InvalidOperationError("can not do files push operation on different types files")

        tag_ids = [tag["tags"]["tag_id"] for tag in file_tags]

        tag_models = UploadModuleFileTag.objects.filter(id__in=tag_ids)

        file_source = [
            {
                "files": ["{}/{}".format(tag.file_path, tag.file_name)],
                "account": "root",
                "ip_list": [{"bk_cloud_id": 0, "ip": tag.source_ip}],
            }
            for tag in tag_models
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
