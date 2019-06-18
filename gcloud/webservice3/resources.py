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

from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from haystack.query import SearchQuerySet
from tastypie import fields

from tastypie.constants import ALL
from tastypie.exceptions import NotFound, ImmediateHttpResponse
from tastypie.resources import ModelResource
from tastypie.exceptions import BadRequest
from tastypie.authorization import ReadOnlyAuthorization
from tastypie.http import HttpForbidden

from auth_backend.plugins.tastypie.authorization import BkSaaSLooseAuthorization
from auth_backend.plugins.tastypie.resources import BkSaaSLabeledDataResourceMixin

from pipeline.component_framework.library import ComponentLibrary
from pipeline.component_framework.models import ComponentModel
from pipeline.variable_framework.models import VariableModel
from gcloud import exceptions
from gcloud.core.models import Business, Project
from gcloud.core.utils import prepare_user_business
from gcloud.core.api_adapter import is_user_functor, is_user_auditor
from gcloud.webservice3.serializers import AppSerializer
from gcloud.core.permissions import project_resource

logger = logging.getLogger('root')


class GCloudModelResource(BkSaaSLabeledDataResourceMixin, ModelResource):
    login_exempt = False

    def wrap_view(self, view):
        view = super(GCloudModelResource, self).wrap_view(view)
        setattr(view, "login_exempt", self.login_exempt)
        return view

    def determine_format(self, request):
        u"""强制指定返回数据格式为json"""
        return "application/json"

    def unauthorized_result(self, exception):
        """
        @summary: return 403 if operation is forbidden, while default of tastypie is 401
        @return:
        """
        raise ImmediateHttpResponse(response=HttpForbidden())

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
        queryset = super(GCloudModelResource, self).apply_filters(request, applicable_filters)
        return queryset.filter(query) if query else queryset

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
        queryset = Business.objects.exclude(status='disabled') \
                                   .exclude(life_cycle__in=[Business.LIFE_CYCLE_CLOSE_DOWN, _(u"停运")])
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        authorization = ReadOnlyAuthorization()
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
        except (exceptions.Unauthorized, exceptions.Forbidden, exceptions.APIError) as e:
            logger.error(u'get business list[username=%s] from CMDB raise error: %s' % (request.user.username, e))
            return super(BusinessResource, self).get_object_list(request)
        cc_id_list = [biz.cc_id for biz in biz_list]
        return super(BusinessResource, self).get_object_list(request).filter(cc_id__in=cc_id_list)


class ProjectResource(GCloudModelResource):
    name = fields.CharField(attribute='name')
    time_zone = fields.CharField(attribute='time_zone')
    creator = fields.CharField(attribute='creator')
    desc = fields.CharField(attribute='desc')
    create_at = fields.DateTimeField(attribute='create_at', readonly=True)
    from_cmdb = fields.BooleanField(attribute='from_cmdb', readonly=True)
    bk_biz_id = fields.IntegerField(attribute='bk_biz_id', readonly=True)
    is_disable = fields.BooleanField(attribute='is_disable')

    ALLOW_UPDATE_FIELD = {'desc', 'is_disable'}

    class Meta:
        queryset = Project.objects.all()
        resource_name = 'project'
        authorization = BkSaaSLooseAuthorization(auth_resource=project_resource,
                                                 read_action_id='view',
                                                 update_action_id='edit')
        always_return_data = True
        serializer = AppSerializer()
        filtering = {
            "name": ALL,
            "is_disable": ALL,
        }

    def obj_create(self, bundle, **kwargs):
        bundle.data['creator'] = bundle.request.user.username
        return super(ProjectResource, self).obj_create(bundle, **kwargs)

    def obj_update(self, bundle, skip_errors=False, **kwargs):
        update_data = {}
        for field in self.ALLOW_UPDATE_FIELD:
            update_data[field] = bundle.data.get(field, getattr(bundle.obj, field))

        bundle.data = update_data

        return super(ProjectResource, self).obj_update(bundle, skip_errors, **kwargs)

    def obj_delete(self, bundle, **kwargs):
        raise BadRequest("can not delete project")


class ComponentModelResource(ModelResource):
    group_icon = fields.CharField(
        attribute='group_icon',
        readonly=True,
        null=True)

    class Meta:
        queryset = ComponentModel.objects.filter(status=True).order_by('name')
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
    name = fields.CharField(
        attribute='name',
        readonly=True,
        null=True)
    form = fields.CharField(
        attribute='form',
        readonly=True,
        null=True)
    type = fields.CharField(
        attribute='type',
        readonly=True,
        null=True)
    tag = fields.CharField(
        attribute='tag',
        readonly=True,
        null=True)
    meta_tag = fields.CharField(
        attribute='meta_tag',
        readonly=True,
        null=True)

    class Meta:
        queryset = VariableModel.objects.filter(status=True)
        resource_name = 'variable'
        excludes = ['status', 'id']
        detail_uri_name = 'code'
        ordering = ['id']
        authorization = ReadOnlyAuthorization()
        limit = 0
