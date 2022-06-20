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
from rest_framework.exceptions import ValidationError

from gcloud.user_custom_config.models import UserCustomProjectConfig
from gcloud.user_custom_config.constants import UserConfOption


class UserCustomProjectConfigSerializer(serializers.ModelSerializer):

    # 新增用户自定义项目配置字段时，需保持required=False
    task_template_ordering = serializers.CharField(help_text="模板默认排序字段", required=False)

    class Meta:
        model = UserCustomProjectConfig
        fields = "__all__"


class UserCustomProjectConfigOptionsSerializer(serializers.Serializer):

    # field_a,field_b
    configs = serializers.CharField(help_text="要获取的用户自定义配置项,多个以逗号分割", default="")
    project_id = serializers.CharField(help_text="项目ID", required=True)

    def is_valid(self, raise_exception=False):
        super().is_valid(raise_exception)
        configs = self.data["configs"].split(",")
        for key in configs:
            if key not in UserConfOption.keys():
                _errors_detail = {key: f"该配置项不存在:{key}"}
                if not raise_exception:
                    return False
                raise ValidationError(detail=_errors_detail)
        self.validated_data["configs"] = configs
        return True
