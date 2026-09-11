from dataclasses import dataclass
from typing import Optional

from gcloud.iam_auth.models import Resource


@dataclass(frozen=True)
class PermissionCheck:
    action_id: str
    resource: Optional[Resource] = None


@dataclass(frozen=True)
class PermissionDecision:
    check: PermissionCheck
    allowed: bool


@dataclass(frozen=True)
class AuthorizedScope:
    values: dict

    @classmethod
    def empty(cls):
        return cls(values={})

    def ids(self, resource_type):
        return frozenset(self.values.get(resource_type, ()))

    @property
    def is_empty(self):
        return not any(self.values.values())
