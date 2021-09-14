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
from typing import Any
import logging
import yaml

from gcloud.template_base.domains.schema_converter import YamlSchemaConverter

logger = logging.getLogger("root")


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

    @staticmethod
    def load_yaml_docs(stream: Any):
        """导入Yaml数据文件，返回Yaml字段格式流程列表"""
        try:
            yaml_docs = list(yaml.load_all(stream, Loader=yaml.FullLoader))
        except yaml.YAMLError as e:
            logger.exception("[load_yaml_docs]: {}".format(e))
            return {"result": False, "data": None, "message": e}
        return {"result": True, "data": yaml_docs, "message": ""}
