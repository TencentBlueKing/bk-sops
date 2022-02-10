# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2022 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import ujson as json

from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from gcloud.contrib.collection.models import Collection
from gcloud.utils.drf.serializer import ReadWriteSerializerMethodField


class CollectionSerializer(serializers.ModelSerializer):

    extra_info = ReadWriteSerializerMethodField(help_text=_("额外信息"))

    def get_extra_info(self, obj):
        if not getattr(obj, "extra_info") or not obj.extra_info:
            return dict()
        return json.loads(obj.extra_info)

    def set_extra_info(self, data):
        return {"extra_info": json.dumps(data)}

    class Meta:
        model = Collection
        fields = "__all__"
