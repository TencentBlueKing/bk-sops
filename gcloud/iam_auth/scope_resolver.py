from functools import reduce
from operator import or_

from django.db.models import Q

from gcloud.iam_auth.client import IAMV4Client
from gcloud.iam_auth.conf import ACTION_RESOURCE_TYPES, RESOURCES_BY_ID
from gcloud.iam_auth.creator import has_creator_action
from gcloud.iam_auth.exceptions import IAMV4ProtocolError
from gcloud.iam_auth.models import Subject
from gcloud.iam_auth.repository import creator_local_queryset, local_resource_queryset
from gcloud.iam_auth.service import validate_identity
from gcloud.iam_auth.types import AuthorizedScope


class ScopeResolver:
    def __init__(self, client=None):
        self.client = client or IAMV4Client()

    def authorized_scope(self, username, tenant_id, action_id):
        validate_identity(username, tenant_id)
        if action_id not in ACTION_RESOURCE_TYPES:
            raise IAMV4ProtocolError("unknown action id")
        rows = self.client.list_authorized_resources(tenant_id, Subject("user", username), action_id)
        target_type = ACTION_RESOURCE_TYPES[action_id]
        if target_type is None:
            raise IAMV4ProtocolError("authorized scope requires a resource action")
        allowed_types = {target_type}
        if RESOURCES_BY_ID[target_type]["parent_id"] == "project":
            allowed_types.add("project")
        clauses = {}
        unrestricted = set()
        for row in rows:
            resource_type = row["type"]
            if resource_type not in allowed_types:
                raise IAMV4ProtocolError("authorized scope returned an unrelated resource type")
            ids = row["ids"]
            if ids == ["*"]:
                unrestricted.add(resource_type)
            else:
                clauses.setdefault(resource_type, []).append(Q(id__in=ids))
            if row["type"] == "project" and target_type != "project":
                project_queryset = local_resource_queryset("project", tenant_id)
                if ids != ["*"]:
                    project_queryset = project_queryset.filter(id__in=ids)
                clauses.setdefault(target_type, []).append(Q(project_id__in=project_queryset.values("id")))
        if target_type and has_creator_action(target_type, action_id):
            creator_queryset = creator_local_queryset(target_type, username, tenant_id)
            clauses.setdefault(target_type, []).append(Q(id__in=creator_queryset.values("id")))

        querysets = {}
        for resource_type in set(clauses) | unrestricted:
            queryset = local_resource_queryset(resource_type, tenant_id)
            if resource_type not in unrestricted:
                queryset = queryset.filter(reduce(or_, clauses[resource_type]))
            querysets[resource_type] = queryset.distinct()
        return AuthorizedScope(values={}, querysets=querysets)
