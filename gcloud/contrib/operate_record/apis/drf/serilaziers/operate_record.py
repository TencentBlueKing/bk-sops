# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import json

from rest_framework import serializers

from gcloud.core.apis.drf.validators import ProjectExistValidator
from gcloud.contrib.operate_record.constants import OperateType, OperateSource


class OperateRecordSetSerializer(serializers.Serializer):
    project_id = serializers.IntegerField(required=False, validators=[ProjectExistValidator()])
    instance_id = serializers.IntegerField()
    operator = serializers.CharField(required=False)
    operate_type = serializers.CharField(required=False)
    operate_date = serializers.DateTimeField(required=False)
    operate_source = serializers.CharField(required=False)

    def to_representation(self, instance):
        data = super(OperateRecordSetSerializer, self).to_representation(instance)
        operate_type = instance.operate_type
        operate_source = instance.operate_source
        data["operate_type_name"] = OperateType[operate_type].value if operate_type else None
        data["operate_source_name"] = OperateSource[operate_source].value
        return data


class TemplateOperateRecordSetSerializer(OperateRecordSetSerializer):
    ...


class TaskOperateRecordSetSerializer(OperateRecordSetSerializer):
    node_id = serializers.CharField(required=False)
    extra_info = serializers.SerializerMethodField()

    def get_extra_info(self, obj):
        return json.loads(obj.extra_info) if obj.extra_info else {}
