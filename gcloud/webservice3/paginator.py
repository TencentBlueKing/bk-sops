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

from django.forms.fields import BooleanField
from tastypie.paginator import Paginator


class PropertyFilterPaginator(Paginator):

    def properties(self):
        raise NotImplementedError()

    def filter_objects(self, filter_items):
        if not filter_items:
            return

        filtered = []

        for obj in self.objects:

            for item in filter_items:
                if getattr(obj, item['p']) != item['v']:
                    break
            else:
                filtered.append(obj)

        setattr(self, '_objects', self.objects)
        self.objects = filtered

    def page(self):
        """
        Generates all pertinent data about the requested page.

        Handles getting the correct ``limit`` & ``offset``, then slices off
        the correct set of results and returns all pertinent metadata.
        """
        limit = self.get_limit()
        offset = self.get_offset()

        # do property filter work before page
        filter_items = []
        for prop, field in self.properties().items():
            if prop in self.request_data:
                filter_items.append({'p': prop,
                                     'v': field.to_python(self.request_data[prop])})

        self.filter_objects(filter_items)

        # count after filter
        count = self.get_count()

        objects = self.get_slice(limit, offset)
        meta = {
            'offset': offset,
            'limit': limit,
            'total_count': count,
        }

        if limit:
            meta['previous'] = self.get_previous(limit, offset)
            meta['next'] = self.get_next(limit, offset, count)

        return {
            self.collection_name: objects,
            'meta': meta,
        }


class TemplateFilterPaginator(PropertyFilterPaginator):
    def properties(self):
        return {'subprocess_has_update': BooleanField(),
                'has_subprocess': BooleanField()}
