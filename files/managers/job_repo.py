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
from django.core.files.base import File

from files.exceptions import InvalidOperationError, ApiResultError
from files.managers.base import Manager
from gcloud.conf import settings
from gcloud.core.models import Project

logger = logging.getLogger("root")

get_client_by_user = settings.ESB_GET_CLIENT_BY_USER


class JobRepoStorage:
    @staticmethod
    def generate_temporary_upload_url(
        username: str,
        bk_biz_id: int,
        file_names: list,
        bk_scope_type: str = "biz",
    ):
        esb_client = get_client_by_user(username)
        job_kwargs = {
            "bk_scope_type": bk_scope_type,
            "bk_scope_id": str(bk_biz_id),
            "bk_biz_id": bk_biz_id,
            "file_name_list": file_names,
        }
        job_result = esb_client.jobv3.generate_local_file_upload_url(job_kwargs)
        return job_result

    @staticmethod
    def save(upload_url, name, content, allow_overwrite=True):
        headers = {
            "X-BKREPO-OVERWRITE": str(allow_overwrite),
        }
        fh = File(file=content, name=name)
        try:
            response = requests.put(upload_url, headers=headers, data=fh)
            data = response.json()
        except Exception as e:
            message = f"[upload job_repo file failed]: {e}"
            logger.exception(message)
            raise ApiResultError(message)
        return {"result": data.get("code") == 0, "data": data.get("data", {}), "message": data.get("message")}


class JobRepoManager(Manager):

    type = "job_repo"

    def __init__(self):
        super(JobRepoManager, self).__init__(storage=JobRepoStorage())

    def save(self, name, content, shims=None, max_length=None, **kwargs):
        project_id = kwargs["project_id"]
        bk_biz_id = Project.objects.filter(id=project_id).only("bk_biz_id").first().bk_biz_id
        url_fetch_result = self.storage.generate_temporary_upload_url(
            username=kwargs["username"], bk_biz_id=bk_biz_id, file_names=[name]
        )
        if not url_fetch_result["result"]:
            logger.error(f"[fetch temporary upload url failed]: {url_fetch_result}")
            raise ApiResultError(f'fetch temporary upload url failed: {url_fetch_result["message"]}')
        file_name, data = list(url_fetch_result["data"]["url_map"].items())[0]  # 每次仅上传一个文件
        upload_url = data["upload_url"]
        upload_path = data["path"]
        upload_result = self.storage.save(upload_url, file_name, content)
        if not upload_result["result"]:
            raise ApiResultError(f'upload file failed: {upload_result["message"]}')
        return {"type": "job_repo", "tags": {"file_path": upload_path, "name": file_name}}

    def push_files_to_ips(
        self,
        esb_client,
        bk_biz_id,
        file_tags,
        target_path,
        ips,
        account,
        callback_url=None,
        timeout=None,
        bk_scope_type="biz",
    ):

        if not all([tag["type"] == "job_repo" for tag in file_tags]):
            raise InvalidOperationError("can not do files push operation on different types files, need job_repo")

        job_kwargs = {
            "bk_scope_type": bk_scope_type,
            "bk_scope_id": str(bk_biz_id),
            "bk_biz_id": bk_biz_id,
            "account_alias": account,
            "file_target_path": target_path,
            "file_source_list": [{"file_list": [tag["tags"]["file_path"] for tag in file_tags], "file_type": 2}],
            "target_server": {"ip_list": ips},
        }
        if timeout is not None:
            job_kwargs["timeout"] = int(timeout)
        if callback_url:
            job_kwargs["callback_url"] = callback_url

        job_result = esb_client.jobv3.fast_transfer_file(job_kwargs)

        if not job_result["result"]:
            return {
                "result": job_result["result"],
                "message": job_result["message"],
                "response": job_result,
                "kwargs": job_kwargs,
                "job_api": "jobv3.fast_transfer_file",
            }
        return {"result": job_result["result"], "data": {"job_id": job_result["data"]["job_instance_id"]}}

    def get_push_job_state(self, esb_client, job_id):
        raise NotImplementedError()
