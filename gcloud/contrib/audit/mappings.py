# -*- coding: utf-8 -*-
from gcloud.common_template.models import CommonTemplate
from gcloud.constants import BUSINESS, COMMON, ONETIME, PROJECT
from gcloud.iam_auth import IAMMeta
from gcloud.tasktmpl3.models import TaskTemplate


def get_task_create_action(template_source, create_method=None):
    if create_method == "app_maker":
        return IAMMeta.MINI_APP_CREATE_TASK_ACTION
    return {
        PROJECT: IAMMeta.FLOW_CREATE_TASK_ACTION,
        BUSINESS: IAMMeta.FLOW_CREATE_TASK_ACTION,
        COMMON: IAMMeta.COMMON_FLOW_CREATE_TASK_ACTION,
        ONETIME: IAMMeta.PROJECT_FAST_CREATE_TASK_ACTION,
    }.get(template_source)


def get_periodic_task_create_action(template_source):
    return {
        PROJECT: IAMMeta.FLOW_CREATE_PERIODIC_TASK_ACTION,
        COMMON: IAMMeta.COMMON_FLOW_CREATE_PERIODIC_TASK_ACTION,
    }.get(template_source)


def get_template_audit_meta(template_model_cls):
    if template_model_cls is TaskTemplate:
        return IAMMeta.FLOW_CREATE_ACTION, IAMMeta.FLOW_DELETE_ACTION, IAMMeta.FLOW_RESOURCE
    if template_model_cls is CommonTemplate:
        return (
            IAMMeta.COMMON_FLOW_CREATE_ACTION,
            IAMMeta.COMMON_FLOW_DELETE_ACTION,
            IAMMeta.COMMON_FLOW_RESOURCE,
        )
    raise ValueError("unsupported template model: {}".format(template_model_cls))
