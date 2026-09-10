import hashlib
import json
from dataclasses import dataclass

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db.models import Q

from gcloud.iam_auth.conf import SEARCH_INSTANCE_CACHE_TIME
from gcloud.iam_auth.exceptions import IAMV4ProtocolError
from gcloud.iam_auth.repository import local_resource_queryset
from gcloud.iam_auth.topology import project_path


def deduplicate(values):
    return list(dict.fromkeys(str(value) for value in values if value))


def list_instance_cache_key(tenant_id, resource_type, parent, keyword, page, page_size):
    context = {
        "tenant_id": tenant_id,
        "resource_type": resource_type,
        "parent": parent or {},
        "keyword": keyword,
        "page": page,
        "page_size": page_size,
    }
    digest = hashlib.sha256(json.dumps(context, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    return "iam:v4:callback:list:{}".format(digest)


@dataclass(frozen=True)
class ProviderSpec:
    resource_type: str
    name_lookup: str
    parent_field: str = ""
    approver_lookups: tuple = ()


class ResourceProvider:
    def __init__(self, spec):
        self.spec = spec

    def _validate_parent(self, tenant_id, parent):
        if not parent:
            return None
        if not self.spec.parent_field or parent.get("type") != "project":
            raise IAMV4ProtocolError("invalid parent resource")
        from gcloud.core.models import Project

        if not Project.objects.filter(id=parent.get("id"), tenant_id=tenant_id, is_disable=False).exists():
            raise IAMV4ProtocolError("parent resource was not found")
        return parent["id"]

    def build_queryset(self, tenant_id, parent=None, keyword=""):
        queryset = local_resource_queryset(self.spec.resource_type, tenant_id)
        parent_id = self._validate_parent(tenant_id, parent)
        if parent_id is not None:
            queryset = queryset.filter(**{self.spec.parent_field: parent_id})
        if keyword:
            query = Q(**{"{}__icontains".format(self.spec.name_lookup): keyword})
            try:
                query |= Q(id=int(keyword))
            except (TypeError, ValueError):
                pass
            queryset = queryset.filter(query)
        return queryset.order_by("id")

    def _value(self, obj, lookup):
        value = obj
        for part in lookup.split("__"):
            value = getattr(value, part)
        return value

    def _display_name(self, obj):
        return str(self._value(obj, self.spec.name_lookup))

    def _approvers(self, obj, tenant_id):
        candidates = deduplicate(self._value(obj, lookup) for lookup in self.spec.approver_lookups)
        if not candidates:
            return []
        valid = set(
            get_user_model()
            .objects.filter(username__in=candidates, tenant_id=tenant_id)
            .values_list("username", flat=True)
        )
        return [username for username in candidates if username in valid]

    def list_instance(self, tenant_id, parent=None, keyword="", page=1, page_size=20):
        cache_key = list_instance_cache_key(tenant_id, self.spec.resource_type, parent, keyword, page, page_size)
        cached = cache.get(cache_key)
        if cached is not None:
            return cached
        queryset = self.build_queryset(tenant_id, parent, keyword)
        count = queryset.count()
        start = (page - 1) * page_size
        result = {
            "count": count,
            "results": [
                {"id": str(obj.id), "display_name": self._display_name(obj)}
                for obj in queryset[start : start + page_size]
            ],
        }
        cache.set(cache_key, result, SEARCH_INSTANCE_CACHE_TIME)
        return result

    def fetch_instance_info(self, tenant_id, ids=(), requires=()):
        queryset = local_resource_queryset(self.spec.resource_type, tenant_id).filter(id__in=ids).order_by("id")
        requested = set(requires) or {"display_name", "_bk_iam_path_", "_bk_iam_approvers_"}
        results = []
        for obj in queryset:
            item = {"id": str(obj.id)}
            if "display_name" in requested:
                item["display_name"] = self._display_name(obj)
            if "_bk_iam_path_" in requested and self.spec.parent_field:
                item["_bk_iam_path_"] = project_path(self._value(obj, self.spec.parent_field))
            if "_bk_iam_approvers_" in requested:
                item["_bk_iam_approvers_"] = self._approvers(obj, tenant_id)
            results.append(item)
        return results
