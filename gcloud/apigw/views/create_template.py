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

from datetime import datetime

import ujson as json
from apigw_manager.apigw.decorators import apigw_require
from blueapps.account.decorators import login_exempt
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from gcloud import err_code
from gcloud.apigw.decorators import mark_request_whether_is_trust, project_inject, return_json_response
from gcloud.apigw.views.utils import logger
from gcloud.contrib.audit.utils import bk_audit_add_event
from gcloud.contrib.operate_record.constants import OperateSource, OperateType, RecordType
from gcloud.contrib.operate_record.decorators import record_operation
from gcloud.iam_auth import IAMMeta
from gcloud.iam_auth.intercept import iam_intercept
from gcloud.iam_auth.view_interceptors.apigw import CreateTemplateInterceptor
from gcloud.label.models import Label, TemplateLabelRelation
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.tasktmpl3.signals import post_template_save_commit
from gcloud.template_base.domains.converter_handler import YamlSchemaConverterHandler
from gcloud.template_base.domains.template_manager import TemplateManager
from pipeline_web.drawing_new.drawing import draw_pipeline

manager = TemplateManager(template_model_cls=TaskTemplate)


@login_exempt
@csrf_exempt
@require_POST
@apigw_require
@mark_request_whether_is_trust
@return_json_response
@project_inject
@iam_intercept(CreateTemplateInterceptor())
@record_operation(RecordType.template.name, OperateType.create.name, OperateSource.api.name)
def create_template(request, project_id):
    try:
        params = json.loads(request.body)
    except Exception:
        return {"result": False, "message": "invalid json format", "code": err_code.REQUEST_PARAM_INVALID.code}

    # name 空时，与前端一致生成默认名称
    name = params.get("name")
    description = params.get("description", "")
    pipeline_tree = params.get("pipeline_tree")
    if not pipeline_tree:
        return {"result": False, "message": "pipeline_tree is required", "code": err_code.REQUEST_PARAM_INVALID.code}

    input_format = params.get("format", "json")
    if input_format == "yaml":
        if not isinstance(pipeline_tree, str):
            return {
                "result": False,
                "message": "pipeline_tree must be a YAML string when format=yaml",
                "code": err_code.REQUEST_PARAM_INVALID.code,
            }
        converter_handler = YamlSchemaConverterHandler("v1")
        load_result = converter_handler.load_yaml_docs(pipeline_tree)
        if not load_result["result"]:
            return {
                "result": False,
                "message": "invalid YAML: {}".format(load_result["message"]),
                "code": err_code.REQUEST_PARAM_INVALID.code,
            }
        try:
            convert_result = converter_handler.reconvert(load_result["data"])
        except Exception as e:
            logger.exception("[API] create_template reconvert yaml failed: %s", e)
            return {
                "result": False,
                "message": "YAML reconvert failed: {}".format(str(e)),
                "code": err_code.REQUEST_PARAM_INVALID.code,
            }
        if not convert_result["result"]:
            return {
                "result": False,
                "message": "YAML reconvert failed: {}".format(convert_result["message"]),
                "code": err_code.REQUEST_PARAM_INVALID.code,
            }
        template_order = convert_result["data"]["template_order"]
        templates = convert_result["data"]["templates"]
        if not template_order:
            return {
                "result": False,
                "message": "YAML contains no valid template",
                "code": err_code.REQUEST_PARAM_INVALID.code,
            }
        if len(template_order) > 1:
            logger.warning(
                "[API] create_template: YAML contains %d templates, only the first will be imported",
                len(template_order),
            )
        first_template_id = template_order[0]
        first_template = templates[first_template_id]
        pipeline_tree = first_template["tree"]
        name = name or first_template.get("name")
        description = description or first_template.get("description", "")
    else:
        # pipeline_tree 支持传入 dict 或 JSON 字符串
        if isinstance(pipeline_tree, str):
            try:
                pipeline_tree = json.loads(pipeline_tree)
            except Exception:
                return {
                    "result": False,
                    "message": "pipeline_tree is not a valid JSON string",
                    "code": err_code.REQUEST_PARAM_INVALID.code,
                }

    name = name or "new{}".format(datetime.now().strftime("%Y%m%d%H%M%S"))

    # location 自动排版
    try:
        draw_pipeline(pipeline_tree)
    except Exception as e:
        logger.warning("[API] create_template draw_pipeline failed: %s, skip auto layout", e)

    creator = request.user.username
    project = request.project
    category = params.get("category", "Default")
    notify_type = params.get("notify_type", {"success": [], "fail": []})
    notify_receivers = params.get("notify_receivers", {"receiver_group": [], "more_receiver": ""})
    time_out = params.get("timeout", 20)
    default_flow_type = params.get("default_flow_type", "common")
    template_labels = params.get("template_labels", [])
    executor_proxy = params.get("executor_proxy", "")

    logger.info(
        "[API] create_template info, project_id: %s, name: %s, creator: %s",
        project.id,
        name,
        creator,
    )

    try:
        with transaction.atomic():
            # 1. 创建 PipelineTemplate
            result = manager.create_pipeline(
                name=name, creator=creator, pipeline_tree=pipeline_tree, description=description
            )
            if not result["result"]:
                logger.error(result["message"])
                return {
                    "result": False,
                    "message": result["message"],
                    "code": err_code.REQUEST_PARAM_INVALID.code,
                }

            # 2. 创建 TaskTemplate
            template = TaskTemplate.objects.create(
                project=project,
                pipeline_template_id=result["data"].template_id,
                category=category,
                notify_type=json.dumps(notify_type) if isinstance(notify_type, (dict, list)) else notify_type,
                notify_receivers=json.dumps(notify_receivers)
                if isinstance(notify_receivers, dict)
                else notify_receivers,
                time_out=time_out,
                default_flow_type=default_flow_type,
                executor_proxy=executor_proxy,
            )

            # 3. 同步模板标签
            if template_labels:
                if not Label.objects.check_label_ids(template_labels):
                    raise ValueError("template_labels contain invalid label ids")
                TemplateLabelRelation.objects.set_labels_for_template(template.id, template_labels)

    except ValueError as e:
        return {"result": False, "message": str(e), "code": err_code.REQUEST_PARAM_INVALID.code}
    except Exception as e:
        logger.exception("[API] create_template error: %s", e)
        return {"result": False, "message": str(e), "code": err_code.UNKNOWN_ERROR.code}

    # 4. 事务提交后发送信号
    post_template_save_commit.send(
        sender=TaskTemplate,
        project_id=template.project_id,
        template_id=template.id,
        is_deleted=False,
    )

    # 5. 审计上报
    bk_audit_add_event(
        username=creator,
        action_id=IAMMeta.FLOW_CREATE_ACTION,
        resource_id=IAMMeta.FLOW_RESOURCE,
        instance=template,
    )

    return {
        "result": True,
        "data": {
            "template_id": template.id,
            "template_name": template.name,
            "pipeline_template_id": template.pipeline_template_id,
        },
        "code": err_code.SUCCESS.code,
        "message": "success",
    }
