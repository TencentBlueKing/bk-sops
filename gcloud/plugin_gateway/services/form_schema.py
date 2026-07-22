# -*- coding: utf-8 -*-

from copy import deepcopy

from django.utils.encoding import force_text
from django.utils.functional import Promise

UNIFORM_TYPE_MAP = {
    "array": "list",
    "boolean": "bool",
    "bool": "bool",
    "dict": "json",
    "float": "int",
    "integer": "int",
    "int": "int",
    "json": "json",
    "list": "list",
    "number": "int",
    "object": "json",
    "string": "string",
}


def normalize_uniform_type(field_type):
    return UNIFORM_TYPE_MAP.get(field_type or "string", "string")


def convert_component_io(io_format):
    fields = []
    for raw_item in io_format or []:
        item = _item_as_dict(raw_item)
        schema = _schema_as_dict(item.get("schema"))
        field = _build_uniform_field(
            key=item.get("key", ""),
            name=item.get("name", ""),
            field_type=item.get("type") or schema.get("type"),
            schema=schema,
            required=item.get("required"),
        )
        fields.append(field)
    return fields


def convert_json_schema_fields(schema, required=None):
    if not isinstance(schema, dict):
        return []

    required_fields = set(required if required is not None else schema.get("required") or [])
    fields = []
    for key, field_schema in (schema.get("properties") or {}).items():
        field_schema = field_schema if isinstance(field_schema, dict) else {}
        fields.append(
            _build_uniform_field(
                key=key,
                name=field_schema.get("title") or key,
                field_type=field_schema.get("type"),
                schema=field_schema,
                required=key in required_fields,
            )
        )
    return fields


def build_structured_form_schema(inputs_schema, renderform=None):
    if not isinstance(inputs_schema, dict):
        return None

    form_schema = deepcopy(inputs_schema)
    form_schema.setdefault("type", "object")
    form_schema.setdefault("properties", {})

    if isinstance(renderform, dict):
        if isinstance(renderform.get("properties"), dict):
            form_schema = _deep_merge(form_schema, renderform)
        elif all(isinstance(value, dict) for value in renderform.values()):
            form_schema["properties"] = _deep_merge(form_schema["properties"], renderform)

    return _json_safe(form_schema)


def _build_uniform_field(key, name, field_type, schema, required=None):
    normalized_type = normalize_uniform_type(field_type or schema.get("type"))
    description = _stringify(schema.get("description", ""))
    field = {
        "key": _stringify(key),
        "name": _stringify(name),
        "type": normalized_type,
        "desc": description,
        "description": description,
    }
    if required:
        field["required"] = True
    if "default" in schema:
        field["default"] = _json_safe(schema["default"])

    options = schema.get("enum") or []
    items = schema.get("items") if isinstance(schema.get("items"), dict) else {}
    if normalized_type == "list" and not options:
        options = items.get("enum") or []
    if options:
        field["options"] = _json_safe(options)

    if normalized_type == "list" and normalize_uniform_type(items.get("type")) == "json":
        field["form_type"] = "table"
        field["table"] = {
            "fields": convert_json_schema_fields(items),
            "meta": {},
        }

    return field


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


def _schema_as_dict(schema):
    if isinstance(schema, dict):
        return schema
    as_dict = getattr(schema, "as_dict", None)
    if callable(as_dict):
        return as_dict()
    return {}


def _deep_merge(base, overlay):
    merged = deepcopy(base)
    for key, value in overlay.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = deepcopy(value)
    return merged


def _json_safe(value):
    if isinstance(value, Promise):
        return force_text(value)
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    return value


def _stringify(value):
    if value is None:
        return ""
    return force_text(value)
