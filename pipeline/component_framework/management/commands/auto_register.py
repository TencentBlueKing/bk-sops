# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from django.core.management import BaseCommand

from pipeline.component_framework.library import ComponentLibrary
from pipeline.component_framework.component import Component
from pipeline.component_framework.models import ComponentModel


class Command(BaseCommand):
    def handle(self, *args, **options):

        for component_code, component_cls in ComponentLibrary.components.iteritems():

            if isinstance(component_cls, type) and issubclass(component_cls, Component):

                # not register ignored component
                ignore = getattr(component_cls, '__register_ignore__', False)
                if ignore:
                    continue

                ComponentModel.objects.get_or_create(
                    code=component_cls.code,
                    defaults={
                        'name': component_cls.name,
                        'status': __debug__,
                    }
                )
