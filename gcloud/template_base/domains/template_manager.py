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
specific lan
"""

import traceback

from pipeline.exceptions import PipelineException

from gcloud.constants import TEMPLATE_NODE_NAME_MAX_LENGTH
from gcloud.template_base.utils import replace_template_id
from gcloud.utils.strings import standardize_name, standardize_pipeline_node_name

from pipeline.models import PipelineTemplate, TemplateRelationship
from pipeline_web.core.models import NodeInTemplate
from pipeline_web.parser.validator import validate_web_pipeline_tree
from pipeline_web.parser.clean import PipelineWebTreeCleaner


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
            return {
                "result": False,
                "data": None,
                "message": "[TemplateManager]validate_web_pipeline_tree failed: {}".format(str(e)),
                "verbose_message": "[TemplateManager]validate_web_pipeline_tree failed: {}".format(
                    traceback.format_exc()
                ),
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
            return {
                "result": False,
                "data": None,
                "message": "[TemplateManager]create_pipeline_template({kwargs}) failed: {e}".format(
                    kwargs=create_template_kwargs, e=str(e)
                ),
                "verbose_message": "[TemplateManager]create_pipeline_template({kwargs}) failed: {trace}".format(
                    kwargs=create_template_kwargs, trace=traceback.format_exc()
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
            return {
                "result": False,
                "data": None,
                "message": "[TemplateManager]create objects.create({kwargs}) failed: {e}".format(
                    kwargs=template_kwargs, e=str(e)
                ),
                "verbose_message": "[TemplateManager]create objects.create({kwargs}) failed: {trace}".format(
                    kwargs=template_kwargs, trace=traceback.format_exc()
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
                return {
                    "result": False,
                    "data": None,
                    "message": "[TemplateManager]validate_web_pipeline_tree failed: {}".format(str(e)),
                    "verbose_message": "[TemplateManager]validate_web_pipeline_tree failed: {}".format(
                        traceback.format_exc()
                    ),
                }

            replace_template_id(self.template_model_cls, pipeline_tree)

            pipeline_web_tree = PipelineWebTreeCleaner(pipeline_tree)
            pipeline_web_tree.clean()
            update_kwargs["structure_data"] = pipeline_tree

            try:
                pipeline_template.update_template(**update_kwargs)
            except PipelineException as e:
                return {
                    "result": False,
                    "data": None,
                    "message": "[TemplateManager]update_template({update_kwargs}) failed: {e}".format(
                        update_kwargs=update_kwargs, e=str(e)
                    ),
                    "verbose_message": "[TemplateManager]update_template({update_kwargs}) failed: {trace}".format(
                        update_kwargs=update_kwargs, trace=traceback.format_exc()
                    ),
                }

            # create node in template
            NodeInTemplate.objects.update_nodes_in_template(pipeline_template, pipeline_web_tree.origin_data)
        else:
            for k, v in update_kwargs.items():
                setattr(pipeline_template, k, v)
            pipeline_template.save()

        return {"result": True, "data": pipeline_template, "message": "success", "verbose_message": "success"}

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
            return (
                False,
                "flow template are referenced by other templates[{}], please delete them first".format(
                    ",".join(["%s:%s" % (item["id"], item["name"]) for item in referencer])
                ),
            )

        appmaker_referencer = template.referencer_appmaker()
        if appmaker_referencer:
            return (
                False,
                "flow template are referenced by mini apps[{}], please delete them first".format(
                    ",".join(["{}:{}".format(item["id"], item["name"]) for item in appmaker_referencer])
                ),
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
        pipeline_template_id_list = []
        references = {}
        for template in templates:
            referencer = template.referencer()
            referencer = [item for item in referencer if item["id"] not in template_ids]
            if referencer:
                references.setdefault(template.id, {}).setdefault("template", []).extend(referencer)
            appmaker_referencer = template.referencer_appmaker()
            if appmaker_referencer:
                references.setdefault(template.id, {}).setdefault("appmaker", []).extend(appmaker_referencer)
            if referencer or appmaker_referencer:
                not_delete_list.append(template.id)
            else:
                pipeline_template_id_list.append(template.pipeline_template.template_id)
                delete_list.append(template.id)

        # 删除该流程引用的子流程节点的执行方案
        relation_queryset = TemplateRelationship.objects.filter(ancestor_template_id__in=pipeline_template_id_list)
        for relation in relation_queryset:
            relation.templatescheme_set.clear()

        self.template_model_cls.objects.filter(id__in=delete_list).update(is_deleted=True)
        return {
            "result": True,
            "data": {"success": delete_list, "fail": not_delete_list, "references": references},
            "message": "",
        }
