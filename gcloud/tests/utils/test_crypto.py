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
import random

from bkcrypto import constants as bkcrypto_constants
from bkcrypto.asymmetric.ciphers import BaseAsymmetricCipher
from bkcrypto.asymmetric.options import RSAAsymmetricOptions
from bkcrypto.contrib.django.ciphers import get_asymmetric_cipher
from bkcrypto.contrib.django.selectors import AsymmetricCipherSelector
from django.test import TestCase

from gcloud.utils import crypto


class CryptoTestCase(TestCase):

    plaintext: str = None
    legacy_cipher: BaseAsymmetricCipher = None

    def setUp(self) -> None:
        self.plaintext = "123" * random.randint(1, 100)
        self.legacy_cipher = get_asymmetric_cipher(
            cipher_type=bkcrypto_constants.AsymmetricCipherType.RSA.value,
            cipher_options={
                bkcrypto_constants.AsymmetricCipherType.RSA.value: RSAAsymmetricOptions(
                    public_key_string=crypto.get_default_asymmetric_key_config(
                        cipher_type=bkcrypto_constants.AsymmetricCipherType.RSA.value
                    ).public_key_string,
                    padding=bkcrypto_constants.RSACipherPadding.PKCS1_v1_5,
                )
            },
        )

    def test_ciphertext_without_prefix(self):
        """测试不带前缀的密文，模拟存量数据场景"""
        self.assertEqual(crypto.decrypt(ciphertext=self.legacy_cipher.encrypt(self.plaintext)), self.plaintext)

    def test_ciphertext_with_secondary_encryption(self):
        """测试原密文再次保存被二次加密的场景"""
        ciphertext_without_prefix: str = self.legacy_cipher.encrypt(self.plaintext)
        ciphertext: str = AsymmetricCipherSelector().encrypt(ciphertext_without_prefix)
        self.assertEqual(crypto.decrypt(ciphertext=ciphertext), self.plaintext)

    def test_ciphertext(self):
        """模拟新数据加密携带前缀的场景"""
        ciphertext: str = AsymmetricCipherSelector().encrypt(plaintext=self.plaintext)
        print(ciphertext)
        self.assertTrue(ciphertext.startswith(f"{bkcrypto_constants.AsymmetricCipherType.RSA.value.lower()}_str:::"))
        self.assertEqual(crypto.decrypt(ciphertext=ciphertext), self.plaintext)

    def test_plaintext(self):
        self.assertEqual(self.plaintext, crypto.decrypt(self.plaintext))

    def test_invalid_b64(self):
        self.assertEqual("AAAA", crypto.decrypt("AAAA"))
