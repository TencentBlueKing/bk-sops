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
import time
import traceback

from django.conf import settings
from django.http import JsonResponse
from cryptography.fernet import Fernet
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from blueapps.account.decorators import login_exempt

import env
from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.taskflow3.domains.dispatchers import NodeCommandDispatcher

logger = logging.getLogger("root")


@login_exempt
@csrf_exempt
@require_POST
def node_callback(request, token):
    logger.info("[node_callback]callback body for token({}): {}".format(token, request.body))

    try:
        f = Fernet(settings.CALLBACK_KEY)
        back_load = f.decrypt(bytes(token, encoding="utf8")).decode().split(":")

        # 不带 root_pipeline_id 的回调 payload
        if len(back_load) == 3:
            root_pipeline_id, engine_ver, node_id, node_version = None, int(back_load[0]), back_load[1], back_load[2]

        # 携带了 root_pipeline_id 的回调 payload
        elif len(back_load) == 4:
            root_pipeline_id, engine_ver, node_id, node_version = (
                back_load[0],
                int(back_load[1]),
                back_load[2],
                back_load[3],
            )
        else:
            logger.error("invalid backload: %s" % back_load)
    except Exception:
        logger.warning("invalid token %s" % token)
        return JsonResponse({"result": False, "message": "invalid token"}, status=400)

    try:
        callback_data = json.loads(request.body)
    except Exception:
        logger.warning("node callback error: %s" % traceback.format_exc())
        return JsonResponse({"result": False, "message": "invalid request body"}, status=400)

    taskflow_id = None
    if root_pipeline_id:
        qs = TaskFlowInstance.objects.filter(pipeline_instance__instance_id=root_pipeline_id).values_list(
            "id", flat=True
        )
        if qs.exists():
            taskflow_id = qs[0]

    dispatchers = NodeCommandDispatcher(engine_ver=engine_ver, node_id=node_id, taskflow_id=taskflow_id)

    # 由于回调方不一定会进行多次回调，这里为了在业务层防止出现不可抗力（网络，DB 问题等）导致失败
    # 增加失败重试机制
    for _ in range(env.NODE_CALLBACK_RETRY_TIMES):
        callback_result = dispatchers.dispatch(
            command="callback", operator="", version=node_version, data=callback_data
        )
        logger.info(
            "result of callback call(token: {} engine_ver: {} node_id: {}, node_version: {}): {}".format(
                token, engine_ver, node_id, node_version, callback_result
            )
        )
        if callback_result["result"]:
            break
        # 考虑callback时Process状态还没及时修改为sleep的情况
        time.sleep(0.5)

    return JsonResponse(callback_result)
