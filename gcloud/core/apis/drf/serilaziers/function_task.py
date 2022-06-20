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

from gcloud.contrib.function.models import FunctionTask
from gcloud.core.apis.drf.serilaziers.taskflow import TaskSerializer


class FunctionTaskSerializer(serializers.ModelSerializer):
    task = TaskSerializer()
    status_name = serializers.CharField(read_only=True)
    create_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S%z", read_only=True)
    claim_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S%z", read_only=True)

    class Meta:
        model = FunctionTask
        fields = "__all__"
