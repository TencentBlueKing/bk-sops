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
import logging
from functools import partial
from typing import Dict, List, Optional, Tuple

import ujson as json
from django.apps import apps
from django.utils.translation import ugettext_lazy as _
from pipeline.core.constants import PE

from gcloud import err_code
from gcloud.conf import settings
from gcloud.constants import COMMON, PROJECT

logger = logging.getLogger("root")


def read_encoded_template_data(content):
    try:
        data = json.loads(base64.b64decode(content))
    except Exception:
        message = _("模板解析失败: 文件解析异常, 模板参数缺陷. 请重试或联系管理员处理 | read_encoded_template_data")
        logger.error(message)
        return {"result": False, "message": message, "code": err_code.REQUEST_PARAM_INVALID.code}

    # check the validation of file
    templates_data = data["template_data"]
    check_digest = partial(check_template_digest, templates_data=templates_data, data_digest=data["digest"])

    if not check_digest(salt=settings.TEMPLATE_DATA_SALT):
        if not check_digest(salt=settings.OLD_COMMUNITY_TEMPLATE_DATA_SALT):
            message = _("模板解析失败: 文件解析异常, 模板参数非法. 请重试或联系管理员处理 | read_encoded_template_data")
            logger.error(message)
            return {"result": False, "message": message, "code": err_code.VALIDATION_ERROR.code}
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
            subprocess_template_model = (
                apps.get_model("template", "CommonTemplate") if act.get("template_source") == COMMON else template_model
            )
            if not reverse:
                act["template_id"] = subprocess_template_model.objects.get(
                    pk=act["template_id"]
                ).pipeline_template.template_id
            else:
                template = subprocess_template_model.objects.get(pipeline_template__template_id=act["template_id"])
                act["template_id"] = str(template.pk)


def inject_template_node_id(pipeline_tree: dict):
    """pipeline_tree需要在unfold_subprocess之后才可递归处理"""
    for act_id, act in pipeline_tree[PE.activities].items():
        act["template_node_id"] = act.get("template_node_id") or act_id
        if act[PE.type] == PE.SubProcess:
            if "pipeline_tree" in act:
                inject_template_node_id(act["pipeline_tree"])
            if "pipeline" in act:
                inject_template_node_id(act["pipeline"])


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


def fill_default_version_to_service_activities(pipeline_tree):
    """
    填充默认版本到 ServiceActivity 类型的节点，避免因导出数据版本丢失导致流程导入后无法正常执行
    :param pipeline_tree:
    :return:
    """
    service_acts = [act for act in pipeline_tree["activities"].values() if act["type"] == "ServiceActivity"]
    for act in service_acts:
        if not act.get("version"):
            act["version"] = "legacy"
        if not act["component"].get("version"):
            act["component"]["version"] = "legacy"


def fetch_templates_info(
    pipeline_template_ids: List,
    fetch_fields: Tuple,
    appointed_template_type: Optional[str] = None,
) -> List[Dict]:
    """
    根据pipeline template id列表获取上层template数据，
    :param pipeline_template_ids: PipelineTemplate id 列表
    :param fetch_fields: 返回的模版包含的字段
    :param appointed_template_type: 搜索的模版类型，common/project/None，None表示不指定类型
    :return: 模版信息列表，不保证返回数据与输入id一一对应
    """

    def get_templates(template_model):
        template_qs = template_model.objects.filter(pipeline_template_id__in=pipeline_template_ids).values(
            *fetch_fields
        )
        template_type = COMMON if template_model.__name__ == "CommonTemplate" else PROJECT
        return [{"template_type": template_type, **template} for template in template_qs]

    task_template_model = apps.get_model("tasktmpl3", "TaskTemplate")
    common_template_model = apps.get_model("template", "CommonTemplate")
    if appointed_template_type:
        templates = get_templates(common_template_model if appointed_template_type == COMMON else task_template_model)
    else:
        task_templates = get_templates(task_template_model)
        common_templates = (
            get_templates(common_template_model) if len(pipeline_template_ids) > len(task_templates) else []
        )
        templates = task_templates + common_templates
    return templates
