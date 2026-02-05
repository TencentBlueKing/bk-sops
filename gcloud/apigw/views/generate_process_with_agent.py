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

import json
import logging

from blueapps.account.decorators import login_exempt
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from gcloud import err_code
from gcloud.tasktmpl3.agent_utils import (
    AgentAPIError,
    AgentResponseParseError,
    FlowConversionError,
    FlowLayoutError,
    generate_pipeline_tree,
)

logger = logging.getLogger("root")


@require_POST
@login_exempt
@csrf_exempt
def generate_process_with_agent(request):
    """
    AI 生成流程

    请求方法: POST
    请求体格式: JSON Object
    {
        "bk_biz_id": 业务ID,
        "prompt": "流程描述"
    }
    """
    try:
        request_data = json.loads(request.body)
    except json.JSONDecodeError as e:
        logger.warning("generate_process_with_agent: Invalid JSON format - {}".format(str(e)))
        return JsonResponse(
            {
                "result": False,
                "message": "Invalid JSON format: {}".format(str(e)),
                "code": err_code.REQUEST_PARAM_INVALID.code,
            }
        )

    bk_biz_id = request_data.get("bk_biz_id")
    prompt = request_data.get("prompt")

    if not prompt:
        return JsonResponse(
            {"result": False, "message": "prompt is required", "code": err_code.REQUEST_PARAM_INVALID.code}
        )

    try:
        pipeline_tree = generate_pipeline_tree(prompt, bk_biz_id)
    except (AgentAPIError, AgentResponseParseError) as e:
        return JsonResponse({"result": False, "message": str(e), "code": err_code.UNKNOWN_ERROR.code})
    except FlowConversionError as e:
        return JsonResponse({"result": False, "message": str(e), "code": err_code.REQUEST_PARAM_INVALID.code})
    except FlowLayoutError as e:
        return JsonResponse({"result": False, "message": str(e), "code": err_code.UNKNOWN_ERROR.code})

    return JsonResponse({"result": True, "data": pipeline_tree, "code": err_code.SUCCESS.code, "message": ""})
