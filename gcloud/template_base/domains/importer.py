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

from .template_manager import TemplateManager


class TemplateImporter:
    def __init__(self, template_model_cls):
        self.template_model_cls = template_model_cls

    def import_template(self, operator: str, template_data: list) -> dict:
        manager = TemplateManager(template_model_cls=self.template_model_cls)
        import_result = []
        for td in template_data:
            override_template_id = td["override_template_id"]
            name = td["name"]
            pipeline_tree = td["pipeline_tree"]
            description = td["description"]
            if not override_template_id:
                import_result.append(
                    manager.create(
                        name=name,
                        creator=operator,
                        pipeline_tree=pipeline_tree,
                        template_kwargs={},
                        description=description,
                    )
                )
            else:
                template = self.template_model_cls.objects.get(id=override_template_id)
                import_result.append(
                    manager.update(
                        template=template,
                        editor=operator,
                        name=name,
                        pipeline_tree=pipeline_tree,
                        description=description,
                    )
                )
        return import_result
