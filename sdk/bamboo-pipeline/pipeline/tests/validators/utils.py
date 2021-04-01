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
start_event_id = "start_event_id"
end_event_id = "end_event_id"


def exclusive_gw_id(num):
    return "eg_%s" % num


def converge_gw_id(num):
    return "cg_%s" % num


def parallel_gw_id(num):
    return "pg_%s" % num


def act_id(num):
    return "act_%s" % num
