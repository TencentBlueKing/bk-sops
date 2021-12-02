# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.


BK JWT - settings option
1. settings.APIGW_ENABLED: if enabled, it will automatically get the apigw public key
2. settings.APIGW_PUBLIC_KEY: If you get the apigw public key manually
3. settings.APIGW_API_ACCOUNT: The account used to call the apigw API
4. settings.APIGW_JWT_KEY: Apigw uses this key to pass jwt encrypted content
"""

import logging

from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.utils.translation import ugettext_lazy as _

from blueapps.account import get_user_model
from blueapps.utils.jwt_client import JWTClient

logger = logging.getLogger("component")  # pylint: disable=invalid-name


class BkJwtBackend(ModelBackend):
    def authenticate(self, request=None):
        logger.debug(u"进入 BK_JWT 认证 Backend")

        try:
            verify_data = self.verify_bk_jwt_request(request)
        except Exception as err:  # pylint: disable=broad-except
            logger.exception(u"[BK_JWT]校验异常: %s" % err)
            return None

        if not verify_data["result"] or not verify_data["data"]:
            logger.error(u"BK_JWT 验证失败： %s" % verify_data)
            return None

        user_info = verify_data["data"]["user"]
        user_model = get_user_model()
        try:
            user, _ = user_model.objects.get_or_create(
                defaults={"nickname": user_info["bk_username"]},
                username=user_info["bk_username"],
            )
        except Exception as err:  # pylint: disable=broad-except
            logger.exception(u"自动创建 & 更新 User Model 失败: %s" % err)
            return None

        return user

    def get_user(self, user_id):
        user_model = get_user_model()
        try:
            return user_model.objects.get(pk=user_id)
        except user_model.DoesNotExist:
            return None

    @staticmethod
    def verify_bk_jwt_request(request):
        """
        验证 BK_JWT 请求
        @param {string} x_bkapi_jwt JWT请求头
        @return {dict}
            {
                'result': True,
                'message': '',
                'data': {
                    'user': {
                        'bk_username': '调用方用户'
                    },
                    'app': {
                        'bk_app_code': '调用方app'
                    }
                }
            }
        """
        ret = {"result": False, "message": "", "data": {}}

        jwt = JWTClient(request)
        if not jwt.is_valid:
            ret["message"] = _(u"jwt_invalid: %s") % jwt.error_message
            return ret

        # verify: user && app
        app = jwt.get_app_model()
        if not app["verified"]:
            ret["message"] = app.get("valid_error_message", _(u"APP鉴权失败"))
            ret["data"]["app"] = app
            return ret

        if not app.get("bk_app_code"):
            app["bk_app_code"] = app["app_code"]

        user = jwt.get_user_model()
        # ESB默认需要校验用户信息
        use_esb_white_list = getattr(settings, "USE_ESB_WHITE_LIST", True)

        if not use_esb_white_list and not user["verified"]:
            ret["message"] = user.get("valid_error_message", _(u"用户鉴权失败且不支持ESB白名单"))
            ret["data"]["user"] = user
            return ret
        if not user.get("bk_username"):
            user["bk_username"] = user["username"]

        if not app["bk_app_code"]:
            ret["message"] = _(u"无法获取bk_app_code")
            return ret

        if not user["bk_username"]:
            ret["message"] = _(u"无法获取用户信息")
            return ret

        ret["result"] = True
        ret["data"] = {"user": user, "app": app}
        return ret
