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
from rest_framework.fields import SerializerMethodField


class ReadWriteSerializerMethodField(SerializerMethodField):
    """
    支持可读写的SerializerMethodField
    可实现Model字段和Serializer字段更加灵活地解绑
    通过实现get_xxx_field方法，实现从Model的某个字段读值映射到Serializer对应字段
    通过实现set_xxx_field方法，实现从Serializer字段回填值到Model对应字段
    """

    def __init__(self, method_name=None, write_method_name=None, **kwargs):
        self.method_name = method_name
        self.write_method_name = write_method_name
        kwargs["source"] = "*"
        super(SerializerMethodField, self).__init__(**kwargs)

    def bind(self, field_name, parent):
        default_method_name = f"get_{field_name}"
        default_write_method_name = f"set_{field_name}"

        if self.method_name is None:
            self.method_name = default_method_name
        if self.write_method_name is None:
            self.write_method_name = default_write_method_name
        super(SerializerMethodField, self).bind(field_name, parent)

    def to_representation(self, value):
        method = getattr(self.parent, self.method_name)
        return method(value)

    def to_internal_value(self, data):
        method = getattr(self.parent, self.write_method_name)
        return method(data)
