# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import logging

from pipeline_web.label.models import Label, NodeInInstanceAttrLabel, NodeInTemplateAttrLabel

logger = logging.getLogger("root")


def node_in_save(node_in_model, nodes_objs, nodes_info):
    nodes_pk_to_node_id = {node.pk: node.node_id for node in nodes_objs}
    node_pks = nodes_pk_to_node_id.keys()
    nodes_attr_label_to_update = node_in_model.objects.select_related("node").filter(node__pk__in=node_pks)
    # update when exist
    if nodes_attr_label_to_update.exists():
        node_in_model.labels.through.objects.filter(
            nodeintemplateattrlabel_id__in=nodes_attr_label_to_update.values_list("id", flat=True)
        ).delete()

    # add when not exist
    existing_node_pks = set(nodes_attr_label_to_update.values_list("node__pk", flat=True))
    nodes_obj_to_add = [node_in_model(node=node) for node in nodes_objs if node.pk not in existing_node_pks]
    if nodes_obj_to_add:
        node_in_model.objects.bulk_create(nodes_obj_to_add, batch_size=100)

    all_nodes_attr_label = node_in_model.objects.select_related("node").filter(node__pk__in=node_pks)
    label_params = set()
    for node_info in nodes_info.values():
        for label_info in node_info.get("labels", []):
            label_params.add((label_info["group"], label_info["label"]))
    label_objs = Label.objects.filter(
        group__code__in={g for g, _ in label_params}, code__in={c for _, c in label_params}
    ).select_related("group")
    label_dict = {(label.group.code, label.code): label for label in label_objs}

    through_objs = []
    for node_attr_label in all_nodes_attr_label:
        node_info = nodes_info.get(node_attr_label.node.node_id, {})
        for label_info in node_info.get("labels", []):
            group_code = label_info["group"]
            code = label_info["label"]
            label_obj = label_dict.get((group_code, code))
            if label_obj:
                through_objs.append(
                    node_in_model.labels.through(nodeinmodel_id=node_attr_label.id, label_id=label_obj.id)
                )
            else:
                logger.warning(f"Label[code={code}, group_code={group_code}] does not exist")
    if through_objs:
        node_in_model.labels.through.objects.bulk_create(through_objs, batch_size=100)


def node_in_template_save_handle(sender, nodes_objs, nodes_info, **kwargs):
    node_in_save(NodeInTemplateAttrLabel, nodes_objs, nodes_info)


def node_in_template_delete_handle(sender, nodes_objs, **kwargs):
    NodeInTemplateAttrLabel.objects.filter(node__in=nodes_objs).delete()


def node_in_instance_save_handle(sender, nodes_objs, nodes_info, **kwargs):
    node_in_save(NodeInInstanceAttrLabel, nodes_objs, nodes_info)
