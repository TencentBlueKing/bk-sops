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

from bkcrypto import constants as crypto_constants
from bkcrypto.asymmetric.configs import KeyConfig as AsymmetricKeyConfig
from Crypto import Util
from Crypto.Cipher import PKCS1_v1_5 as PKCS1_v1_5_cipher
from Crypto.PublicKey import RSA
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


def get_nodeman_asymmetric_key_config(cipher_type: str) -> AsymmetricKeyConfig:
    """
    获取节点管理非对称加密配置
    :param cipher_type:
    :return:
    """
    pass


def _get_block_size(key_obj, is_encrypt=True) -> int:
    """
    获取加解密最大片长度，用于分割过长的文本，单位：bytes
    :param key_obj:
    :param is_encrypt:
    :return:
    """
    block_size = Util.number.size(key_obj.n) / 8
    reserve_size = 11
    if not is_encrypt:
        reserve_size = 0
    return int(block_size - reserve_size)


def _block_list(lst, block_size):
    """
    序列切片
    :param lst:
    :param block_size:
    :return:
    """
    for idx in range(0, len(lst), block_size):
        yield lst[idx : idx + block_size]


def encrypt_auth_key(auth_key, public_key_name, public_key):
    """
    @summary: rsa分块加密
    @param auth_key: 待加密的敏感信息
    @param public_key_name: 公钥名称
    @param public_key: 公钥
    """
    public_key_obj = RSA.importKey(public_key)
    message_bytes = auth_key.encode(encoding="utf-8")
    encrypt_message_bytes = b""
    block_size = _get_block_size(public_key_obj)
    cipher = PKCS1_v1_5_cipher.new(public_key_obj)
    for block in _block_list(message_bytes, block_size):
        encrypt_message_bytes += cipher.encrypt(block)

    encrypt_message = base64.b64encode(public_key_name.encode("utf-8")) + base64.b64encode(encrypt_message_bytes)
    return encrypt_message.decode(encoding="utf-8")


def decrypt_auth_key(encrypt_message, private_key):
    """
    @summary: rsa分块解密
    @param encrypt_message: 密文
    @param private_key: rsa私钥
    @return: 解密后的信息
    """
    # TODO 要改的
    decrypt_message_bytes = b""
    private_key_obj = RSA.importKey(private_key.strip("\n"))
    encrypt_message_bytes = base64.b64decode(encrypt_message)
    block_size = _get_block_size(private_key_obj, is_encrypt=False)
    cipher = PKCS1_v1_5_cipher.new(private_key_obj)
    for block in _block_list(encrypt_message_bytes, block_size):
        decrypt_message_bytes += cipher.decrypt(block, "")
    return decrypt_message_bytes.decode(encoding="utf-8")
