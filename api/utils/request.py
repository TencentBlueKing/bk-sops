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

import logging

from gcloud.conf import settings
from .thread import ThreadPool

logger = logging.getLogger("root")
logger_celery = logging.getLogger("celery")
get_client_by_user = settings.ESB_GET_CLIENT_BY_USER


def batch_request(
        func, params, get_data=lambda x: x["data"]["info"], get_count=lambda x: x["data"]["count"], limit=500,
        page_param=None
):
    """
    并发请求接口
    :param page_params: 分页参数，默认使用start/limit分页，例如：{"cur_page_param":"start", "page_size_param":"limit"}
    :param func: 请求方法
    :param params: 请求参数
    :param get_data: 获取数据函数
    :param get_count: 获取总数函数
    :param limit: 一次请求数量
    :return: 请求结果
    """
    # 兼容其他分页参数类型
    if page_param:
        try:
            cur_page_param = page_param["cur_page_param"]
            page_size_param = page_param["page_size_param"]
        except Exception as e:
            logger.error("[batch_request] please input correct page param, {}".format(e))
            return []
    else:
        cur_page_param = "start"
        page_size_param = "limit"

    # 请求第一次获取总数
    result = func(page={cur_page_param: 0, page_size_param: 1}, **params)

    if not result["result"]:
        logger.error("[batch_request] {api} count request error, result: {result}".format(api=func.path, result=result))
        return []

    count = get_count(result)
    data = []
    start = 0

    # 根据请求总数并发请求
    pool = ThreadPool()
    params_and_future_list = []
    while start < count:
        request_params = {"page": {page_size_param: limit, cur_page_param: start}}
        request_params.update(params)
        params_and_future_list.append({"params": request_params, "future": pool.apply_async(func, kwds=request_params)})

        start += limit

    pool.close()
    pool.join()

    # 取值
    for params_and_future in params_and_future_list:
        result = params_and_future["future"].get()

        if not result:
            logger.error(
                "[batch_request] {api} request error, params: {params}, result: {result}".format(
                    api=func.__name__, params=params_and_future["params"], result=result
                )
            )
            return []

        data.extend(get_data(result))

    return data
