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

import logging
from itertools import chain

import ujson as json
import jsonschema
from django.db import transaction
from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.constants import ALL
from tastypie.exceptions import BadRequest, NotFound
from tastypie.resources import (
    Resource,
    convert_post_to_patch
)

from gcloud.webservice3.resources import (
    SuperAuthorization,
    GCloudModelResource,
    AppSerializer,
)
from gcloud.external_plugins import exceptions
from gcloud.external_plugins.models import (
    source_cls_factory,
    CachePackageSource,
    SyncTask,
    RUNNING
)

from gcloud.external_plugins.schemas import ADD_SOURCE_SCHEMA, UPDATE_SOURCE_SCHEMA

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
    imported_plugins = fields.ListField(
        attribute='imported_plugins',
        readonly=True,
        null=True
    )
    packages = fields.DictField(attribute='packages')

    class Meta:
        resource_name = 'package_source'
        authorization = Authorization()
        limit = 0

    @staticmethod
    def get_source_models():
        origin_models = source_cls_factory.values()
        source_models = origin_models + [CachePackageSource]
        return source_models

    @staticmethod
    def get_all_source_objects():
        return list(chain(*[source.objects.all() for source in PackageSourceResource.get_source_models()]))

    def get_object_list(self, request):
        return self.get_all_source_objects()

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
        try:
            origins = bundle.data.pop('origins')
            caches = bundle.data.pop('caches')
        except KeyError:
            raise BadRequest('Invalid params, please check origins and caches')

        with transaction.atomic():
            # collect packages of all origin to cache
            cache_packages = {}
            for origin in origins:
                try:
                    jsonschema.validate(origin, ADD_SOURCE_SCHEMA)
                except jsonschema.ValidationError as e:
                    message = 'Invalid origin source params: %s' % e
                    logger.error(message)
                    raise BadRequest(message)
                cache_packages.update(origin['packages'])

            # create cache first if caches exist
            for cache in caches:
                try:
                    jsonschema.validate(cache, ADD_SOURCE_SCHEMA)
                except jsonschema.ValidationError as e:
                    message = 'Invalid cache source params: %s' % e
                    logger.error(message)
                    raise BadRequest(message)
                try:
                    CachePackageSource.objects.add_cache_source(cache['name'],
                                                                cache['type'],
                                                                cache_packages,
                                                                cache.get('desc', ''),
                                                                **cache['details'])
                except exceptions.GcloudExternalPluginsError as e:
                    message = 'Create cache source raise error: %s' % e
                    logger.error(message)
                    raise BadRequest(message)

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
                source_model.objects.add_original_source(origin['name'],
                                                         source_type,
                                                         origin['packages'],
                                                         original_kwargs,
                                                         **base_kwargs)

    def patch_list(self, request, **kwargs):
        request = convert_post_to_patch(request)
        deserialized = self.deserialize(request,
                                        request.body,
                                        format=request.META.get('CONTENT_TYPE', 'application/json'))
        bundle = self.build_bundle(data=deserialized, request=request)
        return self.obj_update(bundle)

    def obj_update(self, bundle, skip_errors=False, **kwargs):
        try:
            origins = bundle.data.pop('origins')
            caches = bundle.data.pop('caches')
        except KeyError:
            raise BadRequest('Invalid params, please check origins and caches')

        with transaction.atomic():
            # collect packages of all origin to cache
            if caches:
                cache_packages = {}
                for origin_type, origin_model in source_cls_factory.items():
                    origins_from_db = origin_model.objects.all().values('packages')
                    for origin in origins_from_db:
                        cache_packages.update(origin['packages'])

                for origin in origins:
                    try:
                        jsonschema.validate(origin, UPDATE_SOURCE_SCHEMA)
                    except jsonschema.ValidationError as e:
                        message = 'Invalid origin source params: %s' % e
                        logger.error(message)
                        raise BadRequest(message)
                    cache_packages.update(origin['packages'])

                # create or update cache first
                caches_to_update = [cache['id'] for cache in caches if 'id' in cache]
                # delete caches whom id not in param caches
                CachePackageSource.objects.exclude(id__in=caches_to_update).delete()
                for cache in caches:
                    try:
                        jsonschema.validate(cache, UPDATE_SOURCE_SCHEMA)
                    except jsonschema.ValidationError as e:
                        message = 'Invalid cache source params: %s' % e
                        logger.error(message)
                        raise BadRequest(message)
                    if 'id' in cache:
                        try:
                            CachePackageSource.objects.update_base_source(cache['id'],
                                                                          cache['type'],
                                                                          cache_packages,
                                                                          **cache['details'])
                        except CachePackageSource.DoesNotExist:
                            message = 'Invalid cache source id: %s, which cannot be found' % cache['id']
                            logger.error(message)
                            raise BadRequest(message)
                        if cache.get('desc', ''):
                            CachePackageSource.objects.filter(id=cache['id']).update(desc=cache['desc'])
                    else:
                        try:
                            CachePackageSource.objects.add_cache_source(cache['name'],
                                                                        cache['type'],
                                                                        cache_packages,
                                                                        cache.get('desc', ''),
                                                                        **cache['details'])
                        except exceptions.GcloudExternalPluginsError as e:
                            message = 'Create cache source raise error: %s' % e.message
                            logger.error(message)
                            raise BadRequest(message)
            else:
                CachePackageSource.objects.all().delete()

            # delete origins whom id not in param origins
            for origin_type, origin_model in source_cls_factory.items():
                origins_to_update = [origin['id'] for origin in origins
                                     if 'id' in origin and origin['type'] == origin_type]
                origin_model.objects.exclude(id__in=origins_to_update).delete()
            # create origins after
            for origin in origins:
                source_type = origin['type']
                details = origin['details']
                # divide details into two parts，base_kwargs mains fields in base model(e.g. fields of
                # pipeline.contrib.external_plugins.models.GitRepoSource)
                # original_kwargs mains field in origin model but not in base model(e.g. repo_address、desc)
                source_model = source_cls_factory[source_type]
                original_kwargs, base_kwargs = source_model.objects.divide_details_parts(source_type, details)
                if origin.get('desc', ''):
                    original_kwargs['desc'] = origin['desc']
                if 'id' in origin:
                    source_model.objects.update_original_source(origin['id'],
                                                                origin['packages'],
                                                                original_kwargs,
                                                                **base_kwargs)
                else:
                    source_model.objects.add_original_source(origin['name'],
                                                             source_type,
                                                             origin['packages'],
                                                             original_kwargs,
                                                             **base_kwargs)

    def obj_get(self, bundle, **kwargs):
        raise NotFound("Invalid resource uri, please use obj_get_list")

    def obj_delete_list(self, bundle, **kwargs):
        with transaction.atomic():
            caches = CachePackageSource.objects.all()
            # 需要单独调用自定义 delete 方法
            for cache in caches:
                cache.delete()

            for origin_type, origin_model in source_cls_factory.items():
                origins = origin_model.objects.all()
                # 需要单独调用自定义 delete 方法
                for origin in origins:
                    origin.delete()

    def obj_delete_list_for_update(self, bundle, **kwargs):
        pass

    def obj_delete(self, bundle, **kwargs):
        raise NotFound("Invalid resource uri, please use obj_delete_list")

    def rollback(self, bundles):
        pass


class SyncTaskResource(GCloudModelResource):
    id = fields.IntegerField(
        attribute='id',
        readonly=True
    )
    creator_name = fields.CharField(
        attribute='creator_name',
        readonly=True
    )
    status_display = fields.CharField(
        attribute='status_display',
        readonly=True
    )

    class Meta:
        queryset = SyncTask.objects.all()
        resource_name = 'sync_task'
        authorization = SuperAuthorization()
        always_return_data = True
        serializer = AppSerializer()
        filtering = {
            "id": ALL,
            "creator": ALL,
            "create_method": ALL,
            "start_time": ALL,
            "finish_time": ALL,
            "status": ALL,
        }
        q_fields = ["id", "pipeline_template__name"]
        limit = 0

    def obj_create(self, bundle, **kwargs):
        model = bundle.obj.__class__
        if model.objects.filter(status=RUNNING).exists():
            raise BadRequest('There is already a running sync task, please wait for it to complete and try again')
        if not CachePackageSource.objects.all().exists():
            raise BadRequest('No cache package found, please add cache package in Backend Manage')
        if len(PackageSourceResource.get_all_source_objects()) <= 1:
            raise BadRequest('No original packages found, please add original packages in Backend Manage')
        return super(SyncTaskResource, self).obj_create(bundle, **kwargs)
