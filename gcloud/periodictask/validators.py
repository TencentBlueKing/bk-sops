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

from gcloud.utils.validate import ObjectJsonBodyValidator


class SetEnabledForPeriodicTaskValidator(ObjectJsonBodyValidator):
    def validate(self, request, *args, **kwargs):

        valid, err = super().validate(request, *args, **kwargs)

        if not valid:
            return valid, err

        if not isinstance(self.data.get("enabled"), bool):
            return False, "enabled must be a bool"

        return True, ""


class ModifyCronValidator(ObjectJsonBodyValidator):
    def validate(self, request, *args, **kwargs):

        valid, err = super().validate(request, *args, **kwargs)

        if not valid:
            return valid, err

        if not self.data.get("cron"):
            return False, "cron can not be empty"

        return True, ""


class ModifyConstantsValidator(ObjectJsonBodyValidator):
    def validate(self, request, *args, **kwargs):

        valid, err = super().validate(request, *args, **kwargs)

        if not valid:
            return valid, err

        if not isinstance(self.data.get("constants"), dict):
            return False, "constants must be a object"

        return True, ""
