import re
from urllib.parse import urlsplit

from django.conf import settings
from django.core.exceptions import DisallowedHost

PLUGIN_FORM_ORIGIN_ABSENT = "absent"
PLUGIN_FORM_ORIGIN_SAME_ORIGIN = "same_origin"
PLUGIN_FORM_ORIGIN_ALLOWED_CROSS_ORIGIN = "allowed_cross_origin"
PLUGIN_FORM_ORIGIN_FORBIDDEN = "forbidden"

PIPELINE_FORM_METHODS = ("GET",)
DATA_API_FORM_METHODS = ("GET", "POST", "PUT", "PATCH", "DELETE")
PLUGIN_FORM_ROUTES = (
    (re.compile(r"^/pipeline/cc_get_business_list/$"), PIPELINE_FORM_METHODS),
    (re.compile(r"^/pipeline/job_get_public_script_name_list/$"), PIPELINE_FORM_METHODS),
    (re.compile(r"^/pipeline/job_get_script_name_list/\d+/$"), PIPELINE_FORM_METHODS),
    (re.compile(r"^/pipeline/get_job_account_list/\d+/$"), PIPELINE_FORM_METHODS),
    (re.compile(r"^/pipeline/jobv3_get_instance_list/\d+/\d+/\d+/$"), PIPELINE_FORM_METHODS),
    (re.compile(r"^/plugin_service/data_api/[^/]+/.+$"), DATA_API_FORM_METHODS),
)


def _is_valid_http_origin(origin):
    if not isinstance(origin, str) or not origin or origin == "null":
        return False
    if any(character.isspace() for character in origin):
        return False

    try:
        parsed = urlsplit(origin)
        parsed.port
    except (TypeError, ValueError):
        return False

    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return False
    if parsed.username is not None or parsed.password is not None:
        return False
    if parsed.path or parsed.query or parsed.fragment:
        return False
    return origin == "{}://{}".format(parsed.scheme, parsed.netloc)


def classify_plugin_form_request_origin(request):
    if "HTTP_ORIGIN" not in request.META:
        return PLUGIN_FORM_ORIGIN_ABSENT

    origin = request.META.get("HTTP_ORIGIN")
    if not _is_valid_http_origin(origin):
        return PLUGIN_FORM_ORIGIN_FORBIDDEN

    try:
        effective_origin = "{}://{}".format(request.scheme, request.get_host())
    except DisallowedHost:
        return PLUGIN_FORM_ORIGIN_FORBIDDEN

    if origin == effective_origin:
        return PLUGIN_FORM_ORIGIN_SAME_ORIGIN
    if settings.PLUGIN_GATEWAY_FORM_CORS_ALLOW and origin in settings.PLUGIN_GATEWAY_FORM_CORS_ALLOWED_ORIGINS:
        return PLUGIN_FORM_ORIGIN_ALLOWED_CROSS_ORIGIN
    return PLUGIN_FORM_ORIGIN_FORBIDDEN


def is_plugin_form_cross_origin_request(request):
    return classify_plugin_form_request_origin(request) == PLUGIN_FORM_ORIGIN_ALLOWED_CROSS_ORIGIN


def _is_plugin_form_cors_method_allowed(request, allowed_methods):
    method = request.method
    if method == "OPTIONS":
        method = request.META.get("HTTP_ACCESS_CONTROL_REQUEST_METHOD", "")
    return method in allowed_methods


def _get_plugin_form_cors_allowed_methods(request):
    if not settings.PLUGIN_GATEWAY_FORM_CORS_ALLOW:
        return None
    if not is_plugin_form_cross_origin_request(request):
        return None
    return next(
        (allowed_methods for pattern, allowed_methods in PLUGIN_FORM_ROUTES if pattern.match(request.path_info)),
        None,
    )


def allow_plugin_form_cors(sender, request, **kwargs):
    allowed_methods = _get_plugin_form_cors_allowed_methods(request)
    return bool(allowed_methods and _is_plugin_form_cors_method_allowed(request, allowed_methods))


class PluginFormCorsResponseMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.method != "OPTIONS" or "HTTP_ACCESS_CONTROL_REQUEST_METHOD" not in request.META:
            return response

        allowed_methods = _get_plugin_form_cors_allowed_methods(request)
        if allowed_methods and "Access-Control-Allow-Origin" in response:
            response["Access-Control-Allow-Methods"] = ", ".join(allowed_methods)
        return response
