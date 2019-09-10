# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import logging
import traceback

from pipeline.core.constants import PE

from pipeline.core.flow.io import ItemSchema
from pipeline.core.data.library import VariableLibrary
from pipeline.component_framework.library import ComponentLibrary

logger = logging.getLogger('root')

VAR_SOURCE_TYPE_CUSTOM = 'custom'
VAR_SOURCE_TYPE_INPUTS = 'component_inputs'


def add_schema_for_input_vars(pipeline_tree):
    for var in pipeline_tree.get(PE.constants, {}).values():
        try:
            var['schema'] = SchemaFactory.schema_for_var(var)
        except Exception:
            var['schema'] = None
            logger.error('error occurred when get schema for var {var}, error: {trace}'.format(
                var=var, trace=traceback.format_exc()))

    return pipeline_tree


class SchemaFactory(object):
    accept_var_type = {VAR_SOURCE_TYPE_CUSTOM, VAR_SOURCE_TYPE_INPUTS}

    @classmethod
    def _schema_check(cls, code, var, schema, type):
        if not schema:
            return False, 'can not find schema for {type} {code}, var: {var}'.format(type=type, code=code, var=var)

        if not isinstance(schema, ItemSchema):
            return False, 'schema of {type} {code} is not instance of ItemSchema'.format(type=type, code=code)

        return True, ''

    @classmethod
    def decode_source_tag(cls, source_tag):
        if not source_tag:
            return None, None

        segments = source_tag.split('.')
        code, tag = segments[0], segments[1]

        return code, tag

    @classmethod
    def schema_for_var(cls, var):
        source_type = var.get('source_type')
        if source_type not in cls.accept_var_type:
            return None

        source_tag = var.get('source_tag')
        try:
            code, tag = cls.decode_source_tag(source_tag)
        except Exception:
            logger.error('error occurred when decode source_tag for {key}, var: {var}, error: {trace}'.format(
                key=var.get('key'), var=var, trace=traceback.format_exc()))
            return None

        if source_type == VAR_SOURCE_TYPE_INPUTS:
            component_cls = ComponentLibrary.get_component_class(component_code=code)
            # maybe custom var from subprocess
            if not component_cls:
                source_type = VAR_SOURCE_TYPE_CUSTOM
            else:
                schema = component_cls.get_input_schema(key=tag)

                ok, message = cls._schema_check(code=code, var=var, schema=schema, type='component')
                if not ok:
                    logger.error(message)
                    return None

                return schema.as_dict()

        if source_type == VAR_SOURCE_TYPE_CUSTOM:
            var_cls = VariableLibrary.get_var_class(code=code)
            schema = getattr(var_cls, 'schema', None)

            ok, message = cls._schema_check(code=code, var=var, schema=schema, type='variable')
            if not ok:
                logger.error(message)
                return None

            return schema.as_dict()
