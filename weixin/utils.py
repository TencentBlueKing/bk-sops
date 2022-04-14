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


def iam_based_object_list_filter(data, need_actions):
    data["objects"] = list(
        filter(lambda bundle: set(need_actions).issubset(set(bundle.data["auth_actions"])), data["objects"])
    )
    return data


def iam_based_obj_list_filter(data, need_actions):
    if isinstance(data, dict):
        data["results"] = list(
            filter(lambda obj: set(need_actions).issubset(set(obj["auth_actions"])), data["results"])
        )
    else:
        data = list(filter(lambda obj: set(need_actions).issubset(set(obj["auth_actions"])), data))
    return data
