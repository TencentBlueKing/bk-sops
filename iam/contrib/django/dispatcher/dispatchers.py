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


try:
    import ujson as json
except Exception:
    import json

import logging

from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from iam.resource.dispatcher import ResourceApiDispatcher
from iam.resource.provider import ResourceProvider
from iam.resource.utils import get_page_obj, get_filter_obj
from iam.exceptions import AuthInvalidOperation

from iam.contrib.django.dispatcher.exceptions import InvalidPageException

logger = logging.getLogger("iam")


def fail_response(code, message, request_id):
    response = JsonResponse({"code": code, "result": False, "message": message, "data": None})
    response["X-Request-Id"] = request_id
    return response


def success_response(data, request_id):
    response = JsonResponse({"code": 0, "result": True, "message": "", "data": data})
    response["X-Request-Id"] = request_id
    return response


class DjangoBasicResourceApiDispatcher(ResourceApiDispatcher):
    def __init__(self, iam, system):
        self.iam = iam
        self.system = system
        self._provider = {}

    def register(self, provider_type, provider):
        if not issubclass(type(provider), ResourceProvider):
            raise AuthInvalidOperation("provider must be subclass of iam.resource.provider.ResourceProvider")

        if provider_type in self._provider:
            raise AuthInvalidOperation("provider {} already been registered".format(provider_type))

        self._provider[provider_type] = provider

    def as_view(self, decorators=[]):
        @csrf_exempt
        def view(request):
            return self._dispatch(request)

        for dec in decorators:
            view = dec(view)

        return view

    def _dispatch(self, request):

        request_id = request.META.get("HTTP_X_REQUEST_ID", "")

        # auth check
        auth = request.META.get("HTTP_AUTHORIZATION", "")
        auth_allowed = self.iam.is_basic_auth_allowed(self.system, auth)

        if not auth_allowed:
            logger.info("resource request({}) auth failed with auth param: {}".format(request_id, auth))
            return fail_response(401, "basic auth failed", request_id)

        # load json data
        try:
            data = json.loads(request.body)
        except Exception:
            logger.info("resource request({}) failed with invalid body: {}".format(request_id, request.body))
            return fail_response(400, "reqeust body is not a valid json", request_id)

        # check basic params
        method = data.get("method")
        resource_type = data.get("type")
        if not (method and resource_type):
            logger.info("resource request({}) failed with invalid data: {}".format(request_id, data))
            return fail_response(400, "method and type is required field", request_id)

        # check resource type
        if resource_type not in self._provider:
            logger.info(
                "resource request({}) failed with unsupport resource type: {}".format(request_id, resource_type)
            )
            return fail_response(404, "unsupport resource type: {}".format(resource_type), request_id)

        # check method and process
        processor = getattr(self, "_dispatch_{}".format(method), None)
        if not processor:
            logger.info("resource request({}) failed with unsupport method: {}".format(request_id, method))
            return fail_response(404, "unsupport method: {}".format(method), request_id)

        logger.info(
            "resource request({}) with filter: {}, page: {}".format(request_id, data.get("filter"), data.get("page"))
        )
        try:
            return processor(request, data, request_id)
        except InvalidPageException as e:
            return fail_response(422, str(e), request_id)
        except Exception as e:
            logger.exception("resource request({}) failed with exception: {}".format(request_id, e))
            return fail_response(500, str(e), request_id)

    def _get_options(self, request):
        return {"language": request.META.get("HTTP_BLUEKING_LANGUAGE", "zh-cn")}

    def _dispatch_list_attr(self, request, data, request_id):
        options = self._get_options(request)

        provider = self._provider[data["type"]]

        pre_process = getattr(provider, "pre_list_attr", None)
        if pre_process and callable(pre_process):
            pre_process(**options)

        result = provider.list_attr(**options)

        return success_response(result.to_list(), request_id)

    def _dispatch_list_attr_value(self, request, data, request_id):
        options = self._get_options(request)

        filter_obj = get_filter_obj(data.get("filter"), ["attr", "keyword", "ids"])
        page_obj = get_page_obj(data.get("page"))

        provider = self._provider[data["type"]]

        pre_process = getattr(provider, "pre_list_attr_value", None)
        if pre_process and callable(pre_process):
            pre_process(filter_obj, page_obj, **options)

        result = provider.list_attr_value(filter_obj, page_obj, **options)

        return success_response(result.to_dict(), request_id)

    def _dispatch_list_instance(self, request, data, request_id):
        options = self._get_options(request)

        filter_obj = get_filter_obj(data.get("filter"), ["parent", "search", "resource_type_chain"])
        page_obj = get_page_obj(data.get("page"))

        provider = self._provider[data["type"]]

        pre_process = getattr(provider, "pre_list_instance", None)
        if pre_process and callable(pre_process):
            pre_process(filter_obj, page_obj, **options)

        result = provider.list_instance(filter_obj, page_obj, **options)

        return success_response(result.to_dict(), request_id)

    def _dispatch_fetch_instance_info(self, request, data, request_id):
        options = self._get_options(request)

        filter_obj = get_filter_obj(data.get("filter"), ["ids", "attrs"])

        provider = self._provider[data["type"]]

        pre_process = getattr(provider, "pre_fetch_instance_info", None)
        if pre_process and callable(pre_process):
            pre_process(filter_obj, **options)

        result = provider.fetch_instance_info(filter_obj, **options)

        return success_response(result.to_list(), request_id)

    def _dispatch_list_instance_by_policy(self, request, data, request_id):
        options = self._get_options(request)

        filter_obj = get_filter_obj(data.get("filter"), ["expression"])
        page_obj = get_page_obj(data.get("page"))

        provider = self._provider[data["type"]]

        pre_process = getattr(provider, "pre_list_instance_by_policy", None)
        if pre_process and callable(pre_process):
            pre_process(filter_obj, page_obj, **options)

        result = provider.list_instance_by_policy(filter_obj, page_obj, **options)

        return success_response(result.to_list(), request_id)
