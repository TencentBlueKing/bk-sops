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

from pipeline_web.core import signals, models

from pipeline_web.label.signals import handlers


def dispatch_node_in_template_post_save():
    signals.node_in_template_post_save.connect(
        handlers.node_in_template_save_handle,
        sender=models.NodeInTemplate,
        dispatch_uid='_node_in_template_post_save'
    )


def dispatch_node_in_template_delete():
    signals.node_in_template_delete.connect(
        handlers.node_in_template_delete_handle,
        sender=models.NodeInTemplate,
        dispatch_uid='_node_in_template_delete'
    )


def dispatch_node_in_instance_post_save():
    signals.node_in_instance_post_save.connect(
        handlers.node_in_instance_save_handle,
        sender=models.NodeInInstance,
        dispatch_uid='_node_in_instance_post_save'
    )


def dispatch():
    dispatch_node_in_template_post_save()
    dispatch_node_in_template_delete()
    dispatch_node_in_instance_post_save()
