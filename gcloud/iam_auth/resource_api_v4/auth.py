import base64
import binascii
import hmac

from django.conf import settings
from django.core.cache import cache

from gcloud.iam_auth.client import IAMV4Client


class CallbackUnauthorized(Exception):
    pass


class CallbackTenantMissing(Exception):
    pass


def require_callback_tenant(request):
    header_name = settings.IAM_V4_TENANT_HEADER
    meta_name = "HTTP_{}".format(header_name.upper().replace("-", "_"))
    # IAM V4 guarantees Authorization and X-Request-Id for callbacks, but the
    # protocol does not require a tenant header. Prefer an explicitly
    # forwarded tenant and otherwise use the System registration tenant.
    tenant_id = request.META.get(meta_name, "") or getattr(settings, "IAM_V4_MODEL_REGISTRATION_TENANT_ID", "")
    if not tenant_id:
        raise CallbackTenantMissing("tenant header is required")
    return tenant_id


def get_cached_callback_token(tenant_id, force_refresh=False):
    cache_key = "iam:v4:callback-token:{}:{}".format(settings.BK_IAM_SYSTEM_ID, tenant_id)
    if force_refresh:
        cache.delete(cache_key)
    token = cache.get(cache_key)
    if not token:
        token = IAMV4Client().retrieve_callback_token(tenant_id)
        cache.set(cache_key, token, settings.IAM_V4_CALLBACK_TOKEN_CACHE_SECONDS)
    return token


def authenticate_callback(request):
    tenant_id = require_callback_tenant(request)
    authorization = request.META.get("HTTP_AUTHORIZATION", "")
    try:
        scheme, encoded = authorization.split(" ", 1)
        decoded = base64.b64decode(encoded, validate=True).decode("utf-8")
        username, password = decoded.split(":", 1)
    except (ValueError, UnicodeDecodeError, binascii.Error):
        raise CallbackUnauthorized("basic authentication failed")
    if scheme.lower() != "basic" or not hmac.compare_digest(username, "bk_iam"):
        raise CallbackUnauthorized("basic authentication failed")
    expected_token = get_cached_callback_token(tenant_id)
    if not hmac.compare_digest(password, expected_token):
        expected_token = get_cached_callback_token(tenant_id, force_refresh=True)
        if not hmac.compare_digest(password, expected_token):
            raise CallbackUnauthorized("basic authentication failed")
    return tenant_id
