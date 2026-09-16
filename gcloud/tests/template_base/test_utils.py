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

import base64
import hashlib

import ujson as json
from django.test import SimpleTestCase

from gcloud.conf import settings
from gcloud.template_base.utils import read_encoded_template_data


def encoded_template_data(template_data):
    data = {
        "template_data": template_data,
        "digest": check_template_digest_value(template_data),
    }
    return base64.b64encode(json.dumps(data).encode("utf-8"))


def check_template_digest_value(template_data):
    raw = (json.dumps(template_data, sort_keys=True) + settings.TEMPLATE_DATA_SALT).encode("utf-8")
    return hashlib.md5(raw).hexdigest()


class ReadTemplateDataFileTestCase(SimpleTestCase):
    def test_missing_pipeline_template_reference_is_rejected(self):
        template_data = {
            "template": {"1": {"id": 1, "pipeline_template_str_id": None}},
            "pipeline_template_data": {"template": {}},
        }

        result = read_encoded_template_data(encoded_template_data(template_data))

        self.assertFalse(result["result"])
        self.assertIn("流程 [1] 缺少关联的流程定义", str(result["message"]))

    def test_unknown_pipeline_template_reference_is_rejected(self):
        template_data = {
            "template": {"1": {"id": 1, "pipeline_template_str_id": "missing"}},
            "pipeline_template_data": {"template": {"existing": {"name": "flow"}}},
        }

        result = read_encoded_template_data(encoded_template_data(template_data))

        self.assertFalse(result["result"])
        self.assertIn("流程 [1] 关联的流程定义不存在", str(result["message"]))

    def test_valid_pipeline_template_reference_is_accepted(self):
        template_data = {
            "template": {"1": {"id": 1, "pipeline_template_str_id": "pipeline-1"}},
            "pipeline_template_data": {"template": {"pipeline-1": {"name": "flow"}}},
        }

        result = read_encoded_template_data(encoded_template_data(template_data))

        self.assertTrue(result["result"])

    def test_pipeline_template_id_recovers_missing_string_reference(self):
        template_data = {
            "template": {
                "1": {
                    "id": 1,
                    "pipeline_template_id": "pipeline-1",
                    "pipeline_template_str_id": None,
                }
            },
            "pipeline_template_data": {"template": {"pipeline-1": {"name": "flow"}}},
        }

        result = read_encoded_template_data(encoded_template_data(template_data))

        self.assertTrue(result["result"])
        self.assertEqual(
            result["data"]["template_data"]["template"]["1"]["pipeline_template_str_id"],
            "pipeline-1",
        )

    def test_incomplete_pipeline_template_is_rejected(self):
        template_data = {
            "template": {"1": {"id": 1, "pipeline_template_str_id": "pipeline-1"}},
            "pipeline_template_data": {"template": {"pipeline-1": {}}},
        }

        result = read_encoded_template_data(encoded_template_data(template_data))

        self.assertFalse(result["result"])
        self.assertIn("流程 [1] 关联的流程定义数据不完整", str(result["message"]))
