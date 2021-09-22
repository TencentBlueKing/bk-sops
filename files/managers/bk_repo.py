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
import os
import uuid
import logging

from files import env
from files.managers.base import Manager
from bkstorages.backends.bkrepo import BKRepoStorage
from files.models import BKJobFileSource, BKJobFileCredential

logger = logging.getLogger("root")


class BKRepoManager(Manager):

    type = "bk_repo"

    def __init__(self, username, password, project_id, bucket, endpoint_url, file_overwrite):
        super(BKRepoManager, self).__init__(
            storage=BKRepoStorage(
                username=username,
                password=password,
                project_id=project_id,
                bucket=bucket,
                endpoint_url=endpoint_url,
                file_overwrite=file_overwrite,
            )
        )

    @staticmethod
    def _uniq_id():
        return uuid.uuid3(uuid.uuid1(), uuid.uuid4().hex).hex

    def _get_file_path(self, bk_biz_id, name, uid, shims, with_storage_path=False):
        path_args = [str(bk_biz_id), uid, name] if not shims else [str(bk_biz_id), shims, uid, name]
        if with_storage_path:
            path_args = [self.storage.client.project, self.storage.client.bucket] + path_args
        return os.path.join(*path_args)

    def generate_temporary_url(self, bk_biz_id, name, shims=None):
        # 获取临时上传链接
        uid = self._uniq_id()
        file_path = self._get_file_path("", name, uid, shims)
        url = self.storage.client.generate_presigned_url(key=file_path, expires_in=6000, token_type="UPLOAD")
        return {"result": True, "data": {"url": url, "file_path": file_path}}

    def save(self, name, content, shims=None, max_length=None, **kwargs):
        # TODO: 后续等制品库支持前端上传，则不需要通过后端进行文件上传
        uid = self._uniq_id()
        file_path = self._get_file_path("", name, uid, shims)
        self.storage.save(file_path, content)
        return {"type": "bk_repo", "tags": {"uid": uid, "shims": shims, "name": name}}

    def push_files_to_ips(self, esb_client, bk_biz_id, file_tags, target_path, ips, account, callback_url=None):
        try:
            file_source_id = BKJobFileSource.objects.get(bk_biz_id=env.JOB_FILE_BIZ_ID).file_source_id
        except BKJobFileSource.DoesNotExist:
            # 如果没有对应的文件源，则到JOB进行注册
            credential_result = BKJobFileCredential.objects.get_or_create_credential(
                bk_biz_id=env.JOB_FILE_BIZ_ID, esb_client=esb_client
            )
            if not credential_result["result"]:
                logger.error(f"[push_files_to_ips] get_or_create_credential FAILED: {credential_result['message']}")
                return credential_result
            credential_id = credential_result["data"]
            file_source_result = BKJobFileSource.objects.get_or_create_file_source(
                env.JOB_FILE_BIZ_ID, credential_id, esb_client
            )
            if not file_source_result["result"]:
                logger.error(f"[push_files_to_ips] get_or_create_file_source FAILED: {file_source_result['message']}")
                return file_source_result
            file_source_id = file_source_result["data"]
        job_kwargs = {
            "bk_biz_id": env.JOB_FILE_BIZ_ID,
            "account_alias": account,
            "file_target_path": target_path,
            "file_source_list": [
                {
                    "file_list": [
                        self._get_file_path(
                            "", tag["tags"]["name"], tag["tags"]["uid"], tag["tags"]["shims"], with_storage_path=True
                        )
                        for tag in file_tags
                    ],
                    "file_type": 3,
                    "file_source_id": file_source_id,
                }
            ],
            "target_server": {"ip_list": ips},
        }
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
