from functools import reduce
from operator import or_

from django.db.models import Q

from gcloud.iam_auth.client import IAMV4Client
from gcloud.iam_auth.conf import ACTION_RESOURCE_TYPES, RESOURCES_BY_ID, SYSTEM_ID
from gcloud.iam_auth.creator import has_creator_action
from gcloud.iam_auth.exceptions import IAMV4ProtocolError
from gcloud.iam_auth.models import Resource, Subject
from gcloud.iam_auth.repository import creator_local_queryset, local_resource_queryset
from gcloud.iam_auth.service import validate_identity
from gcloud.iam_auth.topology import project_path
from gcloud.iam_auth.types import AuthorizedScope


class ScopeResolver:
    def __init__(self, client=None):
        self.client = client or IAMV4Client()

    def authorized_scope(self, username, tenant_id, action_id, include_creator=True):
        validate_identity(username, tenant_id)
        if action_id not in ACTION_RESOURCE_TYPES:
            raise IAMV4ProtocolError("unknown action id")
        target_type = ACTION_RESOURCE_TYPES[action_id]
        if target_type is None:
            raise IAMV4ProtocolError("authorized scope requires a resource action")
        if RESOURCES_BY_ID[target_type]["parent_id"] == "project":
            return self._project_child_scope(username, tenant_id, action_id, target_type, include_creator)

        rows = self.client.list_authorized_resources(tenant_id, Subject("user", username), action_id)
        clauses = {}
        unrestricted = set()
        for row in rows:
            resource_type = row["type"]
            if resource_type != target_type:
                raise IAMV4ProtocolError("authorized scope returned an unrelated resource type")
            ids = row["ids"]
            if ids == ["*"]:
                unrestricted.add(resource_type)
            else:
                clauses.setdefault(resource_type, []).append(Q(id__in=ids))
        if include_creator and target_type and has_creator_action(target_type, action_id):
            creator_queryset = creator_local_queryset(target_type, username, tenant_id)
            clauses.setdefault(target_type, []).append(Q(id__in=creator_queryset.values("id")))

        querysets = {}
        for resource_type in set(clauses) | unrestricted:
            queryset = local_resource_queryset(resource_type, tenant_id)
            if resource_type not in unrestricted:
                queryset = queryset.filter(reduce(or_, clauses[resource_type]))
            querysets[resource_type] = queryset.distinct()
        return AuthorizedScope(values={}, querysets=querysets)

    def _project_child_scope(self, username, tenant_id, action_id, target_type, include_creator):
        """Resolve child permissions through supported batch authorization calls.

        IAM V4 rejects relation/authorized-resources for child-resource actions.
        Probe each project ancestor first, then only check children outside the
        authorized projects. All candidates are confined to the current tenant.
        """
        subject = Subject("user", username)
        project_ids = list(local_resource_queryset("project", tenant_id).values_list("id", flat=True))
        # IAM accepts any non-empty child ID for an ancestor-scope check. Use
        # distinct IDs because auth-by-resources returns decisions keyed by ID.
        project_probes = [
            Resource(
                SYSTEM_ID,
                target_type,
                "__sops_project_scope_{}__".format(project_id),
                {"_bk_iam_path_": project_path(project_id)},
            )
            for project_id in project_ids
        ]
        project_decisions = (
            self.client.direct_auth_by_resources(tenant_id, subject, action_id, project_probes)
            if project_probes
            else {}
        )
        authorized_project_ids = [
            project_id for project_id, probe in zip(project_ids, project_probes) if project_decisions[str(probe.id)]
        ]

        querysets = {}
        clauses = []
        if authorized_project_ids:
            querysets["project"] = local_resource_queryset("project", tenant_id).filter(id__in=authorized_project_ids)
            clauses.append(Q(project_id__in=authorized_project_ids))

        # A user may also be authorized for individual children outside their
        # project-wide grants. Check those before returning a list/count scope.
        child_queryset = local_resource_queryset(target_type, tenant_id).exclude(project_id__in=authorized_project_ids)
        authorized_child_ids = []
        batch = []
        for resource_id, project_id in child_queryset.values_list("id", "project_id").iterator(chunk_size=1000):
            batch.append(
                Resource(
                    SYSTEM_ID,
                    target_type,
                    str(resource_id),
                    {"_bk_iam_path_": project_path(project_id)},
                )
            )
            if len(batch) == 20:
                decisions = self.client.direct_auth_by_resources(tenant_id, subject, action_id, batch)
                authorized_child_ids.extend(resource.id for resource in batch if decisions[str(resource.id)])
                batch = []
        if batch:
            decisions = self.client.direct_auth_by_resources(tenant_id, subject, action_id, batch)
            authorized_child_ids.extend(resource.id for resource in batch if decisions[str(resource.id)])
        if authorized_child_ids:
            clauses.append(Q(id__in=authorized_child_ids))
        if include_creator and has_creator_action(target_type, action_id):
            creator_queryset = creator_local_queryset(target_type, username, tenant_id)
            clauses.append(Q(id__in=creator_queryset.values("id")))
        if clauses:
            querysets[target_type] = (
                local_resource_queryset(target_type, tenant_id).filter(reduce(or_, clauses)).distinct()
            )
        return AuthorizedScope(values={}, querysets=querysets)
