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
import logging

from django.apps import apps
from django.db import transaction
from django.utils.translation import ugettext_lazy as _

from ...common_template.models import CommonTemplate
from ..utils import replace_biz_id_value
from .template_manager import TemplateManager

logger = logging.getLogger("root")


class TemplateImporter:
    def __init__(self, template_model_cls):
        self.template_model_cls = template_model_cls

    def import_template(self, operator: str, template_data: list, project_id: str, bk_biz_id: int = None) -> dict:
        """
        以 operator 的身份来导入若干个模板

        :param operator: 操作者
        :type operator: str
        :param template_data: [
            {
                "override_template_id": "要覆盖的模板的主键ID",
                "refer_template_config": "dict[template_id, template_type], 要引用的模版的配置",
                "name": "模板名",
                "pipeline_tree": "dict, 模板 pipeline tree",
                "description": "模板描述"，
                "template_kwargs": "dict, 模板创建关键字参数",
                "id": "str, 模板临时唯一 ID"
            }
        ]
        :type template_data: list
        :param project_id: 项目ID
        :type project_id: str
        :param bk_biz_id: 导入业务ID，公共流程为None
        :type bk_biz_id: int
        :return: [description]
        :rtype: dict
        """
        manager = TemplateManager(template_model_cls=self.template_model_cls)
        import_result = []
        pipeline_id_map = {}
        pipeline_version_map = {}
        source_info_map = {}
        common_child_templates = {}
        with transaction.atomic():
            for td in template_data:
                override_template_id = td["override_template_id"]
                refer_template_config = td["refer_template_config"]
                name = td["name"]
                pipeline_tree = td["pipeline_tree"]
                description = td["description"]

                if bk_biz_id:
                    replace_biz_id_value(pipeline_tree, bk_biz_id)

                # 如果引用了公共子流程，则先进行公共子流程的替换再替换子流程节点 ID
                if not override_template_id and not refer_template_config:
                    self._inject_common_child_templates_info(pipeline_tree, common_child_templates)

                replace_result = self._replace_subprocess_template_info(
                    pipeline_tree, pipeline_id_map, source_info_map, pipeline_version_map
                )
                if not replace_result["result"]:
                    import_result.append(replace_result)
                    continue

                if override_template_id or refer_template_config:
                    template_id = override_template_id or refer_template_config["template_id"]
                    try:
                        if (
                            refer_template_config
                            and self.template_model_cls is apps.get_model("tasktmpl3", "TaskTemplate")
                            and refer_template_config["template_type"] == "common"
                        ):
                            result = CommonTemplate.objects.check_template_project_scope(project_id, template_id)
                            if not result["result"]:
                                raise Exception(f"流程导入失败，{result['message']}")
                        else:
                            template = self.template_model_cls.objects.get(id=template_id)
                    except self.template_model_cls.DoesNotExist as e:
                        message = _(
                            f"流程导入失败: 文件解析异常, [ID: {template_id}]的流程不存在. 请修复后重试或联系管理员处理. "
                            f"错误内容: {e} | import_template"
                        )
                        logger.error(message)
                        import_result.append(
                            {
                                "result": False,
                                "data": "",
                                "message": message,
                                "verbose_message": e,
                            }
                        )
                        continue

                if override_template_id:
                    operate_result = manager.update(
                        template=template,
                        editor=operator,
                        name=name,
                        pipeline_tree=pipeline_tree,
                        description=description,
                    )
                    if operate_result["result"]:
                        pipeline_id_map[td["id"]] = operate_result["data"].id
                        pipeline_version_map[td["id"]] = operate_result["data"].version
                elif refer_template_config:
                    pipeline_tree = template.pipeline_tree
                    for key, constant in pipeline_tree["constants"].items():
                        source_info_map.setdefault(td["id"], {}).update({key: constant.get("source_info", {})})
                    if (
                        self.template_model_cls is apps.get_model("tasktmpl3", "TaskTemplate")
                        and refer_template_config["template_type"] == "common"
                    ):
                        common_child_templates[td["id"]] = {"constants": pipeline_tree["constants"]}
                    pipeline_id_map[td["id"]] = refer_template_config["template_id"]
                    pipeline_version_map[td["id"]] = template.version
                    operate_result = {"result": True, "data": None, "message": "success", "verbose_message": "success"}
                else:
                    operate_result = manager.create(
                        name=name,
                        creator=operator,
                        pipeline_tree=pipeline_tree,
                        template_kwargs=td["template_kwargs"],
                        description=description,
                    )
                    if operate_result["result"]:
                        pipeline_id_map[td["id"]] = operate_result["data"].id
                        pipeline_version_map[td["id"]] = operate_result["data"].version
                import_result.append(operate_result)

        return {"result": True, "data": import_result, "message": "success", "verbose_message": "success"}

    @staticmethod
    def _replace_subprocess_template_info(
        pipeline_tree: dict, pipeline_id_map: dict, source_map_info: dict, pipeline_version_map: dict
    ) -> dict:
        """
        将模板数据中临时的模板信息 替换成数据库中模型的对应信息

        :param pipeline_tree: pipeline tree 模板数据
        :type pipeline_tree: dict
        :param pipeline_id_map: Subprocess 节点中临时 ID 到数据库模型主键 ID 的映射
        :type pipeline_id_map: dict
        :param source_map_info: Subprocess 节点变量的的source_info替换成对应子流程一样的值
        :type source_map_info: dict
        :param pipeline_version_map: SubProcess 节点中临时 ID 到对应已导入流程 version的映射
        :type pipeline_version_map: dict
        """
        if not pipeline_id_map:
            return {
                "result": True,
                "data": None,
                "message": "pipeline_id_map is empty",
                "verbose_message": "pipeline_id_map is empty",
            }
        for act in pipeline_tree["activities"].values():
            if act["type"] == "SubProcess":
                if act["template_id"] not in pipeline_id_map:
                    return {
                        "result": False,
                        "data": None,
                        "message": "can not find {} in pipeline_id_map".format(act["template_id"]),
                        "verbose_message": "can not find {} in pipeline_id_map: {}".format(
                            act["template_id"], pipeline_id_map
                        ),
                    }
                imported_template_id = act["template_id"]
                act["template_id"] = pipeline_id_map[imported_template_id]
                act["version"] = pipeline_version_map[imported_template_id]
                if imported_template_id in source_map_info:
                    for key, constant in act["constants"].items():
                        constant["source_info"] = source_map_info[imported_template_id].get(key, {})
        return {
            "result": True,
            "data": None,
            "message": "success",
            "verbose_message": "success",
        }

    @staticmethod
    def _inject_common_child_templates_info(pipeline_tree: dict, common_child_templates: dict):
        """pipeline_tree中注入公共子流程信息"""
        if not common_child_templates:
            return

        activities = pipeline_tree["activities"]
        for activity in activities.values():
            if activity["type"] == "SubProcess" and activity["template_id"] in common_child_templates:
                activity.update(
                    {
                        "template_source": "common",
                        "constants": common_child_templates[activity["template_id"]]["constants"],
                    }
                )
