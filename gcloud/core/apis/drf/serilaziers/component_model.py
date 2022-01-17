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
import re

from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import NotFound

from pipeline.exceptions import ComponentNotExistException
from pipeline.component_framework.models import ComponentModel
from pipeline.component_framework.library import ComponentLibrary

from pipeline_web.plugin_management.models import DeprecatedPlugin

group_en_pattern = re.compile(r"(?:\()(.*)(?:\))")


class ComponentModelSerializer(serializers.ModelSerializer):
    output = serializers.SerializerMethodField(read_only=True)
    form = serializers.SerializerMethodField(read_only=True)
    output_form = serializers.SerializerMethodField(read_only=True)
    desc = serializers.SerializerMethodField(read_only=True)
    form_is_embedded = serializers.SerializerMethodField(read_only=True)
    # 国际化
    group_name = serializers.SerializerMethodField(read_only=True)
    group_icon = serializers.SerializerMethodField(read_only=True)
    name = serializers.SerializerMethodField(read_only=True)
    phase = serializers.SerializerMethodField(read_only=True)
    sort_key_group_en = serializers.SerializerMethodField(read_only=True)
    base = serializers.SerializerMethodField(read_only=True)

    def get_output(self, instance):
        return self.component.outputs_format()

    def get_form(self, instance):
        return self.component.form

    def get_output_form(self, instance):
        return self.component.output_form

    def get_desc(self, instance):
        return self.component.desc

    def get_form_is_embedded(self, instance):
        return self.component.form_is_embedded()

    # 国际化
    def get_group_name(self, instance):
        return _(self.component_name[0])

    def get_group_icon(self, instance):
        return self.component.group_icon

    def get_name(self, instance):
        return _(self.component_name[1])

    def get_phase(self, instance):
        return self.component_phase_dict.get(instance.code, {}).get(
            instance.version, DeprecatedPlugin.PLUGIN_PHASE_AVAILABLE
        )

    def get_sort_key_group_en(self, instance):
        group_name_en = group_en_pattern.findall(self.component_name[0] or "")
        return group_name_en[0] if group_name_en else "#"

    def get_base(self, instance):
        return getattr(self.component, "base", None)

    class Meta:
        model = ComponentModel
        exclude = ["status", "id"]

    def to_representation(self, instance):
        try:
            self.component = ComponentLibrary.get_component_class(instance.code, instance.version)
            self.component_name = instance.name.split("-")
            self.component_phase_dict = DeprecatedPlugin.objects.get_components_phase_dict()
        except ComponentNotExistException:
            raise NotFound("Can not found {}({})".format(instance.code, instance.version))
        return super(ComponentModelSerializer, self).to_representation(instance)


class ListSerializer(ComponentModelSerializer):
    base = None


class DetailSerializer(ComponentModelSerializer):
    phase = None
    sort_key_group_en = None
