# -*- coding: utf-8 -*-
"""
Task-level adapters for the generic pipeline diagnostics capability.
"""

from gcloud.taskflow3.models import TaskFlowInstance, TaskFlowRelation


def resolve_task_diagnostic_context(task):
    pipeline_instance = task.pipeline_instance
    root_pipeline_id = pipeline_instance.instance_id if pipeline_instance else ""
    relations = list(TaskFlowRelation.objects.filter(root_task_id=task.id).values())

    return {
        "task_id": task.id,
        "project_id": task.project_id,
        "engine_ver": task.engine_ver,
        "root_pipeline_id": root_pipeline_id,
        "template_id": task.template_id,
        "template_source": task.template_source,
        "current_flow": task.current_flow,
        "relations": relations,
    }


def get_task_context(task_id):
    task = TaskFlowInstance.objects.select_related("pipeline_instance").get(id=task_id)
    return resolve_task_diagnostic_context(task)
