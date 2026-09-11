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
    querysets: Optional[dict] = None

    @classmethod
    def empty(cls):
        return cls(values={})

    def ids(self, resource_type):
        if self.querysets and resource_type in self.querysets:
            return frozenset(str(item) for item in self.querysets[resource_type].values_list("id", flat=True))
        return frozenset(self.values.get(resource_type, ()))

    def queryset(self, resource_type):
        if self.querysets and resource_type in self.querysets:
            return self.querysets[resource_type]
        return None

    def contains(self, resource_type, resource_id):
        queryset = self.queryset(resource_type)
        if queryset is not None:
            return queryset.filter(id=resource_id).exists()
        return str(resource_id) in {str(item) for item in self.values.get(resource_type, ())}

    def exists(self, resource_type):
        queryset = self.queryset(resource_type)
        if queryset is not None:
            return queryset.exists()
        return bool(self.values.get(resource_type, ()))

    @property
    def is_empty(self):
        resource_types = set(self.values) | set(self.querysets or {})
        return not any(self.exists(resource_type) for resource_type in resource_types)
