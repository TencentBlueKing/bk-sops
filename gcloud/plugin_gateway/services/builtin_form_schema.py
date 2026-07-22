# -*- coding: utf-8 -*-

from copy import deepcopy

from django.utils.encoding import force_text
from django.utils.functional import Promise

BUILTIN_FORM_OVERRIDES = {
    "job_fast_execute_script": {
        "job_content": {
            "name": "codeEditor",
            "props": {"language": "shell", "height": "400px", "showMiniMap": False},
        }
    },
    "all_biz_job_fast_execute_script": {
        "job_content": {
            "name": "codeEditor",
            "props": {"language": "shell", "height": "400px", "showMiniMap": False},
        }
    },
    "bk_http_request": {
        "bk_http_request_body": {"name": "textarea", "props": {"rows": 6}},
        "bk_http_success_exp": {"name": "textarea", "props": {"rows": 4}},
    },
    "nodeman_create_task": {
        "nodeman_hosts[].auth_key": {"name": "password", "props": {}},
        "nodeman_op_info.nodeman_hosts[].auth_key": {"name": "password", "props": {}},
    },
}

JSON_SCHEMA_TYPE_MAP = {
    "bool": "boolean",
    "dict": "object",
    "float": "number",
    "int": "integer",
    "json": "object",
    "list": "array",
}


def build_builtin_form_schema(component_code, io_format):
    overrides = BUILTIN_FORM_OVERRIDES.get(component_code)
    if not overrides:
        return None

    properties = {}
    required = []
    for raw_item in io_format or []:
        item = _item_as_dict(raw_item)
        key = _stringify(item.get("key"))
        if not key:
            continue

        field_schema = _normalize_schema(item.get("schema"), fallback_type=item.get("type"))
        field_schema["title"] = _stringify(item.get("name")) or key
        properties[key] = field_schema
        if item.get("required"):
            required.append(key)

    form_schema = {"type": "object", "properties": properties}
    if required:
        form_schema["required"] = required

    applied = False
    for field_path, component in overrides.items():
        field_schema = _find_field_schema(form_schema, field_path)
        if field_schema is None:
            continue
        field_schema["ui:component"] = deepcopy(component)
        applied = True

    return _json_safe(form_schema) if applied else None


def _normalize_schema(raw_schema, fallback_type=None):
    schema = raw_schema if isinstance(raw_schema, dict) else {}
    normalized = {}

    field_type = schema.get("type") or fallback_type or "string"
    normalized["type"] = JSON_SCHEMA_TYPE_MAP.get(field_type, field_type)
    if "description" in schema:
        normalized["description"] = _stringify(schema["description"])
    if schema.get("enum"):
        normalized["enum"] = _json_safe(schema["enum"])
    if "default" in schema:
        normalized["default"] = _json_safe(schema["default"])

    if normalized["type"] == "array":
        normalized["items"] = _normalize_schema(schema.get("items"))
    elif normalized["type"] == "object":
        normalized["properties"] = {
            _stringify(key): _with_default_title(_normalize_schema(value), key)
            for key, value in (schema.get("properties") or {}).items()
        }

    return normalized


def _with_default_title(schema, key):
    schema["title"] = _stringify(key)
    return schema


def _find_field_schema(form_schema, field_path):
    container = form_schema
    segments = field_path.split(".")
    for index, segment in enumerate(segments):
        is_array = segment.endswith("[]")
        field_name = segment[:-2] if is_array else segment
        field = (container.get("properties") or {}).get(field_name)
        if field is None:
            return None
        if index == len(segments) - 1:
            return field
        container = field.get("items", {}) if is_array else field
    return None


def _item_as_dict(item):
    if isinstance(item, dict):
        return item
    as_dict = getattr(item, "as_dict", None)
    if callable(as_dict):
        return as_dict()
    return {
        "key": getattr(item, "key", ""),
        "name": getattr(item, "name", ""),
        "type": getattr(item, "type", "string"),
        "schema": getattr(item, "schema", None),
        "required": getattr(item, "required", None),
    }


def _json_safe(value):
    if isinstance(value, Promise):
        return force_text(value)
    if isinstance(value, dict):
        return {_stringify(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    return value


def _stringify(value):
    if value is None:
        return ""
    return force_text(value)
