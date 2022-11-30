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


class PluginCodeQuerySerializer(serializers.Serializer):
    plugin_code = serializers.CharField(help_text="插件服务编码")


class LogQuerySerializer(PluginCodeQuerySerializer):
    plugin_code = serializers.CharField(help_text="插件服务编码")
    trace_id = serializers.CharField(help_text="Trace ID")
    scroll_id = serializers.CharField(help_text="翻页标识字段", required=False)


class PluginDetailQuerySerializer(PluginCodeQuerySerializer):
    plugin_version = serializers.CharField(help_text="插件服务版本")
    with_app_detail = serializers.BooleanField(help_text="是否返回插件APP信息", required=False, default=False)


class StandardResponseSerializer(serializers.Serializer):
    result = serializers.BooleanField(help_text="请求是否成功")
    message = serializers.CharField(help_text="请求额外信息，result 为 false 时读取")


class PluginInfoSerializer(serializers.Serializer):
    code = serializers.CharField(help_text="插件Code")
    name = serializers.CharField(help_text="插件名称")
    logo_url = serializers.CharField(help_text="Logo地址")


class PluginDeployedStatusSerializer(serializers.Serializer):
    stag = serializers.DictField(help_text="预发布环境部署状态")
    prod = serializers.DictField(help_text="正式环境部署状态")


class PluginProfileSerializer(serializers.Serializer):
    contact = serializers.CharField(help_text="插件联系人")
    introduction = serializers.CharField(help_text="插件简介")


class PluginAppDetailResponseSerializer(serializers.Serializer):
    code = serializers.CharField(help_text="插件服务应用Code")
    name = serializers.CharField(help_text="插件服务应用名称")
    updated = serializers.TimeField(help_text="插件服务应用更新时间")
    url = serializers.CharField(help_text="插件服务默认地址")
    urls = serializers.ListField(help_text="插件服务支持请求地址列表")


class PluginListSerializer(serializers.Serializer):
    plugins = PluginInfoSerializer(help_text="插件列表信息", many=True)
    count = serializers.IntegerField(help_text="插件条数")


class PluginListResponseSerializer(StandardResponseSerializer):
    data = PluginListSerializer(help_text="插件信息", many=True)


class PluginDetailedInfoSerializer(serializers.Serializer):
    plugin = PluginInfoSerializer(help_text="插件信息")
    deployed_statuses = PluginDeployedStatusSerializer(help_text="部署状态信息")
    profile = PluginProfileSerializer(help_text="插件描述信息")


class PluginDetailListSerializer(serializers.Serializer):
    next_offset = serializers.IntegerField(help_text="下一次请求偏移量")
    return_plugin_count = serializers.IntegerField(help_text="本次返回插件条数")
    plugins = PluginDetailedInfoSerializer(help_text="插件信息及部署状态信息", many=True)


class PluginTagSerializer(serializers.Serializer):
    code_name = serializers.CharField(help_text="Tag 编码")
    name = serializers.CharField(help_text="Tag 名称")
    id = serializers.IntegerField(help_text="Tag ID")


class PluginDetailListResponseSerializer(StandardResponseSerializer):
    data = PluginDetailListSerializer(help_text="插件列表及详情信息")


class PluginTagListResponseSerializer(StandardResponseSerializer):
    data = serializers.ListSerializer(help_text="插件tag列表", child=PluginTagSerializer())


class PluginListQuerySerializer(serializers.Serializer):
    search_term = serializers.CharField(help_text="插件名称搜索过滤字段", required=False)
    limit = serializers.IntegerField(help_text="分页配置，接口一次最多100条", required=False, default=100)
    offset = serializers.IntegerField(help_text="分页配置", required=False, default=0)
    tag_id = serializers.IntegerField(help_text="插件tag id", required=False)

    def validate_limit(self, limit):
        if limit < 0:
            raise serializers.ValidationError("limit must be greater than 0")
        if limit > 100:
            raise serializers.ValidationError("limit must be smaller than 100")
        return limit

    def validate_offset(self, offset):
        if offset < 0:
            raise serializers.ValidationError("offset must be greater than 0")
        return offset


class PluginDetailListQuerySerializer(PluginListQuerySerializer):
    exclude_not_deployed = serializers.BooleanField(help_text="是否排除当前环境未部署数据", required=False, default=True)
    fetch_all = serializers.BooleanField(help_text="是否一次性获取全部数据", required=False, default=False)

    def validate(self, data):
        if data.get("fetch_all") and not data.get("search_term"):
            raise serializers.ValidationError("cannot fetch all plugins without search_term params")
        return data


class PluginTagsListQuerySerializer(serializers.Serializer):
    with_unknown_tag = serializers.BooleanField(help_text="是否返回未知 tag 标签", required=False)


class LogResponseSerializer(StandardResponseSerializer):
    class LogSerializer(serializers.Serializer):
        scroll_id = serializers.CharField(help_text="翻页标识字段，获取下一页时传入该值")
        total = serializers.IntegerField(help_text="日志总数")
        logs = serializers.CharField(help_text="日志内容字符串")

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
        app = PluginAppDetailResponseSerializer(help_text="插件服务APP相关详情信息", required=False)

    data = DetailDataSerializer(help_text="插件详情数据")
