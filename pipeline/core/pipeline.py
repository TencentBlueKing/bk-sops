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

from __future__ import absolute_import

from pipeline.exceptions import PipelineException


class PipelineSpec(object):
    def __init__(self, start_event, end_event, flows, activities, gateways, data, context):
        objects = {
            start_event.id: start_event,
            end_event.id: end_event
        }
        for act in activities:
            objects[act.id] = act
        for gw in gateways:
            objects[gw.id] = gw

        self.start_event = start_event
        self.end_event = end_event
        self.flows = flows
        self.activities = activities
        self.gateways = gateways
        self.data = data
        self.objects = objects
        self.context = context


class Pipeline(object):
    def __init__(self, id, pipeline_spec, parent=None):
        self.id = id
        self.spec = pipeline_spec
        self.parent = parent

    @property
    def data(self):
        return self.spec.data

    @property
    def context(self):
        return self.spec.context

    @property
    def start_event(self):
        return self.spec.start_event

    @property
    def end_event(self):
        return self.spec.end_event

    @property
    def all_nodes(self):
        return self.spec.objects

    def data_for_node(self, node):
        node = self.spec.objects.get(node.id)
        if not node:
            raise PipelineException('Can not find node %s in this pipeline.' % node.id)
        return node.data

    def node(self, id):
        return self.spec.objects.get(id)
