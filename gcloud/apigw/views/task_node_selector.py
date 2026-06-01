# -*- coding: utf-8 -*-
from pipeline.core.constants import PE
from pipeline.models import TemplateScheme
from pipeline_web.preview_base import PipelineTemplateWebPreviewer


class TaskNodeSelectionValidationError(Exception):
    pass


def _is_scheme_pk(value):
    return isinstance(value, int) and not isinstance(value, bool)


def normalize_template_scheme_params(params):
    template_schemes_id = params.get("template_schemes_id", [])

    if isinstance(template_schemes_id, str) or _is_scheme_pk(template_schemes_id):
        template_schemes_id = [template_schemes_id]
        params["template_schemes_id"] = template_schemes_id
    else:
        params.setdefault("template_schemes_id", template_schemes_id)

    return template_schemes_id


def get_exclude_nodes_by_execute_nodes(execute_nodes, pipeline_tree):
    all_nodes = set(pipeline_tree[PE.activities].keys())
    execute_nodes = set(execute_nodes).intersection(all_nodes)
    return sorted(all_nodes - execute_nodes)


def _scheme_identifier_key(scheme_id):
    if _is_scheme_pk(scheme_id):
        return "id", scheme_id
    return "unique_id", scheme_id


def _validate_template_scheme_ids(scheme_ids):
    if not isinstance(scheme_ids, list):
        raise TaskNodeSelectionValidationError("invalid template_schemes_id")

    invalid_scheme_ids = [
        scheme_id
        for scheme_id in scheme_ids
        if not ((isinstance(scheme_id, str) and scheme_id) or (_is_scheme_pk(scheme_id) and scheme_id > 0))
    ]
    if invalid_scheme_ids:
        raise TaskNodeSelectionValidationError(
            "invalid template_schemes_id: all items must be non-empty strings or positive integers"
        )

    seen_scheme_ids = set()
    duplicate_scheme_ids = []
    for scheme_id in scheme_ids:
        scheme_key = _scheme_identifier_key(scheme_id)
        if scheme_key in seen_scheme_ids and scheme_id not in duplicate_scheme_ids:
            duplicate_scheme_ids.append(scheme_id)
        seen_scheme_ids.add(scheme_key)

    if duplicate_scheme_ids:
        raise TaskNodeSelectionValidationError(
            "duplicate template_schemes_id: {}".format(
                ", ".join([str(scheme_id) for scheme_id in duplicate_scheme_ids])
            )
        )


def _resolve_template_scheme_pks(template, scheme_ids):
    template_id = template.pipeline_template.id
    scheme_unique_ids = [scheme_id for scheme_id in scheme_ids if isinstance(scheme_id, str)]
    scheme_pks = [scheme_id for scheme_id in scheme_ids if _is_scheme_pk(scheme_id)]
    scheme_id_by_identifier = {}

    if scheme_unique_ids:
        schemes = TemplateScheme.objects.filter(
            template_id=template_id,
            unique_id__in=scheme_unique_ids,
        )
        scheme_id_by_identifier.update({("unique_id", scheme.unique_id): scheme.id for scheme in schemes})

    if scheme_pks:
        schemes = TemplateScheme.objects.filter(
            template_id=template_id,
            id__in=scheme_pks,
        )
        scheme_id_by_identifier.update({("id", scheme.id): scheme.id for scheme in schemes})

    missing_scheme_ids = [
        scheme_id for scheme_id in scheme_ids if _scheme_identifier_key(scheme_id) not in scheme_id_by_identifier
    ]
    if missing_scheme_ids:
        raise TaskNodeSelectionValidationError(
            "unknown template_schemes_id: {}".format(", ".join([str(scheme_id) for scheme_id in missing_scheme_ids]))
        )
    return [scheme_id_by_identifier[_scheme_identifier_key(scheme_id)] for scheme_id in scheme_ids]


def resolve_exclude_task_nodes_id(template, pipeline_tree, params, support_execute_task_nodes=False):
    template_schemes_id = normalize_template_scheme_params(params)
    exclude_task_nodes_id = params.get("exclude_task_nodes_id", [])
    execute_task_nodes_id = params.get("execute_task_nodes_id", [])

    _validate_template_scheme_ids(template_schemes_id)

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
