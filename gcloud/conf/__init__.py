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

import datetime
import decimal
import uuid
import json

from django.utils.functional import Promise
from django.utils.encoding import force_text
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.timezone import is_aware
from django.conf import settings as django_settings

from gcloud.conf import default_settings


class GcloudSettings(object):

    def __getattr__(self, key):
        if hasattr(django_settings, key):
            return getattr(django_settings, key)

        if hasattr(default_settings, key):
            return getattr(default_settings, key)

        raise AttributeError('Settings object has no attribute %s' % key)


settings = GcloudSettings()


def default(self, o):
    # See "Date Time String Format" in the ECMA-262 specification.
    if isinstance(o, Promise):
        return force_text(o)
    elif isinstance(o, datetime.datetime):
        r = o.isoformat()
        if o.microsecond:
            r = r[:23] + r[26:]
        if r.endswith('+00:00'):
            r = r[:-6] + 'Z'
        return r
    elif isinstance(o, datetime.date):
        return o.isoformat()
    elif isinstance(o, datetime.time):
        if is_aware(o):
            raise ValueError("JSON can't represent timezone-aware times.")
        r = o.isoformat()
        if o.microsecond:
            r = r[:12]
        return r
    elif isinstance(o, (decimal.Decimal, uuid.UUID)):
        return str(o)
    else:
        try:
            return super(DjangoJSONEncoder, self).default(o)
        except TypeError:
            return str(o)


DjangoJSONEncoder.default = default

json.JSONEncoder = DjangoJSONEncoder
