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

from itertools import chain

import ujson as json

from django.core.exceptions import MultipleObjectsReturned
from django.http.response import HttpResponseForbidden
from django.contrib.auth import get_user_model
from guardian.shortcuts import get_objects_for_user
from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.exceptions import BadRequest, ImmediateHttpResponse, NotFound
from tastypie.resources import Resource

from gcloud.external_plugins.models import (
    source_cls_factory
)


class OriginSourceResource(Resource):
    id = fields.IntegerField(
        attribute='id',
        readonly=True
    )
    name = fields.CharField(attribute='name')
    desc = fields.CharField(attribute='desc')
    type = fields.CharField(attribute='type')
    base_source_id = fields.IntegerField(
        attribute='base_source_id',
        null=True
    )
    details = fields.DictField(
        attribute='details',
        readonly=True
    )
    packages = fields.DictField(attribute='packages')

    class Meta:
        resource_name = 'original_source'
        authorization = Authorization()

    @staticmethod
    def get_source_models(types=None):
        if types:
            source_models = [source_cls_factory[tp] for tp in types if tp in source_cls_factory]
        else:
            source_models = source_cls_factory.values()
        return source_models

    def get_object_list(self, request):
        return list(chain(*[source.objects.all() for source in self.get_source_models()]))

    def apply_filters(self, request, applicable_filters):
        source_models = self.get_source_models(applicable_filters.pop('types', None))
        return list(chain(*[source.objects.filter(**applicable_filters) for source in source_models]))

    def build_filters(self, filters=None, ignore_bad_filters=False):
        if 'types' in filters:
            filters['types'] = json.loads(filters['types'])
        elif 'type' in filters:
            filters['types'] = [filters.pop('type')]
        return filters

    def obj_get_list(self, bundle, **kwargs):
        filters = {}

        if hasattr(bundle.request, 'GET'):
            # Grab a mutable copy.
            filters = bundle.request.GET.copy()

        # Update with the provided kwargs.
        filters.update(kwargs)
        applicable_filters = self.build_filters(filters=filters)

        try:
            objects = self.apply_filters(bundle.request, applicable_filters)
            return self.authorized_read_list(objects, bundle)
        except ValueError:
            raise BadRequest("Invalid resource lookup data provided (mismatched type)")

    def obj_create(self, bundle, **kwargs):
        try:
            source_type = bundle.data.pop('type')
            name = bundle.data.pop('name')
            desc = bundle.data.pop('desc', '')
            packages = json.loads(bundle.data.pop('packages'))
            details = json.loads(bundle.data.pop('details'))
        except (KeyError, ValueError) as e:
            raise BadRequest(e.message)

        if source_type not in source_cls_factory:
            raise BadRequest("Invalid origin type: %s, which should be one of [%s]" % (
                source_type, ','.join(source_cls_factory.keys())))
        # divide details into two parts
        # base_kwargs mains fields in base model(e.g. fields of pipeline.contrib.external_plugins.models.GitRepoSource)
        # original_kwargs mains field in origin model but not in base model(e.g. repo_address、desc)
        source_model = source_cls_factory[source_type]
        base_source_model = source_model.objects.get_base_source_cls(source_type)
        all_fields = [field.name for field in base_source_model._meta.get_fields()]
        original_kwargs = {'desc': desc}
        base_kwargs = {}
        for key, value in details.items():
            if key in all_fields:
                base_kwargs[key] = value
            else:
                original_kwargs[key] = value
        obj = source_model.objects.add_original_source(name, source_type, packages, original_kwargs, **base_kwargs)
        return obj

    def obj_update(self, bundle, **kwargs):
        pass

    def obj_get(self, bundle, **kwargs):
        applicable_filters = self.build_filters(filters=kwargs, ignore_bad_filters=True)
        try:
            object_list = self.apply_filters(bundle.request, applicable_filters)
            stringified_kwargs = ', '.join(["%s=%s" % (k, v) for k, v in applicable_filters.items()])

            if len(object_list) <= 0:
                raise self._meta.object_class.DoesNotExist("Couldn't find an instance of '%s' which matched '%s'" % (
                self._meta.object_class.__name__, stringified_kwargs))
            elif len(object_list) > 1:
                raise MultipleObjectsReturned(
                    "More than '%s' matched '%s'." % (self._meta.object_class.__name__, stringified_kwargs))

            bundle.obj = object_list[0]
            self.authorized_read_detail(object_list, bundle)
            return bundle.obj
        except ValueError:
            raise NotFound("Invalid resource lookup data provided (mismatched type)")

    def obj_delete_list_for_update(self, bundle, **kwargs):
        pass

    def obj_delete_list(self, bundle, **kwargs):
        pass

    def obj_delete(self, bundle, **kwargs):
        pass

    def rollback(self, bundles):
        pass
