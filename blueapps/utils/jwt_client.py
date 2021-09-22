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
"""

import cryptography  # noqa
import jwt

from jwt import exceptions as jwt_exceptions

from django.conf import settings

from blueapps.utils.logger import logger
from blueapps.utils.fancy_dict import FancyDict


class JWTClient(object):
    def __init__(self, request):
        self.request = request

        self.raw_content = request.META.get(
            getattr(settings, "APIGW_JWT_KEY", "HTTP_X_BKAPI_JWT"), ""
        )
        self.error_message = ""
        self.is_valid = False

        self.payload = {}
        self.headers = {}
        self.get_jwt_info()

        self.app = self.get_app_model()
        self.user = self.get_user_model()

    def get_app_model(self):
        return FancyDict(self.payload.get("app", {}))

    def get_user_model(self):
        return FancyDict(self.payload.get("user", {}))

    def get_jwt_info(self):
        if not self.raw_content:
            self.error_message = "X_BKAPI_JWT not in http header or it is empty, please called API through API Gateway"
            return False
        try:
            self.headers = jwt.get_unverified_header(self.raw_content)
            self.payload = jwt.decode(
                self.raw_content, settings.APIGW_PUBLIC_KEY, issuer="APIGW"
            )
            self.is_valid = True
        except jwt_exceptions.InvalidKeyError:
            self.error_message = "APIGW_PUBLIC_KEY error"
        except jwt_exceptions.DecodeError:
            self.error_message = "Invalid X_BKAPI_JWT, wrong format or value"
        except jwt_exceptions.ExpiredSignatureError:
            self.error_message = "Invalid X_BKAPI_JWT, which is expired"
        except jwt_exceptions.InvalidIssuerError:
            self.error_message = "Invalid X_BKAPI_JWT, which is not from API Gateway"
        except Exception as error:
            self.error_message = error.message

        if self.error_message:
            logger.exception(
                "[jwt_client] decode jwt fail, err: %s" % self.error_message
            )

    def __str__(self):
        return "<{headers}, {payload}>".format(
            headers=self.headers, payload=self.payload
        )
