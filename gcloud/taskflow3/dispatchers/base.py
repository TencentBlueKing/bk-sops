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

import functools

from abc import ABCMeta

from gcloud import err_code
from gcloud.core.models import EngineConfig

from bamboo_engine.api import EngineAPIResult


def ensure_return_is_dict(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)

        dict_result = {
            "result": result.result,
            "message": result.message,
            "code": err_code.SUCCESS.code if result.result else err_code.UNKNOWN_ERROR.code,
        }
        if isinstance(result, EngineAPIResult) and result.exc:
            dict_result["message"] = "{}: {}".format(result.message, result.exc_trace)
        return dict_result

    return wrapper


class EngineCommandDispatcher(metaclass=ABCMeta):
    VALID_ENGINE_VER = {EngineConfig.ENGINE_VER_V1, EngineConfig.ENGINE_VER_V2}

    def _unsupported_engine_ver_result(self):
        return {
            "result": False,
            "message": "Unsupported engine version: {}".format(self.engine_ver),
            "code": err_code.UNKNOWN_ERROR.code,
        }
