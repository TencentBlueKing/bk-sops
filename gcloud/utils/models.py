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
from django.db.models import Func


class Convert(Func):
    def __init__(self, expression, transcoding_name, **extra):
        super(Convert, self).__init__(expression=expression, transcoding_name=transcoding_name, **extra)

    def as_mysql(self, compiler, connection):
        self.function = "CONVERT"
        self.template = "%(function)s(%(expression)s USING %(transcoding_name)s)"
        return super(Convert, self).as_sql(compiler, connection)
