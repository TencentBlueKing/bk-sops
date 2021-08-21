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
from rest_framework import serializers


class PluginCodeQuerySerializer(serializers.Serializer):
    plugin_code = serializers.CharField(help_text="插件服务编码")


class LogQuerySerializer(PluginCodeQuerySerializer):
    trace_id = serializers.CharField(help_text="Trace ID")


class PluginVersionQuerySerializer(PluginCodeQuerySerializer):
    plugin_version = serializers.CharField(help_text="插件服务版本")


class StandardResponseSerializer(serializers.Serializer):
    result = serializers.BooleanField(help_text="请求是否成功")
    message = serializers.CharField(help_text="请求额外信息，result 为 false 时读取")


class PluginInfoSerializer(serializers.Serializer):
    code = serializers.CharField(help_text="插件Code")
    name = serializers.CharField(help_text="插件名称")
    logo_url = serializers.CharField(help_text="Logo地址")


class PluginAppDetailResponseSerializer(serializers.Serializer):
    code = serializers.CharField(help_text="插件服务应用Code")
    name = serializers.CharField(help_text="插件服务应用名称")
    updated = serializers.TimeField(help_text="插件服务应用更新时间")


class PluginListSerializer(serializers.Serializer):
    plugins = PluginInfoSerializer(help_text="插件列表信息", many=True)
    count = serializers.IntegerField(help_text="插件条数")


class PluginListResponseSerializer(StandardResponseSerializer):
    data = PluginListSerializer(help_text="插件信息", many=True)


class PluginListQuerySerializer(serializers.Serializer):
    search_term = serializers.CharField(help_text="插件名称搜索过滤字段", required=False)
    limit = serializers.IntegerField(help_text="分页配置，接口一次最多100条", required=False, default=100)
    offset = serializers.IntegerField(help_text="分页配置", required=False, default=0)


class LogResponseSerializer(StandardResponseSerializer):
    class LogSerializer(serializers.Serializer):
        log = serializers.CharField(help_text="日志内容")

    data = LogSerializer(help_text="日志内容")


class MetaResponseSerializer(StandardResponseSerializer):
    class MetaSerializer(serializers.Serializer):
        code = serializers.CharField(help_text="插件唯一标识")
        description = serializers.CharField(help_text="插件描述信息")
        versions = serializers.ListField(help_text="版本列表", child=serializers.CharField(help_text="版本号"))
        language = serializers.CharField(help_text="插件开发语言")
        framework_version = serializers.CharField(help_text="插件框架版本")
        runtime_version = serializers.CharField(help_text="插件运行时版本")

    data = MetaSerializer(help_text="插件元数据")


class DetailResponseSerializer(StandardResponseSerializer):
    class DetailDataSerializer(serializers.Serializer):
        class SchemaSerializer(serializers.Serializer):
            class PropertySerializer(serializers.Serializer):
                title = serializers.CharField(help_text="字段名")
                type = serializers.CharField(help_text="字段类型")
                description = serializers.CharField(help_text="字段描述")
                default = serializers.CharField(help_text="默认值")

            type = serializers.CharField(help_text="字段类型")
            properties = PropertySerializer(help_text="字段详情")
            required = serializers.ListField(help_text="必填字段", child=serializers.CharField(help_text="字段 key"))
            definitions = serializers.DictField(help_text="引用对象详情，结构同 SchemaSerializer")

        class InputsFieldsSerializer(SchemaSerializer):
            pass

        class ContextInputsFieldsSerializer(SchemaSerializer):
            pass

        class OutputsFieldsSerializer(SchemaSerializer):
            pass

        class DetailFormsSerializer(serializers.Serializer):
            renderform = serializers.CharField(help_text="renderform 表单数据")

        version = serializers.CharField(help_text="版本号")
        inputs = InputsFieldsSerializer(help_text="输入模型")
        context_inputs = ContextInputsFieldsSerializer(help_text="上下文输入模型")
        outputs = OutputsFieldsSerializer(help_text="输出模型")
        forms = DetailFormsSerializer(help_text="表单数据")

    data = DetailDataSerializer(help_text="插件详情数据")
