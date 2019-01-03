# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
from django.test import TestCase

from pipeline.component_framework import tag
from pipeline.exceptions import AttributeMissingError, AttributeValidationError


class TagForTest(tag.Tag):
    type = 'start'

    def required_attributes(self):
        return ['a', 'b', 'c']

    def validate_attributes(self):
        if self.attributes['a'] != 'a':
            return False, 'error'
        return True, ''


class TestTag(TestCase):
    def test_required_attributes(self):
        kwargs = {
            'tag_code': 'cc_host_ip',
            'name': 'IP',
            'index': 1,
            'could_be_hooked': True,
            'attributes': {
                'a': 'a',
                'b': 'b'
            }
        }
        self.assertRaises(AttributeMissingError, TagForTest, **kwargs)
        kwargs['attributes']['c'] = 'c'
        TagForTest(**kwargs)

    def test_validate_attributes(self):
        kwargs = {
            'tag_code': 'cc_host_ip',
            'name': 'IP',
            'index': 1,
            'could_be_hooked': True,
            'attributes': {
                'a': 'b',
                'b': 'b',
                'c': 'c'
            }
        }
        self.assertRaises(AttributeValidationError, TagForTest, **kwargs)
        kwargs['attributes']['a'] = 'a'
        TagForTest(**kwargs)
