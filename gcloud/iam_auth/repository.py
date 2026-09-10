"""Tenant-scoped IAM resource lookup.

This module is deliberately independent from the IAM HTTP client so it can be
used by authorization, scope expansion, apply URL generation and callbacks.
"""

from gcloud.iam_auth.exceptions import IAMV4ProtocolError


def local_resource_queryset(resource_type, tenant_id):
    if not tenant_id:
        raise IAMV4ProtocolError("tenant_id is required")
    if resource_type == "project":
        from gcloud.core.models import Project

        return Project.objects.filter(tenant_id=tenant_id, is_disable=False)
    if resource_type == "flow":
        from gcloud.tasktmpl3.models import TaskTemplate

        return TaskTemplate.objects.filter(project__tenant_id=tenant_id, is_deleted=False)
    if resource_type == "task":
        from gcloud.taskflow3.models import TaskFlowInstance

        return TaskFlowInstance.objects.filter(project__tenant_id=tenant_id, is_deleted=False)
    if resource_type == "common_flow":
        from gcloud.common_template.models import CommonTemplate

        return CommonTemplate.objects.filter(tenant_id=tenant_id, is_deleted=False)
    if resource_type == "mini_app":
        from gcloud.contrib.appmaker.models import AppMaker

        return AppMaker.objects.filter(project__tenant_id=tenant_id, is_deleted=False)
    if resource_type == "periodic_task":
        from gcloud.periodictask.models import PeriodicTask

        return PeriodicTask.objects.filter(project__tenant_id=tenant_id)
    if resource_type == "clocked_task":
        from gcloud.clocked_task.models import ClockedTask
        from gcloud.core.models import Project

        project_ids = Project.objects.filter(tenant_id=tenant_id, is_disable=False).values_list("id", flat=True)
        return ClockedTask.objects.filter(project_id__in=project_ids)
    raise IAMV4ProtocolError("unknown resource type")


def resource_exists(resource_type, resource_id, tenant_id):
    return local_resource_queryset(resource_type, tenant_id).filter(id=resource_id).exists()


def list_all_local_ids(resource_type, tenant_id):
    return {str(item) for item in local_resource_queryset(resource_type, tenant_id).values_list("id", flat=True)}


def list_creator_local_ids(resource_type, username, tenant_id):
    """Return tenant-local IDs whose owner field matches the current user."""
    creator_fields = {
        "flow": "pipeline_template__creator",
        "task": "pipeline_instance__creator",
        "common_flow": "pipeline_template__creator",
        "mini_app": "creator",
        "periodic_task": "task__creator",
        "clocked_task": "creator",
    }
    creator_field = creator_fields.get(resource_type)
    if creator_field is None:
        return set()
    return {
        str(item)
        for item in local_resource_queryset(resource_type, tenant_id)
        .filter(**{creator_field: username})
        .values_list("id", flat=True)
    }


def intersect_local_ids(resource_type, tenant_id, ids):
    if ids == ["*"]:
        return list_all_local_ids(resource_type, tenant_id)
    return {
        str(item)
        for item in local_resource_queryset(resource_type, tenant_id).filter(id__in=ids).values_list("id", flat=True)
    }


def descendant_ids(resource_type, tenant_id, project_ids):
    """Expand a project-level IAM scope to tenant-local child resources."""

    if resource_type == "project":
        return set(project_ids)
    if resource_type == "common_flow":
        raise IAMV4ProtocolError("common_flow has no project ancestor")
    return {
        str(item)
        for item in local_resource_queryset(resource_type, tenant_id)
        .filter(project_id__in=project_ids)
        .values_list("id", flat=True)
    }
