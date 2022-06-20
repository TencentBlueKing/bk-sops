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

from jsonschema import Draft4Validator

from pipeline.validators import validate_pipeline_tree

from pipeline_web import exceptions
from pipeline_web.parser.schemas import WEB_PIPELINE_SCHEMA, KEY_PATTERN_RE


def validate_web_pipeline_tree(web_pipeline_tree):
    # schema validate
    valid = Draft4Validator(WEB_PIPELINE_SCHEMA)
    errors = []
    for error in sorted(valid.iter_errors(web_pipeline_tree), key=str):
        errors.append("%s: %s" % ("→".join(map(str, error.absolute_path)), error.message))
    if errors:
        raise exceptions.ParserWebTreeException(",".join(errors))

    # constants key pattern validate
    key_validation_erros = []
    for key, const in web_pipeline_tree["constants"].items():
        key_value = const.get("key")
        if key != key_value:
            key_validation_erros.append("constants {} key property value: {} not matched".format(key, key_value))
            continue

        if not KEY_PATTERN_RE.match(key):
            key_validation_erros.append("invalid key: {}".format(key))

    # outputs key pattern validate
    for output_key in web_pipeline_tree["outputs"]:
        if not KEY_PATTERN_RE.match(output_key):
            key_validation_erros.append("invalid outputs key: {}".format(key))

    if key_validation_erros:
        raise exceptions.ParserWebTreeException("\n".join(key_validation_erros))

    validate_pipeline_tree(web_pipeline_tree, cycle_tolerate=True)
