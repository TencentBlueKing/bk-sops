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

WSGI config for testapp3 project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import os

# ============ KMS解密：Web服务入口 ============
# 说明：当BKPAAS_KMS_ENABLED=true时，从/etc/secrets解密敏感配置
# 影响范围：default/web, callback/web, api/web 三个模块的Web进程
# 文档参考：Python SaaS 接入 KMS - blueapps多租户版(2.2节)
if os.getenv('BKPAAS_KMS_ENABLED', '').lower() == 'true':
    from blueapps.contrib.encrypt import decrypt_encrypted_environment
    decrypt_encrypted_environment()

from blueapps.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

application = get_wsgi_application()
