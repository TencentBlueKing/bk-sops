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
import json
import typing

from bkcrypto import constants as crypto_constants
from bkcrypto.asymmetric.configs import KeyConfig as AsymmetricKeyConfig
from bkcrypto.constants import AsymmetricCipherType
from bkcrypto.contrib.django.ciphers import asymmetric_cipher_manager
from bkcrypto.contrib.django.selectors import AsymmetricCipherSelector
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


def decrypt(ciphertext: str, using: typing.Optional[str] = None) -> str:
    using = using or "default"
    # 1. 尝试根据前缀解密
    plaintext: str = AsymmetricCipherSelector(using=using).decrypt(ciphertext)

    # 2. 尝试对明文二次 RSA 解密，用于兼容原逻辑
    try:
        plaintext = asymmetric_cipher_manager.cipher(using=using, cipher_type=AsymmetricCipherType.RSA.value).decrypt(
            plaintext
        )
    except Exception:
        # 已经是明文的情况下会抛出该异常
        pass

    return plaintext


def encrypt(plaintext: str, using: typing.Optional[str] = None) -> str:
    using = using or "default"
    return AsymmetricCipherSelector(using=using).encrypt(plaintext)
