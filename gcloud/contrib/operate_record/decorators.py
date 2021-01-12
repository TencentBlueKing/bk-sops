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
import traceback
from functools import wraps

from django.utils.decorators import available_attrs
from gcloud.contrib.operate_record.core import Record
from gcloud.contrib.operate_record.constants import OperateSource

logger = logging.getLogger("root")


def record_operation(record_type, action, source=OperateSource.app.name):
    """
    记录操作日志
    :param record_type: .constant模块中 RecordType 内容
    :param action: .constant模块中 OperateType 内容
    :param source: .constant模块中 OperateSource 内容
    :return:
    """

    def wrapper(func):
        @wraps(func, assigned=available_attrs(func))
        def decorator(*args, **kwargs):
            result = func(*args, **kwargs)
            try:
                Record(record_type, action, source, result, args, kwargs)()
            except Exception:
                logger.error("record operate failed, error:{}".format(traceback.format_exc()))
            return result

        return decorator

    return wrapper
