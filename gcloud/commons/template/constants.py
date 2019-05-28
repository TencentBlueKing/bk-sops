# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""


# template and taskflow permission names
class PermName(object):
    CREATE_TASK_PERM_NAME = 'create_task'
    FILL_PARAMS_PERM_NAME = 'fill_params'
    EXECUTE_TASK_PERM_NAME = 'execute_task'
    PERM_LIST = [CREATE_TASK_PERM_NAME,
                 FILL_PARAMS_PERM_NAME,
                 EXECUTE_TASK_PERM_NAME]


PermNm = PermName()
