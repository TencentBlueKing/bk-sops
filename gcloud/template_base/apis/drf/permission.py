# -*- coding: utf-8 -*-

from rest_framework import permissions

from gcloud.iam_auth import IAMMeta, get_iam_client, res_factory

from iam import Subject, Action
from iam.shortcuts import allow_or_raise_auth_failed

iam = get_iam_client()


class SchemeEditPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.detail:
            return True
        self.scheme_allow_or_raise_auth_failed(request)
        return True

    def has_object_permission(self, request, view, obj):
        template_id = int(obj.unique_id.split("-")[0])
        self.scheme_allow_or_raise_auth_failed(request, template_id)
        return True

    @staticmethod
    def scheme_allow_or_raise_auth_failed(request, template_id=None):
        data = request.query_params or request.data
        if "template_id" in data:
            template_id = data["template_id"]

        # 项目流程方案的权限控制
        if "project_id" in data or data.get("template_type") != "common":
            # 默认进行是否有流程查看权限校验
            scheme_action = IAMMeta.FLOW_VIEW_ACTION
            scheme_resources = res_factory.resources_for_flow(template_id)

        # 公共流程方案的权限控制
        else:
            # 默认进行是否有流程查看权限校验
            scheme_action = IAMMeta.COMMON_FLOW_VIEW_ACTION
            scheme_resources = res_factory.resources_for_common_flow(template_id)

        allow_or_raise_auth_failed(
            iam=iam,
            system=IAMMeta.SYSTEM_ID,
            subject=Subject("user", request.user.username),
            action=Action(scheme_action),
            resources=scheme_resources,
        )

        return True
