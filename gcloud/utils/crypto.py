# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import base64
import json
import typing

from bkcrypto import constants as crypto_constants
from bkcrypto.asymmetric.configs import KeyConfig as AsymmetricKeyConfig
from bkcrypto.constants import AsymmetricCipherType
from bkcrypto.contrib.django.ciphers import asymmetric_cipher_manager
from bkcrypto.contrib.django.selectors import AsymmetricCipherSelector
from bkcrypto.symmetric.configs import KeyConfig as SymmetricKeyConfig
from django.conf import settings


def get_default_asymmetric_key_config(cipher_type: str) -> AsymmetricKeyConfig:
    """
    获取项目默认非对称加密配置
    :param cipher_type:
    :return:
    """

    if cipher_type == crypto_constants.AsymmetricCipherType.SM2.value:
        private_key_string: str = settings.SM2_PRIV_KEY
        public_key_string: str = json.loads(f'"{settings.SM2_PUB_KEY}"')
    elif cipher_type == crypto_constants.AsymmetricCipherType.RSA.value:
        private_key_string: str = settings.RSA_PRIV_KEY
        public_key_string: str = json.loads(f'"{settings.RSA_PUB_KEY}"')
    else:
        raise NotImplementedError(f"cipher_type -> {cipher_type}")

    return AsymmetricKeyConfig(
        private_key_string=private_key_string.strip("\n"), public_key_string=public_key_string.strip("\n")
    )


def get_default_symmetric_key_config(cipher_type: str) -> SymmetricKeyConfig:
    """
    获取项目默认对称加密配置
    :param cipher_type:
    :return:
    """
    # 统一使用 APP_SECRET 作为对称加密密钥，SDK 会截断，取符合预期的 key length
    return SymmetricKeyConfig(key=settings.SECRET_KEY)


def decrypt(ciphertext: str, using: typing.Optional[str] = None) -> str:
    using = using or "default"
    # 1. 尝试根据前缀解密
    plaintext: str = AsymmetricCipherSelector(using=using).decrypt(ciphertext)

    # 2. 尝试对明文二次 RSA 解密，用于兼容原逻辑
    try:
        # 该校验用于避免非 b64 串 decode 返回空的场景
        # 尝试 base64 解密，如果解密结果是空串，说明 plaintext 为空或者字符非法，说明非密文，直接返回；
        # 如果抛出异常，在外层被 catch 后返回
        if not base64.b64decode(plaintext.encode(encoding="utf-8")):
            return plaintext
        candidate_plaintext: str = asymmetric_cipher_manager.cipher(
            using=using, cipher_type=AsymmetricCipherType.RSA.value
        ).decrypt(plaintext)

        # 空字符串的密文是空字符串
        # 如果解密结果为空，属于解密失败，直接返回原文
        if candidate_plaintext:
            plaintext = candidate_plaintext

    except Exception:
        # 已经是明文的情况下会抛出该异常
        pass

    return plaintext


def encrypt(plaintext: str, using: typing.Optional[str] = None) -> str:
    using = using or "default"
    return AsymmetricCipherSelector(using=using).encrypt(plaintext)
