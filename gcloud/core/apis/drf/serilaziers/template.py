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

import json
import logging

from rest_framework import serializers

from gcloud.utils.drf.serializer import ReadWriteSerializerMethodField

logger = logging.getLogger("root")


class BaseTemplateSerializer(serializers.ModelSerializer):
    notify_type = ReadWriteSerializerMethodField(help_text="通知类型")
    notify_receivers = ReadWriteSerializerMethodField(help_text="通知人列表")

    def get_notify_type(self, obj):
        default_notify_type = {"success": [], "fail": []}
        try:
            notify_type = json.loads(obj.notify_type)
            # 对于旧数据中解析出来为[]的情况，统一返回默认值
            return notify_type if notify_type else default_notify_type
        except Exception as e:
            logger.exception(f"[get_notify_type] error: {e}")
            return default_notify_type

    def set_notify_type(self, data):
        return {"notify_type": json.dumps(data)}

    def get_notify_receivers(self, obj):
        if not getattr(obj, "notify_receivers") or not obj.notify_receivers:
            return json.dumps(dict())
        return json.dumps(obj.notify_receivers)

    def set_notify_receivers(self, data):
        return {"notify_receivers": json.dumps(data)}
