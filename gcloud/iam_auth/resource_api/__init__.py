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
import json

from django.conf import settings
from iam.contrib.django.dispatcher import DjangoBasicResourceApiDispatcher
from iam.contrib.django.dispatcher.dispatchers import fail_response, logger
from iam.contrib.django.dispatcher.exceptions import InvalidPageException, KeywordTooShortException

from gcloud.iam_auth import get_iam_client

from .clocked_task import ClockedTaskResourceProvider
from .common_flow import CommonFlowResourceProvider
from .flow import FlowResourceProvider
from .mini_app import MiniAppResourceProvider
from .periodic_task import PeriodicTaskResourceProvider
from .project import ProjectResourceProvider
from .task import TaskResourceProvider


class ResourceApiDispatcher(DjangoBasicResourceApiDispatcher):
    def __init__(self, system):
        self.system = system
        self._provider = {}

    def _get_options(self, request):
        opts = {"language": request.META.get("HTTP_BLUEKING_LANGUAGE", "zh-cn")}
        if "HTTP_X_BK_TENANT_ID" in request.META:
            opts["bk_tenant_id"] = request.META["HTTP_X_BK_TENANT_ID"]
        else:
            opts["bk_tenant_id"] = "default"
        return opts

    def _dispatch(self, request):

        request_id = request.META.get("HTTP_X_REQUEST_ID", "")
        tenant_id = request.META.get("HTTP_X_BK_TENANT_ID", "default")

        iam_client = get_iam_client(tenant_id)
        # auth check
        auth = request.META.get("HTTP_AUTHORIZATION", "")
        auth_allowed = iam_client.is_basic_auth_allowed(self.system, auth)

        if not auth_allowed:
            logger.error("resource request(%s) auth failed with auth param: %s", request_id, auth)
            return fail_response(401, "basic auth failed", request_id)

        # load json data
        try:
            data = json.loads(request.body)
        except Exception:
            logger.error("resource request(%s) failed with invalid body: %s", request_id, request.body)
            return fail_response(400, "request body is not a valid json", request_id)

        # check basic params
        method = data.get("method")
        resource_type = data.get("type")
        if not (method and resource_type):
            logger.error(
                "resource request(%s) failed with invalid data: %s. method and type required", request_id, data
            )
            return fail_response(400, "method and type is required field", request_id)

        # check resource type
        if resource_type not in self._provider:
            logger.error("resource request(%s) failed with unsupported resource type: %s", request_id, resource_type)
            return fail_response(404, "unsupported resource type: {}".format(resource_type), request_id)

        # check method and process
        processor = getattr(self, "_dispatch_{}".format(method), None)
        if not processor:
            logger.error("resource request(%s) failed with unsupported method: %s", request_id, method)
            return fail_response(404, "unsupported method: {}".format(method), request_id)

        logger.info("resource request(%s) with filter: %s, page: %s", request_id, data.get("filter"), data.get("page"))
        try:
            return processor(request, data, request_id)
        except InvalidPageException as e:
            return fail_response(422, str(e), request_id)
        except KeywordTooShortException as e:
            return fail_response(406, str(e), request_id)
        except Exception as e:
            logger.exception("resource request(%s) failed with exception: %s", request_id, e)
            return fail_response(500, str(e), request_id)


dispatcher = ResourceApiDispatcher(settings.BK_IAM_SYSTEM_ID)
dispatcher.register("project", ProjectResourceProvider())
dispatcher.register("flow", FlowResourceProvider())
dispatcher.register("task", TaskResourceProvider())
dispatcher.register("common_flow", CommonFlowResourceProvider())
dispatcher.register("mini_app", MiniAppResourceProvider())
dispatcher.register("periodic_task", PeriodicTaskResourceProvider())
dispatcher.register("clocked_task", ClockedTaskResourceProvider())
