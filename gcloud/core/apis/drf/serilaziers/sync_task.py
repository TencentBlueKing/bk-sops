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
from rest_framework import serializers

from gcloud.external_plugins.models.sync import SyncTask, SYNC_TASK_CREATED


class SyncTaskSerializer(serializers.ModelSerializer):
    creator_name = serializers.CharField(source="creator", read_only=True)
    status_display = serializers.SerializerMethodField(read_only=True)
    start_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S %z", read_only=True)
    finish_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S %z", read_only=True)
    create_method = serializers.ChoiceField(choices=SYNC_TASK_CREATED)
    creator = serializers.CharField(max_length=32)

    def get_status_display(self, instance):
        return instance.get_status_display()

    class Meta:
        model = SyncTask
        fields = "__all__"
