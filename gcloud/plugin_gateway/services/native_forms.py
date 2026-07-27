# -*- coding: utf-8 -*-

from urllib.parse import urljoin, urlsplit

from django.conf import settings


def _string_value(value):
    if callable(value):
        value = value()
    return value


def absolute_sops_url(value):
    value = _string_value(value)
    if not value:
        return None

    value = str(value)
    if urlsplit(value).scheme:
        return value

    return urljoin(settings.BK_SOPS_HOST.rstrip("/") + "/", value.lstrip("/"))


def _component_form(component_cls, form_attr, embedded_attr, key, base=None):
    data = _string_value(getattr(component_cls, form_attr, None))
    if not data:
        return None

    is_embedded = bool(_string_value(getattr(component_cls, embedded_attr, False)))
    return {
        "type": "component_js",
        "key": key,
        "data": str(data) if is_embedded else absolute_sops_url(data),
        "is_embedded": is_embedded,
        "base": absolute_sops_url(base) if base else None,
    }


def build_component_forms(component_cls):
    code = str(component_cls.code)
    base = _string_value(getattr(component_cls, "base", None))
    return {
        "input": _component_form(component_cls, "form", "form_is_embedded", code, base),
        "output": _component_form(
            component_cls,
            "output_form",
            "embedded_output_form",
            code,
        ),
    }


def _native_descriptor(form_type, key, data, is_embedded=True, base=None):
    if data in (None, ""):
        return None

    return {
        "type": form_type,
        "key": key,
        "data": data if is_embedded else absolute_sops_url(data),
        "is_embedded": bool(is_embedded),
        "base": absolute_sops_url(base) if base else None,
    }


def build_third_party_forms(plugin_code, detail_schema):
    provider_forms = detail_schema.get("forms")
    if not isinstance(provider_forms, dict):
        provider_forms = {}

    renderform = provider_forms.get("renderform")
    jsonschema = provider_forms.get("jsonschema")
    if isinstance(renderform, str) and renderform:
        input_form = _native_descriptor(
            "renderform",
            plugin_code,
            renderform,
            provider_forms.get("is_embedded", True),
            provider_forms.get("base"),
        )
    elif isinstance(jsonschema, dict):
        input_form = _native_descriptor("jsonschema", plugin_code, jsonschema)
    else:
        input_form = None

    return {"input": input_form, "output": None}
