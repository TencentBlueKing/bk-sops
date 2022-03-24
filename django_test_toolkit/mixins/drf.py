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
from mock import patch, MagicMock

from .base import LifeCycleHooksMixin


class DrfPermissionExemptMixin(LifeCycleHooksMixin):
    """豁免DRF ViewSet权限校验，需要在子类中配置对应ViewSet的路径"""

    VIEWSET_PATH = None

    def setUp(self):
        if self.VIEWSET_PATH:
            patch(f"{self.VIEWSET_PATH}.permission_classes", MagicMock(return_value=[])).start()
