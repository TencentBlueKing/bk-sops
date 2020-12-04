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

from django.conf import settings

import env
from api.client import BKComponentClient
from api.utils.request import batch_request

# TODO:待GSE KIT接入ESB后修改
GSE_KIT_API_ENTRY = env.BK_GSE_KIT_API_ENTRY or "{}/{}".format(
    settings.BK_PAAS_INNER_HOST, "api/c/compapi/v2/gse_kit"
)


def _get_gse_kit_api(api_name):
    return "{}/{}/".format(GSE_KIT_API_ENTRY, api_name)


class BKGseKitClient(BKComponentClient):
    def _pre_process_data(self, data):
        """
        去除值为None的可选字段
        :param data:
        :return:
        """
        data = super()._pre_process_data(data)
        for param in data.keys():
            if data[param] is None:
                data.pop(param)
        return data

    def list_process(
            self,
            page_param,
            scope=None,
            expression_scope=None,
            bk_cloud_ids=None,
            process_status=None,
            is_auto=None,
    ):
        params = {
            "scope": scope,
            "expression_scope": expression_scope,
            "bk_cloud_ids": bk_cloud_ids,
            "process_status": process_status,
            "is_auto": is_auto
        }
        return batch_request(func=self._list_processes, params=params, page_param=page_param)

    def _list_processes(
            self,
            pagesize,
            page,
            scope=None,
            expression_scope=None,
            bk_cloud_ids=None,
            process_status=None,
            is_auto=None,
    ):
        return self._request(
            method="post",
            url=_get_gse_kit_api("list_process"),
            data={
                "pagesize": pagesize,
                "page": page,
                "scope": scope,
                "expression_scope": expression_scope,
                "bk_cloud_ids": bk_cloud_ids,
                "process_status": process_status,
                "is_auto": is_auto
            }
        )

    def create_job(self,
                   bk_biz_id,
                   job_object,
                   job_action,
                   scope=None,
                   expression_scope=None
                   ):
        """
        创建 gsekit 任务命令
        """
        param = {
            "job_object": job_object,
            "job_action": job_action,
            "scope": scope,
            "expression_scope": expression_scope
        }
        return self._request(
            method="post",
            url=_get_gse_kit_api("{bk_biz_id}/job".format(bk_biz_id=bk_biz_id)),
            data=param
        )

    def job_status(self, bk_biz_id, job_task_id):
        """
        查询gsekit 任务状态
        :param job_task_id: string
        """
        param = {
            "job_task_id_list": [job_task_id]
        }
        return self._request(
            method="post",
            url=_get_gse_kit_api("{bk_biz_id}/job".format(bk_biz_id=bk_biz_id)),
            data=param
        )
