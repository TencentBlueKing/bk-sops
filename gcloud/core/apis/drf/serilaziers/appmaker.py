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

import env
from gcloud.conf import settings
from gcloud.contrib.appmaker.models import AppMaker
from gcloud.core.apis.drf.serilaziers import ProjectSerializer


class AppmakerSerializer(serializers.ModelSerializer):
    project = ProjectSerializer()
    creator_name = serializers.CharField(help_text="创建者名", read_only=True)
    editor_name = serializers.CharField(help_text="编辑者名", read_only=True)
    desktop_url = serializers.SerializerMethodField(help_text="桌面url", read_only=True)
    link = serializers.SerializerMethodField(help_text="轻应用跳转 url", read_only=True)
    template_name = serializers.CharField(source="task_template_name", read_only=True)
    template_id = serializers.IntegerField(source="task_template.id", read_only=True)
    edit_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S %z", read_only=True)

    def get_desktop_url(self, obj):
        return "{}?app={}".format(env.BK_PAAS_DESKTOP_HOST, obj.code)

    def get_link(self, obj):
        request = self.context.get("request")
        if settings.IS_LOCAL and request is not None:
            link_prefix = request.build_absolute_uri("/appmaker/")
        else:
            link_prefix = f"{settings.APP_HOST.rstrip('/')}/appmaker/"
        return AppMaker.objects.build_app_link(link_prefix, obj.id, obj.project_id, obj.task_template_id)

    class Meta:
        model = AppMaker
        fields = "__all__"
