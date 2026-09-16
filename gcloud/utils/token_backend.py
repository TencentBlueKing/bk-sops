# -*- coding: utf-8 -*-
import json
import logging
import os

import requests
from blueapps.account import get_user_model
from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.db import IntegrityError

logger = logging.getLogger("component")

ROLE_TYPE_ADMIN = "1"
BK_LOGIN_USERINFO_PATH = "/login/api/v3/open/bk-tokens/userinfo/"
REQUEST_TIMEOUT = 10


def get_bk_token_userinfo(bk_token):
    """Validate a bk_token and return its user information through bk-login APIGW."""

    endpoint = settings.BK_API_URL_TMPL.format(api_name="bk-login").rstrip("/")
    url = "{}/prod{}".format(endpoint, BK_LOGIN_USERINFO_PATH)
    app_tenant_id = os.getenv("BKPAAS_APP_TENANT_ID") or "system"
    headers = {
        "X-Bkapi-Authorization": json.dumps({"bk_app_code": settings.APP_CODE, "bk_app_secret": settings.SECRET_KEY}),
        "X-Bk-Tenant-Id": app_tenant_id,
    }

    try:
        response = requests.get(url, headers=headers, params={"bk_token": bk_token}, timeout=REQUEST_TIMEOUT)
    except requests.RequestException:
        logger.exception("bk-login userinfo request failed")
        return None

    try:
        result = response.json()
    except ValueError:
        result = {}

    if response.status_code != 200 or not isinstance(result.get("data"), dict):
        error = result.get("error") if isinstance(result.get("error"), dict) else {}
        logger.error(
            "bk-login userinfo rejected: status_code=%s error_code=%s request_id=%s",
            response.status_code,
            error.get("code") or result.get("code"),
            result.get("request_id", ""),
        )
        return None
    return result["data"]


class TenantAwareTokenBackend(ModelBackend):
    """Authenticate desktop bk_token for a global multi-tenant application."""

    def authenticate(self, request=None, bk_token=None, **credentials):
        if not bk_token:
            return None

        user_info = get_bk_token_userinfo(bk_token)
        if not user_info or not user_info.get("bk_username"):
            return None

        user_model = get_user_model()
        try:
            user, _ = user_model.objects.get_or_create(username=user_info["bk_username"])
            user.display_name = user_info.get("display_name", "")
            user.tenant_id = user_info.get("tenant_id", "")
            if not user.is_superuser and not user.is_staff:
                # bk-login deployments may expose the platform role as either
                # ``role`` or the legacy-compatible ``bk_role`` field.
                is_admin = str(user_info.get("bk_role", user_info.get("role", ""))) == ROLE_TYPE_ADMIN
                user.is_superuser = is_admin
                user.is_staff = is_admin
            user.save()
            return user
        except IntegrityError:
            logger.exception("create or update token user failed")
            return None
