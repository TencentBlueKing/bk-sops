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
specific lan
"""
import hashlib
import json
import logging
import traceback

from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from pipeline.exceptions import PipelineException
from pipeline.models import PipelineTemplate, Snapshot, TemplateRelationship

from gcloud.constants import TEMPLATE_NODE_NAME_MAX_LENGTH
from gcloud.template_base.models import DraftTemplate
from gcloud.template_base.utils import replace_template_id
from gcloud.utils.strings import standardize_name, standardize_pipeline_node_name
from pipeline_web.core.models import NodeInTemplate
from pipeline_web.parser.clean import PipelineWebTreeCleaner
from pipeline_web.parser.validator import validate_web_pipeline_tree

logger = logging.getLogger("root")


class TemplateManager:
    def __init__(self, template_model_cls):
        self.template_model_cls = template_model_cls

    def create_pipeline(
            self,
            name: str,
            creator: str,
            pipeline_tree: dict,
            description: str = "",
    ) -> dict:
        """
        创建 pipeline 层模板

        :param name: 模板名
        :type name: str
        :param creator: 创建者
        :type creator: str
        :param pipeline_tree: 模板数据
        :type pipeline_tree: dict
        :param description: 模板描述, defaults to ""
        :type description: str, optional
        :return: [description]
        :rtype: dict
        """
        name = standardize_name(name, TEMPLATE_NODE_NAME_MAX_LENGTH)
        standardize_pipeline_node_name(pipeline_tree)

        try:
            validate_web_pipeline_tree(pipeline_tree)
        except PipelineException as e:
            message = _(f"保存流程失败: 流程树合法性校验失败, 请检查流程. 失败原因: {e} | create_pipeline")
            logger.error(message)
            return {
                "result": False,
                "data": None,
                "message": message,
                "verbose_message": _(
                    f"保存流程失败: 流程树合法性校验失败, 请检查流程. 失败原因: {traceback.format_exc()} | create_pipeline"),
            }

        create_template_kwargs = {
            "name": name,
            "creator": creator,
            "pipeline_tree": pipeline_tree,
            "description": description,
        }
        try:
            pipeline_template = self.template_model_cls.objects.create_pipeline_template(**create_template_kwargs)
        except Exception as e:
            message = _(
                f"保存流程失败: 创建Pipeline流程失败, 请检查流程. 创建参数[{create_template_kwargs}], 失败原因: [{e}] | create_pipeline")
            logger.error(message)
            return {
                "result": False,
                "data": None,
                "message": message,
                "verbose_message": _(
                    f"保存流程失败: 创建Pipeline流程失败, 请检查流程. "
                    f"创建参数[{create_template_kwargs}], 失败原因: [{traceback.format_exc()}] | create_pipeline"
                ),
            }

        return {"result": True, "data": pipeline_template, "message": "success", "verbose_message": "success"}

    def create(
            self,
            name: str,
            creator: str,
            pipeline_tree: dict,
            template_kwargs: dict,
            description: str = "",
    ) -> dict:
        """
        创建 template 层模板

        :param name: 模板名
        :type name: str
        :param creator: 创建者
        :type creator: str
        :param pipeline_tree: 模板数据
        :type pipeline_tree: dict
        :param template_kwargs: template 层参数
        :type template_kwargs: dict
        :param description: 描述, defaults to ""
        :type description: str, optional
        :return: [description]
        :rtype: dict
        """
        create_result = self.create_pipeline(
            name=name, creator=creator, pipeline_tree=pipeline_tree, description=description
        )
        if not create_result["result"]:
            return create_result

        template_kwargs["pipeline_template_id"] = create_result["data"].template_id
        try:
            template = self.template_model_cls.objects.create(**template_kwargs)
        except Exception as e:
            message = _(
                f"保存流程失败: 创建模板失败, 请检查流程. 创建参数[{template_kwargs}], 失败原因: [{e}] | create")
            logger.error(message)
            return {
                "result": False,
                "data": None,
                "message": message,
                "verbose_message": _(
                    f"保存流程失败: 创建模板失败, 请检查流程. 创建参数[{template_kwargs}], 失败原因: [{traceback.format_exc()}] | create"
                ),
            }

        return {"result": True, "data": template, "message": "success", "verbose_message": "success"}

    def update_pipeline(
            self,
            pipeline_template: PipelineTemplate,
            editor: str,
            name: str = "",
            pipeline_tree: str = None,
            description: str = "",
    ) -> dict:
        """
        更新 pipeline 层模板

        :param pipeline_template: pipeline 模板对象
        :type pipeline_template: PipelineTemplate
        :param editor: 编辑者
        :type editor: str
        :param name: 模板名, defaults to ""
        :type name: str, optional
        :param pipeline_tree: 模板结构, defaults to None
        :type pipeline_tree: str, optional
        :param description: 模板描述, defaults to ""
        :type description: str, optional
        :return: [description]
        :rtype: dict
        """
        update_kwargs = {"editor": editor}
        if name:
            update_kwargs["name"] = standardize_name(name, TEMPLATE_NODE_NAME_MAX_LENGTH)

        if description:
            update_kwargs["description"] = description

        if pipeline_tree:
            standardize_pipeline_node_name(pipeline_tree)
            try:
                validate_web_pipeline_tree(pipeline_tree)
            except PipelineException as e:
                message = _(f"保存流程失败: 流程树合法性校验失败, 请检查流程. 失败原因: {e} | update_pipeline")
                logger.error(message)
                return {
                    "result": False,
                    "data": None,
                    "message": message,
                    "verbose_message": _(
                        f"保存流程失败: 流程树合法性校验失败, 请检查流程. 失败原因: {traceback.format_exc()} | update_pipeline"
                    ),
                }

            replace_template_id(self.template_model_cls, pipeline_tree)

            pipeline_web_tree = PipelineWebTreeCleaner(pipeline_tree)
            pipeline_web_tree.clean()
            update_kwargs["structure_data"] = pipeline_tree

            try:
                pipeline_template.update_template(**update_kwargs)
            except Exception as e:
                message = _(
                    f"更新流程失败: 更新Pipeline失败, 请检查流程. 更新参数: [{update_kwargs}], 失败原因: [{e}] | update_pipeline")
                logger.error(message)
                return {
                    "result": False,
                    "data": None,
                    "message": message,
                    "verbose_message": _(
                        f"更新流程失败: 更新Pipeline失败, 请检查流程. 更新参数: [{update_kwargs}], 失败原因: [{traceback.format_exc()}"
                    ),
                }

            # create node in template
            NodeInTemplate.objects.update_nodes_in_template(pipeline_template, pipeline_web_tree.origin_data)
        else:
            for k, v in update_kwargs.items():
                setattr(pipeline_template, k, v)
            pipeline_template.save()

        return {"result": True, "data": pipeline_template, "message": "success", "verbose_message": "success"}

    def create_draft_without_template(self, pipeline_tree, editor):

        snapshot_id = Snapshot.objects.create_snapshot(pipeline_tree).id
        draft_template = DraftTemplate.objects.create(editor=editor, snapshot_id=snapshot_id)

        return draft_template.id

    def create_draft(self, template, editor):
        """
        创建一个草稿
        @param template: 模板
        @param editor: 编辑人
        @return:
        """
        snapshot_id = Snapshot.objects.create_snapshot(template.pipeline_template.data).id
        draft_template = DraftTemplate.objects.create(editor=editor, snapshot_id=snapshot_id)
        template.draft_template_id = draft_template.id
        template.save(update_fields=["draft_template_id"])

    @transaction.atomic()
    def update_draft_pipeline(self, draft_template, editor, pipeline_tree):
        # 草稿更新不会触发流程合法性校验
        draft_template.editor = editor
        draft_template.save()

        # 更新快照
        snapshot = Snapshot.objects.get(id=draft_template.snapshot_id)
        h = hashlib.md5()
        h.update(json.dumps(pipeline_tree).encode("utf-8"))
        snapshot.md5sum = h.hexdigest()
        snapshot.data = pipeline_tree
        snapshot.save()

        return {"result": True, "data": None, "message": "success", "verbose_message": "success"}

    def publish_draft_pipeline(self, template, editor):
        # 如果模板处于已发布状态, 此时应该更新
        result = self.update_pipeline(
            pipeline_template=template.pipeline_template,
            editor=editor,
            pipeline_tree=template.draft_pipeline_tree,
        )
        if result["result"] and not template.published:
            template.published = True
            template.save(update_fields=["published"])

        result["data"] = None
        return result

    @transaction.atomic()
    def discard_draft(self, template, editor):

        if not template.published:
            message = _("草稿废弃失败，当前流程处于未发布状态!")
            return {"result": False, "data": None, "message": message, "verbose_message": message}

        # 废弃草稿
        pipeline_tree = template.pipeline_template.data
        draft_template = template.draft_template

        draft_template.editor = editor
        draft_template.save()

        # 更新快照, 回退到当前正在发布的最后一个正式版本
        snapshot = Snapshot.objects.get(id=draft_template.snapshot_id)
        h = hashlib.md5()
        h.update(json.dumps(pipeline_tree).encode("utf-8"))
        snapshot.md5sum = h.hexdigest()
        snapshot.data = pipeline_tree
        snapshot.save()

        return {"result": True, "data": None, "message": "success", "verbose_message": "success"}

    def update(
            self,
            template: object,
            editor: str,
            name: str = "",
            pipeline_tree: str = None,
            description: str = "",
    ) -> dict:
        """
        更新 template 层模板

        :param template: template 对象
        :type template: object
        :param editor: 编辑者
        :type editor: str
        :param name: 模板名, defaults to ""
        :type name: str, optional
        :param pipeline_tree: 模板结构, defaults to None
        :type pipeline_tree: str, optional
        :param description: 模板描述, defaults to ""
        :type description: str, optional
        :return: [description]
        :rtype: dict
        """
        data = self.update_pipeline(
            pipeline_template=template.pipeline_template,
            editor=editor,
            name=name,
            pipeline_tree=pipeline_tree,
            description=description,
        )
        if not data["result"]:
            return data

        data["data"] = template
        return data

    def can_delete(self, template: object) -> (bool, str):
        """
        检测 template 是否能够删除

        :param self: [description]
        :type self: [type]
        :param str: [description]
        :type str: [type]
        :return: [description]
        :rtype: [type]
        """
        referencer = template.referencer()
        if referencer:
            message = _(
                "流程删除失败: 流程已被其他流程引用[{}], 暂不可删除, 请处理后重试 | can_delete".format(
                    ",".join([f'{item["template_type"]}:{item["id"]}:{item["name"]}' for item in referencer])
                )
            )
            logger.error(message)
            return (
                False,
                message,
            )

        appmaker_referencer = template.referencer_appmaker()
        if appmaker_referencer:
            message = _(
                "流程删除失败: 流程已被其他轻应用引用[{}], 暂不可删除, 请处理后重试 | can_delete".format(
                    ",".join([f'{item["id"]}:{item["name"]}' for item in appmaker_referencer])
                )
            )
            logger.error(message)
            return (
                False,
                message,
            )

        clocked_task_referencer = template.referencer_clocked_task()
        if clocked_task_referencer:
            message = _(
                "流程删除失败: 流程已被其他计划任务引用[{}], 暂不可删除, 请处理后重试 | can_delete".format(
                    ",".join([f'{item["id"]}:{item["name"]}' for item in clocked_task_referencer])
                )
            )
            logger.error(message)
            return (
                False,
                message,
            )

        periodic_task_referencer = template.referencer_periodic_task()
        if periodic_task_referencer:
            message = _(
                "流程删除失败: 流程已被其他周期任务引用[{}], 暂不可删除, 请处理后重试 | can_delete".format(
                    ",".join([f'{item["id"]}:{item["name"]}' for item in periodic_task_referencer])
                )
            )
            logger.error(message)
            return (
                False,
                message,
            )

        return True, ""

    def delete(self, template: object) -> dict:
        """
        删除某个 template

        :param template: template 对象
        :type template: object
        :return: [description]
        :rtype: dict
        """
        can_delete, message = self.can_delete(template)
        if not can_delete:
            return {"result": False, "data": None, "message": message, "verbose_message": message}

        self.template_model_cls.objects.filter(id=template.id).update(is_deleted=True)
        return {"result": True, "data": template, "message": "success", "verbose_message": "success"}

    def batch_delete(self, template_ids: list) -> dict:
        """
        批量删除 template

        :param template_ids: template id列表
        :type: list
        :return: [description]
        :rtype: dict
        """
        templates = self.template_model_cls.objects.select_related("pipeline_template").filter(id__in=template_ids)
        delete_list = []
        not_delete_list = []
        delete_pipeline_template_id_list = []
        references = {}
        for template in templates:
            referencer = template.referencer()
            referencer = [item for item in referencer if item["id"] not in template_ids]
            if referencer:
                references.setdefault(template.id, {}).setdefault("template", []).extend(referencer)
            appmaker_referencer = template.referencer_appmaker()
            if appmaker_referencer:
                references.setdefault(template.id, {}).setdefault("appmaker", []).extend(appmaker_referencer)
            clocked_task_referencer = template.referencer_clocked_task()
            if clocked_task_referencer:
                references.setdefault(template.id, {}).setdefault("clocked_task", []).extend(clocked_task_referencer)
            periodic_task_referencer = template.referencer_periodic_task()
            if periodic_task_referencer:
                references.setdefault(template.id, {}).setdefault("periodic_task", []).extend(periodic_task_referencer)
            if referencer or appmaker_referencer or clocked_task_referencer or periodic_task_referencer:
                not_delete_list.append(template.id)
            else:
                delete_pipeline_template_id_list.append(template.pipeline_template.template_id)
                delete_list.append(template.id)

        # 删除该流程引用的子流程节点的执行方案
        relation_queryset = TemplateRelationship.objects.filter(
            ancestor_template_id__in=delete_pipeline_template_id_list
        )
        for relation in relation_queryset:
            relation.templatescheme_set.clear()

        self.template_model_cls.objects.filter(id__in=delete_list).update(is_deleted=True)
        return {
            "result": True,
            "data": {"success": delete_list, "fail": not_delete_list, "references": references},
            "message": "",
        }
