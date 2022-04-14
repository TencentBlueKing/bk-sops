# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2022 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import logging
import jsonschema
import ujson as json
from itertools import chain
from django.db import transaction

from rest_framework import status

from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.exceptions import NotAcceptable
from rest_framework.generics import UpdateAPIView, ListCreateAPIView, DestroyAPIView

from gcloud.iam_auth import IAMMeta
from gcloud.external_plugins import exceptions
from gcloud.external_plugins.models import source_cls_factory, CachePackageSource
from gcloud.external_plugins.schemas import ADD_SOURCE_SCHEMA, UPDATE_SOURCE_SCHEMA

from gcloud.core.apis.drf.viewsets.base import GcloudCommonMixin
from gcloud.core.apis.drf.permission import IamPermissionInfo, IamPermission, HAS_OBJECT_PERMISSION
from gcloud.core.apis.drf.serilaziers import PackageSourceSerializer

logger = logging.getLogger("root")


class PackageSourcePermission(IamPermission):
    actions = {
        "list": IamPermissionInfo(IAMMeta.ADMIN_VIEW_ACTION),
        "partial_update": IamPermissionInfo(IAMMeta.ADMIN_EDIT_ACTION),
        "create": IamPermissionInfo(IAMMeta.ADMIN_EDIT_ACTION, check_hook=HAS_OBJECT_PERMISSION),
        "destroy": IamPermissionInfo(pass_all=True),
    }


def get_source_models():
    origin_models = list(source_cls_factory.values())
    source_models = origin_models + [CachePackageSource]
    return source_models


def get_all_source_objects():
    return list(chain(*[source.objects.all() for source in get_source_models()]))


class PackageSourceViewSet(GcloudCommonMixin, UpdateAPIView, ListCreateAPIView, DestroyAPIView):
    queryset = get_all_source_objects
    serializer_class = PackageSourceSerializer
    permission_classes = [permissions.IsAuthenticated, PackageSourcePermission]

    def list(self, request, *args, **kwargs):

        filters = dict(request.query_params)
        if "types" in filters:
            filters["types"] = json.loads(filters["types"])
        elif "type" in filters:
            filters["types"] = [filters.pop("type")]

        if filters:
            queryset = list(chain(*[source.objects.filter(**filters) for source in get_all_source_objects()]))
        else:
            queryset = get_all_source_objects()
        page = self.paginate_queryset(queryset)

        serializer = self.get_serializer(page, many=True)

        data = serializer.data
        return self.get_paginated_response(data) if page is not None else Response(data)

    def create(self, request, *args, **kwargs):
        try:
            origins = request.data.pop("origins")
            caches = request.data.pop("caches")
        except KeyError:
            raise NotAcceptable("Invalid params, please check origins and caches")

        with transaction.atomic():
            # collect packages of all origin to cache
            cache_packages = {}
            for origin in origins:
                try:
                    jsonschema.validate(origin, ADD_SOURCE_SCHEMA)
                except jsonschema.ValidationError as e:
                    message = "Invalid origin source params: %s" % e
                    logger.error(message)
                    raise NotAcceptable(message)
                cache_packages.update(origin["packages"])

            # create cache first if caches exist
            for cache in caches:
                try:
                    jsonschema.validate(cache, ADD_SOURCE_SCHEMA)
                except jsonschema.ValidationError as e:
                    message = "Invalid cache source params: %s" % e
                    logger.error(message)
                    raise NotAcceptable(message)
                try:
                    CachePackageSource.objects.add_cache_source(
                        cache["name"], cache["type"], cache_packages, cache.get("desc", ""), **cache["details"]
                    )
                except exceptions.GcloudExternalPluginsError as e:
                    message = "Create cache source raise error: %s" % e
                    logger.error(message)
                    raise NotAcceptable(message)

            # create origins after
            for origin in origins:
                source_type = origin["type"]
                details = origin["details"]
                # divide details into two parts，base_kwargs mains fields in base model(e.g. fields of
                # pipeline.contrib.external_plugins.models.GitRepoSource)
                # original_kwargs mains field in origin model but not in base model(e.g. repo_address、desc)
                source_model = source_cls_factory[source_type]
                original_kwargs, base_kwargs = source_model.objects.divide_details_parts(source_type, details)
                original_kwargs["desc"] = origin.get("desc", "")
                source_model.objects.add_original_source(
                    origin["name"], source_type, origin["packages"], original_kwargs, **base_kwargs
                )
        return Response(status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        raise NotAcceptable("put method is not allowed")

    def partial_update(self, request, *args, **kwargs):
        origins = request.data.pop("origins")
        caches = request.data.pop("caches")
        with transaction.atomic():
            # collect packages of all origin to cache
            if caches:
                cache_packages = {}
                for origin_type, origin_model in list(source_cls_factory.items()):
                    origins_from_db = origin_model.objects.all().values("packages")
                    for origin in origins_from_db:
                        cache_packages.update(origin["packages"])

                for origin in origins:
                    try:
                        jsonschema.validate(origin, UPDATE_SOURCE_SCHEMA)
                    except jsonschema.ValidationError as e:
                        message = "Invalid origin source params: %s" % e
                        logger.error(message)
                        raise NotAcceptable(message)
                    cache_packages.update(origin["packages"])

                # create or update cache first
                caches_to_update = [cache["id"] for cache in caches if "id" in cache]
                # delete caches whom id not in param caches
                CachePackageSource.objects.exclude(id__in=caches_to_update).delete()
                for cache in caches:
                    try:
                        jsonschema.validate(cache, UPDATE_SOURCE_SCHEMA)
                    except jsonschema.ValidationError as e:
                        message = "Invalid cache source params: %s" % e
                        logger.error(message)
                        raise NotAcceptable(message)
                    if "id" in cache:
                        try:
                            CachePackageSource.objects.update_base_source(
                                cache["id"], cache["type"], cache_packages, **cache["details"]
                            )
                        except CachePackageSource.DoesNotExist:
                            message = "Invalid cache source id: %s, which cannot be found" % cache["id"]
                            logger.error(message)
                            raise NotAcceptable(message)
                        if cache.get("desc", ""):
                            CachePackageSource.objects.filter(id=cache["id"]).update(desc=cache["desc"])
                    else:
                        try:
                            CachePackageSource.objects.add_cache_source(
                                cache["name"], cache["type"], cache_packages, cache.get("desc", ""), **cache["details"]
                            )
                        except exceptions.GcloudExternalPluginsError as e:
                            message = "Create cache source raise error: %s" % str(e)
                            logger.error(message)
                            raise NotAcceptable(message)
            else:
                CachePackageSource.objects.all().delete()

            # delete origins whom id not in param origins
            for origin_type, origin_model in list(source_cls_factory.items()):
                origins_to_update = [
                    origin["id"] for origin in origins if "id" in origin and origin["type"] == origin_type
                ]
                origin_model.objects.exclude(id__in=origins_to_update).delete()
            # create origins after
            for origin in origins:
                source_type = origin["type"]
                details = origin["details"]
                # divide details into two parts，base_kwargs mains fields in base model(e.g. fields of
                # pipeline.contrib.external_plugins.models.GitRepoSource)
                # original_kwargs mains field in origin model but not in base model(e.g. repo_address、desc)
                source_model = source_cls_factory[source_type]
                original_kwargs, base_kwargs = source_model.objects.divide_details_parts(source_type, details)
                if origin.get("desc", ""):
                    original_kwargs["desc"] = origin["desc"]
                if "id" in origin:
                    source_model.objects.update_original_source(
                        origin["id"], origin["packages"], original_kwargs, **base_kwargs
                    )
                else:
                    source_model.objects.add_original_source(
                        origin["name"], source_type, origin["packages"], original_kwargs, **base_kwargs
                    )
        return Response(status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, *args, **kwargs):
        with transaction.atomic():
            caches = CachePackageSource.objects.all()
            # 需要单独调用自定义 delete 方法
            for cache in caches:
                cache.delete()

            for origin_type, origin_model in list(source_cls_factory.items()):
                origins = origin_model.objects.all()
                # 需要单独调用自定义 delete 方法
                for origin in origins:
                    origin.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
