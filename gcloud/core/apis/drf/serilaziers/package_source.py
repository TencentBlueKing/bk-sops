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

from gcloud.external_plugins.protocol.readers import validate_s3_service_address
from gcloud.external_plugins import exceptions


class PackageSourceSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    desc = serializers.CharField()
    category = serializers.CharField()
    type = serializers.CharField()
    base_source_id = serializers.IntegerField(allow_null=True)
    details = serializers.DictField(read_only=True)
    imported_plugins = serializers.ListField(read_only=True, allow_null=True)
    packages = serializers.DictField()
    is_valid = serializers.SerializerMethodField(read_only=True)
    validation_message = serializers.SerializerMethodField(read_only=True)

    def get_is_valid(self, obj):
        """
        检查包源是否有效（仅针对 S3 类型检查域名白名单）
        """
        # 只对 S3 类型的包源进行域名白名单验证（type 字段存储为小写 "s3"）
        if obj.type.upper() == "S3":
            service_address = None

            # 原始包源：直接有 service_address 属性
            if hasattr(obj, 'service_address'):
                service_address = obj.service_address
            # 缓存包源：通过 base_source 访问
            elif hasattr(obj, 'base_source') and obj.base_source:
                if hasattr(obj.base_source, 'service_address'):
                    service_address = obj.base_source.service_address

            if service_address:
                try:
                    validate_s3_service_address(service_address)
                    return True
                except exceptions.ForbiddenExternalPluginSourceError:
                    return False

        # 其他类型默认为有效
        return True

    def get_validation_message(self, obj):
        """
        获取验证失败的错误信息
        """
        # 只对 S3 类型的包源进行域名白名单验证（type 字段存储为小写 "s3"）
        if obj.type.upper() == "S3":
            service_address = None

            # 原始包源：直接有 service_address 属性
            if hasattr(obj, 'service_address'):
                service_address = obj.service_address
            # 缓存包源：通过 base_source 访问
            elif hasattr(obj, 'base_source') and obj.base_source:
                if hasattr(obj.base_source, 'service_address'):
                    service_address = obj.base_source.service_address

            if service_address:
                try:
                    validate_s3_service_address(service_address)
                    return None
                except exceptions.ForbiddenExternalPluginSourceError as e:
                    return str(e)

        return None
