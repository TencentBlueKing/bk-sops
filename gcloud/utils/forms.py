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

import ujson as json
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class JsonField(forms.CharField):
    default_error_messages = {
        "invalid": _("invalid json string"),
    }

    def validate(self, value):
        super(JsonField, self).validate(value)

        try:
            json.loads(value)
        except Exception:
            raise ValidationError(self.error_messages["invalid"], code="invalid")
        else:
            return value


class JsonListField(JsonField):
    default_error_messages = {
        "invalid": _("json.loads result is not instance of list or tuple "),
    }

    def validate(self, value):
        super(JsonListField, self).validate(value)

        data = json.loads(value)

        if not isinstance(data, (list, tuple)):
            raise ValidationError(self.error_messages["invalid"], code="invalid")

        return value


class JsonDictField(JsonField):
    default_error_messages = {
        "invalid": _("json.loads result is not list"),
    }

    def validate(self, value):
        super(JsonListField, self).validate(value)

        data = json.loads(value)

        if not isinstance(data, dict):
            raise ValidationError(self.error_messages["invalid"], code="invalid")

        return value
