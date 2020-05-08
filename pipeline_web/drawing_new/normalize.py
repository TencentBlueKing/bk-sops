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

from pipeline.core.constants import PE


def normalize_run(pipeline):
    pipeline['all_nodes'] = {}
    pipeline['all_nodes'].update(pipeline[PE.activities])
    pipeline['all_nodes'].update(pipeline[PE.gateways])
    pipeline['all_nodes'].update({
        pipeline[PE.start_event][PE.id]: pipeline[PE.start_event],
        pipeline[PE.end_event][PE.id]: pipeline[PE.end_event]
    })


def normalize_undo(pipeline):
    pipeline.pop('all_nodes')
