# -*- coding: utf-8 -*-
from rest_framework import permissions

from gcloud.constants import COMMON, PROJECT
from gcloud.core.apis.drf.viewsets import IAMMixin
from gcloud.iam_auth import IAMMeta, get_iam_client, res_factory
from gcloud.iam_auth.creator import get_flow_creator_ids, is_flow_creator
from gcloud.iam_auth.exceptions import MultiAuthFailedException
from gcloud.iam_auth.models import Action, Request, Subject


class TemplateFormWithSchemesPermissions(IAMMixin, permissions.BasePermission):
    def has_permission(self, request, view):
        template_id = request.data["template_id"]
        template_source = request.data["template_source"]
        tenant_id = request.user.tenant_id
        if template_source == PROJECT:
            if is_flow_creator(
                request.user.username,
                tenant_id,
                template_id,
                project_id=request.data.get("project_id"),
            ):
                return True
            action = IAMMeta.FLOW_VIEW_ACTION
            resources = res_factory.resources_for_flow(template_id, tenant_id)
        else:
            action = IAMMeta.COMMON_FLOW_VIEW_ACTION
            resources = res_factory.resources_for_common_flow(template_id, tenant_id)

        self.iam_auth_check(request, action, resources)

        return True


class BatchTemplateFormWithSchemesPermissions(IAMMixin, permissions.BasePermission):
    def is_allowed_batch_view_flow(self, request, template_source, flows):
        subject = Subject("user", request.user.username)
        tenant_id = request.user.tenant_id
        if template_source == PROJECT:
            action = Action(IAMMeta.FLOW_VIEW_ACTION)
            creator_ids = get_flow_creator_ids(
                request.user.username,
                tenant_id,
                flows,
                project_id=request.data.get("project_id"),
            )
            flows = [flow_id for flow_id in flows if str(flow_id) not in creator_ids]
            resources_list = res_factory.resources_list_for_flows(flows, tenant_id)
        else:
            action = Action(IAMMeta.COMMON_FLOW_VIEW_ACTION)
            resources_list = res_factory.resources_list_for_common_flows(flows, tenant_id)

        if not resources_list:
            return True

        iam = get_iam_client(tenant_id)
        resources_map = {}
        for resources in resources_list:
            resources_map[resources[0].id] = resources

        request = Request(IAMMeta.SYSTEM_ID, subject, action, [], {})
        result = iam.batch_is_allowed(request, resources_list)

        if not result:
            raise MultiAuthFailedException(IAMMeta.SYSTEM_ID, subject, action, resources_list)

        not_allowed_list = []
        for tid, allow in result.items():
            if not allow:
                not_allowed_list.append(resources_map[tid])

        if not_allowed_list:
            raise MultiAuthFailedException(IAMMeta.SYSTEM_ID, subject, action, not_allowed_list)

    def has_permission(self, request, view):
        template_list = request.data["template_list"]

        flows = []
        common_flows = []
        for template in template_list:
            if template["template_source"] == PROJECT:
                flows.append(template["id"])
            else:
                common_flows.append(template["id"])

        self.is_allowed_batch_view_flow(request, PROJECT, flows)
        self.is_allowed_batch_view_flow(request, COMMON, common_flows)

        return True
