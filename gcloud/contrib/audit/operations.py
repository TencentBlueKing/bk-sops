# -*- coding: utf-8 -*-
import logging

from django.conf import settings

from gcloud.contrib.audit.mappings import get_template_audit_meta
from gcloud.contrib.audit.utils import bk_audit_add_event_on_commit, get_audit_snapshot

logger = logging.getLogger("root")


def audit_imported_templates(username, template_model_cls, import_result):
    if not settings.ENABLE_BK_AUDIT or import_result.get("result") is not True:
        return
    try:
        create_action, _, resource_id = get_template_audit_meta(template_model_cls)
        flows = (import_result.get("data") or {}).get("flows") or {}
        template_ids = [int(template_id) for template_id in flows]
        for instance in template_model_cls.objects.filter(id__in=template_ids):
            bk_audit_add_event_on_commit(
                username=username,
                action_id=create_action,
                resource_id=resource_id,
                instance=instance,
            )
    except Exception:
        logger.exception("bk_audit_import_templates_failed")


def audit_deleted_templates(username, template_model_cls, instances_by_id, success_ids):
    if not settings.ENABLE_BK_AUDIT:
        return
    try:
        _, delete_action, resource_id = get_template_audit_meta(template_model_cls)
        for template_id in success_ids:
            try:
                normalized_template_id = int(template_id)
            except (TypeError, ValueError):
                continue
            instance = instances_by_id.get(normalized_template_id)
            if instance is None:
                continue
            bk_audit_add_event_on_commit(
                username=username,
                action_id=delete_action,
                resource_id=resource_id,
                instance=instance,
                origin_data=get_audit_snapshot(resource_id, instance),
                data={"id": normalized_template_id, "is_deleted": True},
            )
    except Exception:
        logger.exception("bk_audit_delete_templates_failed")
