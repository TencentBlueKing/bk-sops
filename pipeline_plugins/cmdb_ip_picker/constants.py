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

NO_ERROR = '0'
ERROR_CODE_PREFIX = '35'


class ErrorCode(object):
    PARAMETERS_ERROR = '%s01001' % ERROR_CODE_PREFIX
    API_GSE_ERROR = '%s10001' % ERROR_CODE_PREFIX
    API_CMDB_ERROR = '%s11001' % ERROR_CODE_PREFIX
    API_JOB_ERROR = '%s12001' % ERROR_CODE_PREFIX


ERROR_CODES = ErrorCode()
