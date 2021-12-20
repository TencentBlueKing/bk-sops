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

import base64
import hashlib
import logging
from functools import partial

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
    check_digest = partial(check_template_digest, templates_data=templates_data, data_digest=data["digest"])

    if not check_digest(salt=settings.TEMPLATE_DATA_SALT):
        if not check_digest(salt=settings.OLD_COMMUNITY_TEMPLATE_DATA_SALT):
            return {"result": False, "message": "Invalid template data", "code": err_code.VALIDATION_ERROR.code}
    return {"result": True, "data": data, "code": err_code.SUCCESS.code}


def check_template_digest(templates_data, data_digest, salt):
    data_string = (json.dumps(templates_data, sort_keys=True) + salt).encode("utf-8")
    digest = hashlib.md5(data_string).hexdigest()

    is_data_valid = digest == data_digest
    if not is_data_valid:
        return False
    return True


def read_template_data_file(f):
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


def replace_biz_id_value(pipeline_tree: dict, bk_biz_id: int):
    service_acts = [act for act in pipeline_tree["activities"].values() if act["type"] == "ServiceActivity"]
    for act in service_acts:
        act_info = act["component"]["data"]
        bk_biz_id_field = act_info.get("biz_cc_id") or act_info.get("bk_biz_id")
        if bk_biz_id_field and (not bk_biz_id_field["hook"]):
            bk_biz_id_field["value"] = bk_biz_id

        for constant in pipeline_tree["constants"].values():
            if (
                constant["source_tag"].endswith(".biz_cc_id") or constant["source_tag"].endswith(".bk_biz_id")
            ) and constant["value"]:
                constant["value"] = bk_biz_id
