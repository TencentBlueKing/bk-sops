# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2022 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import time
from concurrent.futures import as_completed
from concurrent.futures.thread import ThreadPoolExecutor
from typing import Callable, Dict, List


def batch_call(
    func: Callable,
    params_list: List[Dict],
    get_data=lambda x: x,
    extend_result: bool = False,
    interval: float = 0,
    **kwargs
) -> List:
    """
    # TODO 后续 batch_call 支持 *args 类参数
    并发请求接口，每次按不同参数请求最后叠加请求结果
    :param func: 请求方法
    :param params_list: 参数列表
    :param get_data: 获取数据函数
    :param extend_result: 是否展开结果
    :param interval: 任务提交间隔
    :return: 请求结果累计
    """

    result = []

    # 不存在参数列表，直接返回
    if not params_list:
        return result

    with ThreadPoolExecutor(max_workers=50) as ex:
        tasks = []
        for idx, params in enumerate(params_list):
            if idx != 0:
                time.sleep(interval)
            tasks.append(ex.submit(func, **params))

    for future in as_completed(tasks):
        if extend_result:
            result.extend(get_data(future.result()))
        else:
            result.append(get_data(future.result()))
    return result
