# -*- coding: utf-8 -*-
from rest_framework import permissions

from gcloud.core.apis.drf.viewsets import IAMMixin
from gcloud.iam_auth import IAMMeta, res_factory


class CollectionTaskPermissions(IAMMixin, permissions.BasePermission):
    actions = {
        "list": IAMMeta.PROJECT_VIEW_ACTION,
    }

    def has_permission(self, request, view):
        if view.action == "list":
            if "project_id" not in request.query_params:
                return False
            self.iam_auth_check(
                request,
                action=self.actions[view.action],
                resources=res_factory.resources_for_project(request.query_params["project_id"]),
            )
        return True
