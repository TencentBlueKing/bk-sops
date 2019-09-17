# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import json
import logging

from django.conf import settings
from django.http import HttpResponse
# 非强制安装PyJWT
try:
    from jwt import exceptions as jwt_exceptions
    import jwt
    has_jwt = True
except ImportError:
    has_jwt = False

try:
    import cryptography    # noqa
    has_crypto = True
except ImportError:
    has_crypto = False

from .utils import FancyDict

LOG = logging.getLogger('component')


class JWTClient(object):
    JWT_KEY_NAME = 'HTTP_X_BKAPI_JWT'

    def __init__(self, request):
        self.request = request
        self.raw_content = request.META.get(self.JWT_KEY_NAME, '')
        self.error_message = ''
        self.is_valid = False

        self.payload = {}
        self.headers = {}
        self.get_jwt_info()

        self.app = self.get_app_model()
        self.user = self.get_user_model()

    def get_app_model(self):
        return FancyDict(self.payload.get('app', {}))

    def get_user_model(self):
        return FancyDict(self.payload.get('user', {}))

    def get_jwt_info(self):
        if has_jwt is False:
            self.error_message = "PyJWT not installed, please add PyJWT to requirements.txt add deploy saas again"
            return False
        if has_crypto is False:
            self.error_message = ("cryptography not installed, please add PyJWT to requirements.txt add "
                                  "deploy saas again")
            return False

        if not self.raw_content:
            self.error_message = "X_BKAPI_JWT not in http header or it is empty, please called API through API Gateway"
            return False
        try:
            self.headers = jwt.get_unverified_header(self.raw_content)
            self.payload = jwt.decode(self.raw_content, settings.APIGW_PUBLIC_KEY, issuer='APIGW')
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
            LOG.exception('decode jwt fail')
            self.error_message = error.message

    def __unicode__(self):
        return '<%s, %s>' % (self.headers, self.payload)


def jwt_invalid_view(request):
    """无效jwt返回
    """
    LOG.warning('jwt_invalid %s' % request.jwt.error_message)
    data = {'result': False, 'data': None, 'message': request.jwt.error_message}
    return HttpResponse(json.dumps(data), content_type='application/json')
