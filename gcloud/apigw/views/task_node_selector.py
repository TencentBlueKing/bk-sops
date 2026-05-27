# -*- coding: utf-8 -*-
from pipeline.core.constants import PE
from pipeline.models import TemplateScheme
from pipeline_web.preview_base import PipelineTemplateWebPreviewer


class TaskNodeSelectionValidationError(Exception):
    pass


def normalize_template_scheme_params(params):
    template_schemes_id = params.get("template_schemes_id", [])

    if isinstance(template_schemes_id, str):
        template_schemes_id = [template_schemes_id]
        params["template_schemes_id"] = template_schemes_id
    else:
        params.setdefault("template_schemes_id", template_schemes_id)

    return template_schemes_id


def get_exclude_nodes_by_execute_nodes(execute_nodes, pipeline_tree):
    all_nodes = set(pipeline_tree[PE.activities].keys())
    execute_nodes = set(execute_nodes).intersection(all_nodes)
    return sorted(all_nodes - execute_nodes)


def _validate_template_scheme_unique_ids(scheme_unique_ids):
    if not isinstance(scheme_unique_ids, list):
        raise TaskNodeSelectionValidationError("invalid template_schemes_id")

    if any(not isinstance(unique_id, str) or not unique_id for unique_id in scheme_unique_ids):
        raise TaskNodeSelectionValidationError("invalid template_schemes_id: all items must be non-empty strings")

    seen_unique_ids = set()
    duplicate_unique_ids = []
    for unique_id in scheme_unique_ids:
        if unique_id in seen_unique_ids and unique_id not in duplicate_unique_ids:
            duplicate_unique_ids.append(unique_id)
        seen_unique_ids.add(unique_id)

    if duplicate_unique_ids:
        raise TaskNodeSelectionValidationError(
            "duplicate template_schemes_id: {}".format(", ".join(duplicate_unique_ids))
        )


def _resolve_template_scheme_pks(template, scheme_unique_ids):
    schemes = TemplateScheme.objects.filter(
        template_id=template.pipeline_template.id,
        unique_id__in=scheme_unique_ids,
    )
    scheme_id_by_unique_id = {scheme.unique_id: scheme.id for scheme in schemes}
    missing_unique_ids = [unique_id for unique_id in scheme_unique_ids if unique_id not in scheme_id_by_unique_id]
    if missing_unique_ids:
        raise TaskNodeSelectionValidationError(
            "unknown template_schemes_id: {}".format(", ".join(missing_unique_ids))
        )
    return [scheme_id_by_unique_id[unique_id] for unique_id in scheme_unique_ids]


def resolve_exclude_task_nodes_id(template, pipeline_tree, params, support_execute_task_nodes=False):
    template_schemes_id = normalize_template_scheme_params(params)
    exclude_task_nodes_id = params.get("exclude_task_nodes_id", [])
    execute_task_nodes_id = params.get("execute_task_nodes_id", [])

    _validate_template_scheme_unique_ids(template_schemes_id)

    if template_schemes_id and (exclude_task_nodes_id or execute_task_nodes_id):
        raise TaskNodeSelectionValidationError(
            "template_schemes_id can not be used with exclude_task_nodes_id or execute_task_nodes_id"
        )

    if template_schemes_id:
        scheme_pks = _resolve_template_scheme_pks(template, template_schemes_id)
        return PipelineTemplateWebPreviewer.get_template_exclude_task_nodes_with_schemes(
            pipeline_tree, scheme_pks, check_schemes_exist=True
        )

    if support_execute_task_nodes and execute_task_nodes_id:
        return get_exclude_nodes_by_execute_nodes(execute_task_nodes_id, pipeline_tree)

    return exclude_task_nodes_id
