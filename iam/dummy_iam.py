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

from django.db.models import Q

from .api.client import Client
from .eval.object import ObjectSet
from .contrib.converter.queryset import DjangoQuerySetConverter
from .auth.models import Request, MultiActionRequest, Resource, ApiAuthRequest
from .exceptions import AuthAPIError, AuthInvalidRequest, AuthInvalidParam
from .apply.models import Application


class DummyIAM(object):
    """
    input: object
    """

    def __init__(self, app_code, app_secret, bk_iam_host, bk_paas_host):
        self._client = Client(app_code, app_secret, bk_iam_host, bk_paas_host)

    def _do_policy_query(self, request, with_resources=True):
        return []

    def _do_policy_query_with_cache(self, request):
        return self._do_policy_query(request)

    def _do_policy_query_by_actions(self, request, with_resources=True):
        return []

    def _eval_expr(self, expr, obj_set):
        return True

    def _eval_policy(self, policy, obj_set):
        return True

    def _build_object_set(self, system, resources, only_local=False):
        obj_set = ObjectSet()

        resource_id_list = []

        # if no resources or resources is None
        if not resources:
            return obj_set, ""

        for resource in resources:
            # only local resource need to be calculated
            # 跨系统资源依赖的策略在服务端就计算完了, 策略表达式中只会存在本系统的
            if only_local and (resource.system != system):
                continue

            attrs = resource.attribute
            attrs["id"] = resource.id
            obj_set.add_object(resource.type, attrs)

            resource_id_list.append((resource.type, resource.id))

        # 如果只有一个本地资源, 直接返回不带类型的ID;
        # [("flow", "1")]   => "1"
        # 如果存在层级资源 返回 {type},{id}/{type2},{id2}
        # [("cluster", "a"), ("area", "b")) =>  "cluster,a/area,b"

        # NOTE: 这里不会存在=> 跨系统资源依赖=>上面已经过滤掉了
        # [("job", "script", "a"), ("cmdb", "host", "b")) =>  "job:script,a/cmdb:host,b"

        resource_id = ""
        if len(resource_id_list) == 1:
            resource_id = resource_id_list[0][1]
        else:
            resource_id = "/".join(["%s,%s" % (a[0], a[1]) for a in resource_id_list])

        return obj_set, resource_id

    def _validate_request(self, request):
        if not isinstance(request, Request):
            raise AuthInvalidRequest("request should be instance of iam.auth.models.Request")

        request.validate()

    def _validate_multi_action_request(self, request):
        if not isinstance(request, MultiActionRequest):
            raise AuthInvalidRequest("request should be instance of iam.auth.models.MultiActionRequest")

        request.validate()

    def _validate_resources_list(self, resources_list):
        # resources_list = [resources] = [[Resource], [Resource]]
        if not isinstance(resources_list, list):
            raise AuthInvalidParam("resources_list should be list of [iam.auth.models.Resource]")

        if not all([isinstance(r, list) for r in resources_list]):
            raise AuthInvalidParam("resources_list should be list of [iam.auth.models.Resource]")

        if not all([isinstance(i, Resource) for r in resources_list for i in r]):
            raise AuthInvalidParam("resources should be list of iam.auth.models.Resource")

    def _validate_resources_list_same_local_only(self, system, resources_list):
        # 校验, resources_list中只能是本地同一类的资源
        resource_types = {}
        for rs in resources_list:
            for r in rs:
                if system != r.system:
                    raise AuthInvalidParam(
                        "resources_list not support auth for resource belong other system: %s" % r.system
                    )
                resource_types[r.type] = 1

        if len(resource_types) != 1:
            raise AuthInvalidParam(
                "resources_list should all with the same resource_type, but got %s" % resource_types.keys()
            )

    def is_allowed_with_cache(self, request):
        return self.is_allowed(request)

    def is_allowed(self, request):
        """
        单个资源是否有权限校验
        request中会带resource到IAM, IAM会进行两阶段计算, 即resources也会参与到计算中

        支持:
        - 本地资源 resources中只有本地资源
        - 跨系统资源依赖 resources中有本地也有远程资源 (此时resoruces一定要传, 因为需要IAM帮助获取跨系统资源)
        """
        return True

    def batch_is_allowed(self, request, resources_list):
        """
        多个资源是否有权限校验
        request中不会带resource到IAM, IAM不会会进行两阶段计算, 直接返回system+action+subejct的所有策略
        然后逐一计算

        - 一次策略查询, 多次计算

        支持:
        - 本地资源 resources中只有本地资源
        - **不支持**跨系统资源依赖
        """
        # NOTE: 不向服务端传任何resource
        result = {}
        for resources in resources_list:
            _, resource_id = self._build_object_set(request.system, resources, only_local=False)
            result[resource_id] = True
        return result

    def resource_multi_actions_allowed(self, request):
        """
        单个资源多个action是否有权限校验
        request中会带resource到IAM, IAM会进行两阶段计算, 即resources也会参与到计算中

        支持:
        - 本地资源 resources中只有本地资源
        - 跨系统资源依赖 resources中有本地也有远程资源 (此时resoruces一定要传, 因为需要IAM帮助获取跨系统资源)
        """
        actions_allowed = {}
        for a in request.to_dict()["actions"]:
            action = a["id"]
            actions_allowed[action] = True
        return actions_allowed

    def batch_resource_multi_actions_allowed(self, request, resources_list):
        """
        批量资源多个action是否有权限校验
        request中会带resource到IAM, IAM会进行两阶段计算, 即resources也会参与到计算中

        支持:
        - 本地资源 resources中只有本地资源
        - **不支持**跨系统资源依赖
        """
        resources_actions_perms = {}
        for resources in resources_list:
            for a in request.to_dict()["actions"]:
                action = a["id"]
                obj_set, resource_id = self._build_object_set(request.system, resources, only_local=False)
                resources_actions_perms.setdefault(resource_id, {})[action] = True
        return resources_actions_perms

    def make_filter(self, request, converter_class=DjangoQuerySetConverter, key_mapping=None):
        return ~Q(pk=None)

    # TODO: add the register model apis
    def get_token(self, system):
        # bool, message, token
        return self._client.get_token(system)

    def is_basic_auth_allowed(self, system, basic_auth):
        return True

    def get_apply_url(self, application, bk_token=None, bk_username=None):
        if isinstance(application, dict):
            data = application
        elif isinstance(application, Application):
            # do validate
            application.validate()
            data = application.to_dict()
        else:
            raise AuthInvalidRequest("application shuld be instance of dict or iam.apply.modles.Application")

        if not (bk_token or bk_username):
            raise AuthInvalidRequest("bk_token and bk_username can not both be empty")

        # bool, message, url
        return self._client.get_apply_url(bk_token, bk_username, data)

    def grant_resource_creator_actions(self, application, bk_token=None, bk_username=None):
        return True, "success"

    def grant_resource_creator_action_attributes(self, application, bk_token=None, bk_username=None):
        return True, "success"

    def grant_batch_resource_creator_actions(self, application, bk_token=None, bk_username=None):
        return True, "success"

    def grant_or_revoke_instance_permission(self, request, bk_token=None, bk_username=None):
        if not isinstance(request, ApiAuthRequest):
            raise AuthInvalidRequest("request should be a instance of iam.auth.models.ApiAuthRequest")

        self._validate_request(request)
        data = request.to_dict()

        if not (bk_token or bk_username):
            raise AuthInvalidRequest("bk_token and bk_username can not both be empty")

        ok, message, policies = self._client.instance_authorization(bk_token, bk_username, data)
        if not ok:
            raise AuthAPIError(message)
        return policies

    def grant_or_revoke_path_permission(self, request, bk_token=None, bk_username=None):
        if not isinstance(request, ApiAuthRequest):
            raise AuthInvalidRequest("request should be a instance of iam.auth.models.ApiAuthRequest")
        self._validate_request(request)
        data = request.to_dict()

        if not (bk_token or bk_username):
            raise AuthInvalidRequest("bk_token and bk_username can not both be empty")

        ok, message, policies = self._client.path_authorization(bk_token, bk_username, data)
        if not ok:
            raise AuthAPIError(message)
        return policies
