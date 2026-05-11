# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import hashlib
import hmac

from django.conf import settings

# 签名分隔符，选用不会出现在 Fernet token 字符集（URL-safe base64）中的字符
SIGNATURE_DELIMITER = "~"


def sign_callback_token(fernet_token):
    """为 Fernet 生成的 token 追加 HMAC-SHA256 二次签名。

    :param fernet_token: str, Fernet.encrypt 生成的 URL-safe base64 字符串
    :return: str, 形如 "<fernet_token>~<signature>"
    """
    secret = getattr(settings, "CALLBACK_SIGN_SECRET", b"")
    if not secret:
        # 启动期已经阻断该情况，这里仅作兜底保护
        raise RuntimeError("CALLBACK_SIGN_SECRET is not configured")
    signature = hmac.new(secret, fernet_token.encode("utf-8"), hashlib.sha256).hexdigest()
    return "{}{}{}".format(fernet_token, SIGNATURE_DELIMITER, signature)


def verify_and_split_token(signed_token):
    """校验 HMAC 二次签名并拆分出原始 Fernet token。

    :param signed_token: str, sign_callback_token 的返回值
    :return: (bool, str_or_None) (校验是否通过, 拆分出的 Fernet token)
    """
    secret = getattr(settings, "CALLBACK_SIGN_SECRET", b"")
    if not secret:
        return False, None
    if not signed_token or SIGNATURE_DELIMITER not in signed_token:
        return False, None
    fernet_token, _, signature = signed_token.rpartition(SIGNATURE_DELIMITER)
    if not fernet_token or not signature:
        return False, None
    expected = hmac.new(secret, fernet_token.encode("utf-8"), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, signature):
        return False, None
    return True, fernet_token
