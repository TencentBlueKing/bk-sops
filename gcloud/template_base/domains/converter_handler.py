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

from gcloud.template_base.domains.schema_converter import YamlSchemaConverter


class YamlSchemaConverterHandler:
    _schema_converters = {YamlSchemaConverter.VERSION: YamlSchemaConverter}

    def __init__(self, version: str):
        if version not in self._schema_converters:
            raise Exception("schema converter of version {} does not found.".format(version))
        self.converter = self._schema_converters.get(version)()

    def convert(self, data: dict):
        """从原始数据字段转换成Yaml数据字段"""
        return self.converter.convert(data)

    def reconvert(self, yaml_docs: list):
        """从Yaml数据字段转换成原始数据字段"""
        return self.converter.reconvert(yaml_docs)

    def reconvert_with_override_id(self, yaml_docs: list, override_mappings: dict):
        """从Yaml数据字段转换成原始数据字段，同时添加"""
        reconvert_result = self.reconvert(yaml_docs)
        if not reconvert_result["result"]:
            return reconvert_result
        templates, orders = reconvert_result["templates"], reconvert_result["template_order"]
        reconverted_templates = []
        for template_id in orders:
            if template_id in override_mappings:
                templates[template_id].update({"override_template_id": override_mappings[template_id]})
            reconverted_templates.append(templates[template_id])
        return {"result": True, "data": reconverted_templates, "message": []}
