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

import logging
from django.conf import settings

import env
from api.client import BKComponentClient
from api.utils.thread import ThreadPool
from gcloud.exceptions import ApiRequestError
from gcloud.utils.handlers import handle_api_error

logger = logging.getLogger("root")


GSE_KIT_API_ENTRY = env.BK_GSE_KIT_API_ENTRY or "{}/{}".format(settings.BK_PAAS_ESB_HOST, "api/c/compapi/v2/gsekit/api")


def _get_gse_kit_api(api_name):
    return "{}/{}/".format(GSE_KIT_API_ENTRY, api_name)


class BKGseKitClient(BKComponentClient):
    def _pre_process_data(self, data):
        """
        去除值为None的可选字段
        :param data:
        :return:
        """
        super()._pre_process_data(data)
        data = {k: v for k, v in data.items() if v is not None}

        return data

    @staticmethod
    def _batch_request(
        func, params, get_data=lambda x: x["data"]["list"], get_count=lambda x: x["data"]["count"], limit=500,
    ):
        """
        gsekit 并发请求接口
        :param func: 请求方法
        :param params: 请求参数
        :param get_data: 获取数据函数
        :param get_count: 获取总数函数
        :param limit: 一次请求数量
        :return: 请求结果
        """

        # 请求第一次获取总数
        result = func(page_param={"page": 1, "pagesize": limit}, **params)

        if not result["result"]:
            message = handle_api_error("[batch_request]", func.__name__, params, result)
            logger.error(message)
            raise ApiRequestError(message)

        count = get_count(result)
        data = []
        start = 1

        # 根据请求总数并发请求
        pool = ThreadPool()
        params_and_future_list = []
        page_count = int(count / 500) + 1
        while start <= page_count:
            request_params = {"page_param": {"pagesize": limit, "page": start}}
            request_params.update(params)
            params_and_future_list.append(
                {"params": request_params, "future": pool.apply_async(func, kwds=request_params)}
            )

            start += 1

        pool.close()
        pool.join()

        # 取值
        for params_and_future in params_and_future_list:
            result = params_and_future["future"].get()

            if not result:
                message = handle_api_error("[batch_request]", func.__name__, params, result)
                logger.error(message)
                raise ApiRequestError(message)

            data.extend(get_data(result))

        return data

    def process_status(
        self, bk_biz_id, scope=None, expression_scope=None, bk_cloud_ids=None, process_status=None, is_auto=None,
    ):
        params = {
            "bk_biz_id": bk_biz_id,
            "scope": scope,
            "expression_scope": expression_scope,
            "bk_cloud_ids": bk_cloud_ids,
            "process_status": process_status,
            "is_auto": is_auto,
        }
        return self._batch_request(func=self._process_status, params=params)

    def _process_status(
        self,
        bk_biz_id,
        page_param,
        scope=None,
        expression_scope=None,
        bk_cloud_ids=None,
        process_status=None,
        is_auto=None,
    ):
        pagesize = page_param["pagesize"]
        page = page_param["page"]
        data = {
            "bk_biz_id": bk_biz_id,
            "pagesize": pagesize,
            "page": page,
        }
        if scope:
            data["scope"] = scope
        if expression_scope:
            data["expression_scope"] = expression_scope
        if bk_cloud_ids:
            data["bk_cloud_ids"] = bk_cloud_ids
        if process_status:
            data["process_status"] = process_status
        if is_auto:
            data["is_auto"] = is_auto
        return self._request(method="post", url=_get_gse_kit_api("process/process_status"), data=data,)

    def create_job(self, bk_biz_id, job_object, job_action, expression_scope, extra_data=None):
        """
        创建 gsekit 任务命令
        """
        param = {
            "bk_biz_id": bk_biz_id,
            "job_object": job_object,
            "job_action": job_action,
            "expression_scope": expression_scope,
        }
        if extra_data:
            param["extra_data"] = extra_data
        return self._request(method="post", url=_get_gse_kit_api("job/create_job"), data=param)

    def job_status(self, bk_biz_id, job_task_id):
        """
        查询 gsekit 任务状态
        :param bk_biz_id: string
        :param job_task_id: string
        """
        param = {"bk_biz_id": bk_biz_id, "job_id": job_task_id}
        return self._request(method="post", url=_get_gse_kit_api("job/job_status"), data=param)

    def flush_process(self, bk_biz_id):
        """
        刷新业务进程缓存
        :param bk_biz_id: string
        """
        param = {"bk_biz_id": bk_biz_id}
        return self._request(method="post", url=_get_gse_kit_api("process/flush_process"), data=param)

    def list_config_template(self, bk_biz_id):
        """
        获取 gsekit 配置模版列表
        """
        params = {"bk_biz_id": bk_biz_id}
        url = _get_gse_kit_api("config_template/config_template_list")
        return self._request(method="GET", url=url, data=params)
