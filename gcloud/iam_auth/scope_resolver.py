from gcloud.iam_auth.client import IAMV4Client
from gcloud.iam_auth.conf import ACTION_RESOURCE_TYPES
from gcloud.iam_auth.creator import has_creator_action
from gcloud.iam_auth.exceptions import IAMV4ProtocolError
from gcloud.iam_auth.models import Subject
from gcloud.iam_auth.repository import descendant_ids, intersect_local_ids, list_creator_local_ids
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
        values = {}
        for row in rows:
            local_ids = intersect_local_ids(row["type"], tenant_id, row["ids"])
            values.setdefault(row["type"], set()).update(local_ids)
            if row["type"] == "project" and target_type != "project":
                values.setdefault(target_type, set()).update(descendant_ids(target_type, tenant_id, local_ids))
        if target_type and has_creator_action(target_type, action_id):
            values.setdefault(target_type, set()).update(list_creator_local_ids(target_type, username, tenant_id))
        return AuthorizedScope(values=values)
