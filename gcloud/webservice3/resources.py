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

import datetime

from django.utils import timezone
from django.db.models import Q
from django.forms.fields import BooleanField
from django.utils.translation import ugettext_lazy as _
from django.http.response import HttpResponseForbidden, HttpResponse
from guardian.shortcuts import get_objects_for_user
from haystack.query import SearchQuerySet
from tastypie import fields
from tastypie.paginator import Paginator
from tastypie.authorization import ReadOnlyAuthorization
from tastypie.constants import ALL
from tastypie.exceptions import NotFound, ImmediateHttpResponse
from tastypie.resources import ModelResource
from tastypie.serializers import Serializer

from pipeline.component_framework.library import ComponentLibrary
from pipeline.component_framework.models import ComponentModel
from pipeline.core.data.library import VariableLibrary
from pipeline.models import VariableModel

from gcloud import exceptions
from gcloud.core.models import Business
from gcloud.core.api_adapter import is_user_functor, is_user_auditor
from gcloud.core.utils import name_handler, prepare_user_business
from gcloud.core.constant import TEMPLATE_NODE_NAME_MAX_LENGTH


def pipeline_node_name_handle(pipeline_tree):
    for value in pipeline_tree.values():
        if isinstance(value, dict):
            for info in value.values():
                if isinstance(info, dict) and 'name' in info:
                    info['name'] = name_handler(info['name'],
                                                TEMPLATE_NODE_NAME_MAX_LENGTH)
            if 'name' in value:
                value['name'] = name_handler(value['name'],
                                             TEMPLATE_NODE_NAME_MAX_LENGTH)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict) and 'name' in item:
                    item['name'] = name_handler(item['name'],
                                                TEMPLATE_NODE_NAME_MAX_LENGTH)


def get_business_for_user(user, perms):
    return get_objects_for_user(user, perms, Business, any_perm=True)


class AppSerializer(Serializer):

    def format_datetime(self, data):
        # translate to time in local timezone
        if timezone.is_aware(data):
            data = timezone.localtime(data)
        return data.strftime("%Y-%m-%d %H:%M:%S %z")

    def format_date(self, data):
        return data.strftime("%Y-%m-%d")

    def format_time(self, data):
        return datetime.time.strftime(data, "%H:%M:%S")


class GCloudReadOnlyAuthorization(ReadOnlyAuthorization):

    def _get_business_for_user(self, user, perms):
        return get_business_for_user(user, perms)

    def _get_objects_for_user(self, object_list, bundle, perms):
        user = bundle.request.user

        if isinstance(bundle.obj, Business):
            return object_list.filter(
                pk__in=self._get_business_for_user(user, perms)
            )
        elif hasattr(bundle.obj, 'business_id'):
            return object_list.filter(
                business_id__in=self._get_business_for_user(user, perms)
            )
        else:
            raise exceptions.BadResourceClass("Model %s.%s need foreign key 'business'" % (
                bundle.obj.__class__._meta.app_label,
                bundle.obj.__class__.__name__))

    def _generic_read_list(self, object_list, bundle):
        perms = ['view_business', 'manage_business']
        return self._get_objects_for_user(object_list, bundle, perms)

    def _generic_write_list(self, object_list, bundle):
        perms = ['manage_business']
        return self._get_objects_for_user(object_list, bundle, perms)

    def read_list(self, object_list, bundle):
        return self._generic_read_list(object_list, bundle)

    def read_detail(self, object_list, bundle):
        if bundle.obj not in self.read_list(object_list, bundle):
            raise ImmediateHttpResponse(HttpResponseForbidden(
                'you have no permission to read %s' % bundle.obj.__class__.__name__
            ))
        return True


class GCloudGenericAuthorization(GCloudReadOnlyAuthorization):

    def create_list(self, object_list, bundle):
        return []

    def create_detail(self, object_list, bundle):
        if isinstance(bundle.obj, Business):
            business = bundle.obj
        elif hasattr(bundle.obj, 'business'):
            business = getattr(bundle.obj, 'business')
        else:
            raise exceptions.BadResourceClass("Model %s.%s need foreign key 'business'" % (
                bundle.obj.__class__._meta.app_label,
                bundle.obj.__class__.__name__))

        return self._get_business_for_user(
            bundle.request.user,
            perms=['manage_business']
        ).filter(pk=business.pk).exists()

    def update_list(self, object_list, bundle):
        return self._generic_write_list(object_list, bundle)

    def update_detail(self, object_list, bundle):
        if not self.update_list(object_list, bundle).filter(pk=bundle.obj.pk).exists():
            raise ImmediateHttpResponse(HttpResponseForbidden('you have no permission to write flows'))
        return True

    def delete_list(self, object_list, bundle):
        return self._generic_write_list(object_list, bundle)

    def delete_detail(self, object_list, bundle):
        if not self.delete_list(object_list, bundle).filter(pk=bundle.obj.pk).exists():
            raise ImmediateHttpResponse(HttpResponseForbidden('you have no permission to delete flows'))
        return True


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


class GCloudModelResource(ModelResource):
    login_exempt = False

    def determine_format(self, request):
        u"""强制指定返回数据格式为json"""
        return "application/json"

    def build_filters(self, filters=None, ignore_bad_filters=False):
        if filters is None:
            filters = {}

        orm_filters = super(GCloudModelResource, self).build_filters(
            filters,
            ignore_bad_filters
        )

        if filters.get('q', '').strip():
            if getattr(self.Meta, 'q_fields', []):
                queries = [Q(**{'%s__contains' % field: filters['q']})
                           for field in self.Meta.q_fields]
                query = queries.pop()
                for item in queries:
                    query |= item
                orm_filters['q'] = query

            else:
                sqs = SearchQuerySet().models(
                    self._meta.object_class).auto_query(
                    filters['q']).query_facet(self.Meta.q_fields)
                # 创建自定义定过滤条件
                orm_filters['pk__in'] = [i.pk for i in sqs]

        return orm_filters

    def apply_filters(self, request, applicable_filters):
        if 'q' in applicable_filters:
            query = applicable_filters.pop('q')
        else:
            query = None
        queryset = super(GCloudModelResource, self).apply_filters(
            request,
            applicable_filters)
        return queryset.filter(query) if query else queryset

    def wrap_view(self, view):
        view = super(GCloudModelResource, self).wrap_view(view)
        setattr(view, "login_exempt", self.login_exempt)
        return view

    def obj_delete(self, bundle, **kwargs):
        """
        A ORM-specific implementation of ``obj_delete``.

        Takes optional ``kwargs``, which are used to narrow the query to find
        the instance.
        """
        if not hasattr(bundle.obj, 'delete'):
            try:
                bundle.obj = self.obj_get(bundle=bundle, **kwargs)
            except self.Meta.object_class.DoesNotExist:
                raise NotFound(
                    "A model instance matching the "
                    "provided arguments could not be found")

        self.authorized_delete_detail(
            self.get_object_list(
                bundle.request), bundle)
        if "is_deleted" in bundle.obj.__dict__:
            bundle.obj.__dict__.update({"is_deleted": True})
            bundle.obj.save()
        else:
            bundle.obj.delete()


class BusinessResource(GCloudModelResource):
    class Meta:
        queryset = Business.objects.exclude(life_cycle__in=['3', _(u"停运")]) \
                                   .exclude(status='disabled')
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        authorization = GCloudReadOnlyAuthorization()
        resource_name = 'business'
        detail_uri_name = 'cc_id'
        always_return_data = True
        serializer = AppSerializer()
        filtering = {
            "cc_id": ALL,
            "cc_name": ALL,
            "cc_owner": ALL,
            "cc_company": ALL,
        }
        limit = 0

    def get_object_list(self, request):
        if is_user_functor(request) or is_user_auditor(request):
            return super(BusinessResource, self).get_object_list(request)
        all_flag = request.GET.get('all', '0')
        if request.user.is_superuser and str(all_flag) == '1':
            return super(BusinessResource, self).get_object_list(request)
        try:
            # fetch business from CMDB
            biz_list = prepare_user_business(request)
        except exceptions.Unauthorized:
            return HttpResponse(status=401)
        except exceptions.Forbidden:
            # target business does not exist (irregular request)
            return HttpResponseForbidden()
        except exceptions.APIError as e:
            return HttpResponse(status=503, content=e.error)
        cc_id_list = [biz.cc_id for biz in biz_list]
        return super(BusinessResource, self).get_object_list(request).filter(cc_id__in=cc_id_list)


class ComponentModelResource(ModelResource):
    group_icon = fields.CharField(
        attribute='group_icon',
        readonly=True,
        null=True)

    class Meta:
        queryset = ComponentModel.objects.filter(status=1).order_by('name')
        resource_name = 'component'
        excludes = ['status', 'id']
        detail_uri_name = 'code'
        ordering = ['name']
        authorization = ReadOnlyAuthorization()
        limit = 0

    def alter_list_data_to_serialize(self, request, data):
        for bundle in data['objects']:
            component = ComponentLibrary.get_component_class(bundle.data['code'])
            bundle.data['output'] = component.outputs_format()
            bundle.data['form'] = component.form
            bundle.data['desc'] = component.desc
            # 国际化
            name = bundle.data['name'].split('-')
            bundle.data['group_name'] = _(name[0])
            bundle.data['name'] = _(name[1])

        return data

    def alter_detail_data_to_serialize(self, request, data):
        bundle = data
        component = ComponentLibrary.get_component_class(bundle.data['code'])
        bundle.data['output'] = component.outputs_format()
        bundle.data['form'] = component.form
        bundle.data['desc'] = component.desc
        # 国际化
        name = bundle.data['name'].split('-')
        bundle.data['group_name'] = _(name[0])
        bundle.data['name'] = _(name[1])

        return data


class VariableModelResource(ModelResource):
    class Meta:
        queryset = VariableModel.objects.filter(status=1)
        resource_name = 'variable'
        excludes = ['status', 'id']
        detail_uri_name = 'code'
        ordering = ['id']
        authorization = ReadOnlyAuthorization()
        limit = 0

    def alter_list_data_to_serialize(self, request, data):
        for bundle in data['objects']:
            var = VariableLibrary.get_var_class(bundle.data['code'])
            bundle.data['form'] = var.form

        return data

    def alter_detail_data_to_serialize(self, request, data):
        bundle = data
        var = VariableLibrary.get_var_class(bundle.data['code'])
        is_meta = request.GET.get('meta', False)
        form = getattr(var, 'meta_form') if bool(int(is_meta)) else var.form
        bundle.data['form'] = form

        return data
