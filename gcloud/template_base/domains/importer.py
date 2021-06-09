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

from django.db import transaction

from .template_manager import TemplateManager


class TemplateImporter:
    def __init__(self, template_model_cls):
        self.template_model_cls = template_model_cls

    def import_template(self, operator: str, template_data: list) -> dict:
        """
        以 operator 的身份来导入若干个模板

        :param operator: 操作者
        :type operator: str
        :param template_data: [
            {
                "override_template_id": "要覆盖的模板的主键ID",
                "name": "模板名",
                "pipeline_tree": "dict, 模板 pipeline tree",
                "description": "模板描述"，
                "template_kwargs": "dict, 模板创建关键字参数",
                "id": "str, 模板临时唯一 ID"
            }
        ]
        :type template_data: list
        :return: [description]
        :rtype: dict
        """
        manager = TemplateManager(template_model_cls=self.template_model_cls)
        import_result = []
        pipeline_id_map = {}
        with transaction.atomic():
            for td in template_data:
                override_template_id = td["override_template_id"]
                name = td["name"]
                pipeline_tree = td["pipeline_tree"]
                description = td["description"]

                replace_result = self._replace_subprocess_template_id(pipeline_tree, pipeline_id_map)
                if not replace_result["result"]:
                    import_result.append(replace_result)
                    continue

                if not override_template_id:
                    create_result = manager.create(
                        name=name,
                        creator=operator,
                        pipeline_tree=pipeline_tree,
                        template_kwargs=td["template_kwargs"],
                        description=description,
                    )
                    if create_result["result"]:
                        pipeline_id_map[td["id"]] = create_result["data"].id
                    import_result.append(create_result)
                else:
                    template = self.template_model_cls.objects.get(id=override_template_id)
                    update_result = manager.update(
                        template=template,
                        editor=operator,
                        name=name,
                        pipeline_tree=pipeline_tree,
                        description=description,
                    )
                    if update_result["result"]:
                        pipeline_id_map[td["id"]] = update_result["data"].id
                    import_result.append(update_result)

        return {"result": True, "data": import_result, "message": "success", "verbose_message": "success"}

    def _replace_subprocess_template_id(self, pipeline_tree: dict, pipeline_id_map: dict) -> dict:
        """
        将模板数据中临时的模板 ID 替换成数据库中模型的主键 ID

        :param pipeline_tree: pipeline tree 模板数据
        :type pipeline_tree: dict
        :param pipeline_id_map: Subprocess 节点中临时 ID 到数据库模型主键 ID 的映射
        :type pipeline_id_map: dict
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

                act["template_id"] = pipeline_id_map[act["template_id"]]

        return {
            "result": True,
            "data": None,
            "message": "success",
            "verbose_message": "success",
        }
