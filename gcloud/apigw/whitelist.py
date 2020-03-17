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

import logging

from gcloud.core.models import EnvironmentVariables

logger = logging.getLogger('root')


class EnvWhitelist(object):

    def __init__(self, transient_list, env_key):
        self.transient_list = transient_list
        self.env_key = env_key

    def has(self, app):
        if app in self.transient_list:
            return True

        env_list_var = EnvironmentVariables.objects.get_var(self.env_key)
        if not env_list_var:
            return False

        try:
            env_list = set(env_list_var.split(','))
        except Exception:
            logger.exception('resolve {} error.'.format(self.env_key))
            return False

        return app in env_list
