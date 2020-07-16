# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import base64
import hashlib
import logging

import ujson as json

from pipeline.core.constants import PE

from gcloud import err_code
from gcloud.conf import settings

logger = logging.getLogger("root")


def read_encoded_template_data(content):
    try:
        data = json.loads(base64.b64decode(content))
    except Exception:
        return {"result": False, "message": "Template data is corrupt", "code": err_code.REQUEST_PARAM_INVALID.code}

    # check the validation of file
    templates_data = data["template_data"]
    data_string = (json.dumps(templates_data, sort_keys=True) + settings.TEMPLATE_DATA_SALT).encode("utf-8")
    digest = hashlib.md5(data_string).hexdigest()

    is_data_valid = digest == data["digest"]
    if not is_data_valid:
        return {"result": False, "message": "Invalid template data", "code": err_code.VALIDATION_ERROR.code}

    return {"result": True, "data": data, "code": err_code.SUCCESS.code}


def read_template_data_file(f):
    if not f:
        return {"result": False, "message": "Upload template dat file please."}

    return read_encoded_template_data(content=f.read())


def replace_template_id(template_model, pipeline_data, reverse=False):
    activities = pipeline_data[PE.activities]
    for act_id, act in list(activities.items()):
        if act["type"] == PE.SubProcess:
            if not reverse:
                act["template_id"] = template_model.objects.get(pk=act["template_id"]).pipeline_template.template_id
            else:
                template = template_model.objects.get(pipeline_template__template_id=act["template_id"])
                act["template_id"] = str(template.pk)
