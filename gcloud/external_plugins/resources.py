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

import logging
from itertools import chain

import ujson as json
import jsonschema
from django.db import transaction
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.http.response import HttpResponseForbidden
from django.contrib.auth import get_user_model
from guardian.shortcuts import get_objects_for_user
from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.exceptions import BadRequest, ImmediateHttpResponse, NotFound
from tastypie.resources import Resource

from gcloud.external_plugins.models import (
    source_cls_factory,
    CachePackageSource
)
from gcloud.external_plugins.schemas import SOURCE_SCHEMA

logger = logging.getLogger('root')


class PackageSourceResource(Resource):
    id = fields.IntegerField(
        attribute='id',
        readonly=True
    )
    name = fields.CharField(attribute='name')
    desc = fields.CharField(attribute='desc')
    category = fields.CharField(attribute='category')
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
        resource_name = 'package_source'
        authorization = Authorization()

    @staticmethod
    def get_source_models():
        origin_models = source_cls_factory.values()
        source_models = origin_models + [CachePackageSource]
        return source_models

    def get_object_list(self, request):
        return list(chain(*[source.objects.all() for source in self.get_source_models()]))

    def apply_filters(self, request, applicable_filters):
        source_models = self.get_source_models()
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
            raise BadRequest('Invalid resource lookup params provided')

    def obj_create(self, bundle, **kwargs):
        with transaction.atomic():
            try:
                origins = json.loads(bundle.data.pop('origin'))
                caches = json.loads(bundle.data.pop('caches'))
            except (KeyError, ValueError) as e:
                raise BadRequest(e.message)

            sources = []
            # collect packages of all origin to cache
            cache_packages = {}
            for origin in origins:
                try:
                    jsonschema.validate(origin, SOURCE_SCHEMA)
                except jsonschema.ValidationError as e:
                    message = 'Invalid origin source params: %s' % e
                    logger.error(message)
                    raise BadRequest(message)
                cache_packages.update(origin['packages'])

            # create cache first if caches exist
            for cache in caches:
                try:
                    jsonschema.validate(cache, SOURCE_SCHEMA)
                except jsonschema.ValidationError as e:
                    message = 'Invalid origin source params: %s' % e
                    logger.error(message)
                    raise BadRequest(message)
                obj = CachePackageSource.objects.add_cache_source(cache['name'],
                                                                  cache['type'],
                                                                  cache_packages,
                                                                  **caches['details'])
                sources.append(obj)

            # create origins after
            for origin in origins:
                source_type = origin['type']
                details = origin['details']
                # divide details into two parts，base_kwargs mains fields in base model(e.g. fields of
                # pipeline.contrib.external_plugins.models.GitRepoSource)
                # original_kwargs mains field in origin model but not in base model(e.g. repo_address、desc)
                source_model = source_cls_factory[source_type]
                original_kwargs, base_kwargs = source_model.objects.divide_details_parts(source_type, details)
                original_kwargs['desc'] = origin.get('desc', '')
                obj = source_model.objects.add_original_source(origin['name'],
                                                               source_type,
                                                               origin['packages'],
                                                               original_kwargs,
                                                               **base_kwargs)
                sources.append(obj)
            return sources

    def obj_update(self, bundle, skip_errors=False, **kwargs):
        pass

    def obj_get(self, bundle, **kwargs):
        raise NotFound("Invalid resource uri, please use obj_get_list")

    def obj_delete_list_for_update(self, bundle, **kwargs):
        pass

    def obj_delete_list(self, bundle, **kwargs):
        pass

    def obj_delete(self, bundle, **kwargs):
        pass

    def rollback(self, bundles):
        pass
