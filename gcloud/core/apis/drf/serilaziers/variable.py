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

from rest_framework import serializers

from pipeline.variable_framework.models import VariableModel
from rest_framework.fields import SerializerMethodField

from pipeline_web.plugin_management.utils import DeprecatedPlugin
from pipeline.component_framework.constants import LEGACY_PLUGINS_VERSION


class VariableSerializer(serializers.ModelSerializer):

    name = serializers.CharField(help_text="变量名", read_only=True)
    form = serializers.CharField(help_text="表单路径", read_only=True)
    type = serializers.CharField(help_text="变量类型", read_only=True)
    tag = serializers.CharField(help_text="变量tag", read_only=True)
    meta_tag = serializers.CharField(help_text="变量meta_tag", read_only=True, allow_null=True)
    description = SerializerMethodField(help_text="变量描述")
    phase = SerializerMethodField(help_text="phase")

    def get_description(self, obj):
        return getattr(obj.get_class(), "desc", "")

    def get_phase(self, obj):
        variable_phase_dict = DeprecatedPlugin.objects.get_variables_phase_dict()
        return variable_phase_dict.get(obj.code, {}).get(
            LEGACY_PLUGINS_VERSION, DeprecatedPlugin.PLUGIN_PHASE_AVAILABLE
        )

    class Meta:
        model = VariableModel
        exclude = ["status", "id"]
