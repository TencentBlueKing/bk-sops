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
import json
import logging
import re

from drf_yasg import openapi
from drf_yasg.utils import merge_params
from drf_yasg.inspectors import SwaggerAutoSchema

logger = logging.getLogger("root")


class AnnotationAutoSchema(SwaggerAutoSchema):
    params_regex = re.compile("^param: (?P<key>.*?): (?P<infos>.*?)$")
    response_regex = re.compile("^return: (?P<return_desc>.*?)$")
    body_regex = re.compile("^body: (?P<body_name>.*?)$")
    dict_string_regex = re.compile("^(?P<field_desc>.*?)[(](?P<field_type>.*?)[)]$")
    key_required_regex = re.compile("^(?P<field_desc>.*?)[(](?P<field_require>.*?)[)]$")

    def get_operation(self, operation_keys=None):
        operation = super().get_operation(operation_keys)
        if not hasattr(operation, "summary"):
            operation.summary = operation.description
        parameters, response = self._extract_params_and_returns()
        operation.parameters = merge_params(operation.parameters, parameters)
        if response and not self.overrides.get("responses"):
            operation.responses["200"] = response
        return operation

    def _get_schema_based_on_data(self, data):
        """将对应类型数据转化为Schema对象"""
        if isinstance(data, dict):
            required_properties = []
            properties = {}
            for key, info in data.items():
                key = str(key)
                match_result = self.key_required_regex.match(key)
                if match_result and match_result["field_require"] == "required":
                    key = match_result["field_desc"]
                    required_properties.append(key)
                properties[key] = self._get_schema_based_on_data(info)
            return openapi.Schema(type=openapi.TYPE_OBJECT, properties=properties, required=required_properties)
        elif isinstance(data, list):
            items = (
                self._get_schema_based_on_data(data[0]) if len(data) > 0 else openapi.Schema(type=openapi.TYPE_ARRAY)
            )
            return openapi.Schema(type=openapi.TYPE_ARRAY, items=items)
        elif isinstance(data, str):
            match_result = self.dict_string_regex.match(data)
            desc = match_result["field_desc"] if match_result else data
            field_type = match_result["field_type"] if match_result else openapi.TYPE_STRING
            return openapi.Schema(description=desc, type=field_type)
        else:
            raise TypeError("data {} should be the type of dict or list or string".format(data))

    def _extract_params_and_returns(self, description=None):
        """提取符合格式的接口注释中相关的参数和相应信息，加入对应的参数和响应列表"""
        if description is None:
            description = self.view.get_view_description()
        parameters = []
        response = None
        response_name = ""
        collecting_response_lines = False
        response_lines = []
        body_name = ""
        body_lines = []
        collecting_body_lines = False
        for line in description.splitlines():
            # 处理普通参数
            match_param = self.params_regex.match(line)
            if match_param:
                try:
                    param_key = match_param["key"]
                    param_infos = match_param["infos"].strip()
                    param_required = True if "required" in param_infos else False
                    param_infos = param_infos.split(",")
                    if param_required:
                        param_infos = param_infos[:-1]
                    param_desc, param_type, param_in = (
                        ",".join(param_infos[:-2]),
                        param_infos[-2].strip(),
                        param_infos[-1].strip(),
                    )
                    openapi_param = openapi.Parameter(
                        name=param_key, in_=param_in, description=param_desc, type=param_type, required=param_required,
                    )
                    parameters.append(openapi_param)
                except Exception as e:
                    logger.error(
                        "[AnnotationAutoSchema]: transform param error: {} with annotation: {}".format(e, line)
                    )
                    raise e

            # 处理响应
            match_return = self.response_regex.match(line)
            if match_return:
                response_name = match_return["return_desc"]
                collecting_response_lines = True
                continue

            # 处理body参数情况
            match_body = self.body_regex.match(line)
            if match_body:
                body_name = match_body["body_name"] or "data"
                collecting_body_lines = True
                continue

            if collecting_response_lines:
                response_lines.append(line.strip())
            if collecting_body_lines:
                body_lines.append(line.strip())
            if line == "":
                collecting_response_lines = False
                collecting_body_lines = False

        if response_lines:
            try:
                response_data = json.loads("".join(response_lines))
            except Exception as e:
                logger.error(
                    "[AnnotationAutoSchema]: json loads response_data error: {}, response_data: {})".format(
                        e, "".join(response_lines)
                    )
                )
                raise e
            response = openapi.Response(description=response_name, schema=self._get_schema_based_on_data(response_data))

        if body_lines:
            try:
                body_data = json.loads("".join(body_lines))
            except Exception as e:
                logger.error(
                    "[AnnotationAutoSchema]: json loads body_data error: {}, body_data: {})".format(
                        e, "".join(body_lines)
                    )
                )
                raise e

            body_param = openapi.Parameter(
                name=body_name, in_=openapi.IN_BODY, schema=self._get_schema_based_on_data(body_data)
            )
            parameters.append(body_param)

        return parameters, response

    def should_filter(self):
        if self.overrides.get("ignore_filter_query"):
            return False
        return super(AnnotationAutoSchema, self).should_filter()
