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

import os
import sys

if __name__ == "__main__":
    # ============ KMS解密：Django管理命令入口 ============
    # 说明：当BKPAAS_KMS_ENABLED=true时，从/etc/secrets解密敏感配置
    # 影响范围：default/beat, pipeline/node-timeout, bin/pre_release中的所有python manage.py命令
    # 文档参考：Python SaaS 接入 KMS - blueapps多租户版(2.2节)
    if os.getenv('BKPAAS_KMS_ENABLED', '').lower() == 'true':
        from blueapps.contrib.encrypt import decrypt_encrypted_environment
        decrypt_encrypted_environment()

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
