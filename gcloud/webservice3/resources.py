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

from django import forms
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from haystack.query import SearchQuerySet
from tastypie import fields
from tastypie.authorization import ReadOnlyAuthorization
from tastypie.constants import ALL
from tastypie.exceptions import BadRequest, ImmediateHttpResponse, NotFound
from tastypie.http import HttpForbidden
from tastypie.resources import ModelResource
from tastypie.validation import FormValidation

from auth_backend.plugins.constants import PRINCIPAL_TYPE_USER
from auth_backend.plugins.tastypie.authorization import BkSaaSLooseAuthorization, BkSaaSReadOnlyAuthorization
from auth_backend.plugins.tastypie.resources import BkSaaSLabeledDataResourceMixin
from pipeline.component_framework.constants import LEGACY_PLUGINS_VERSION
from pipeline.component_framework.library import ComponentLibrary
from pipeline.component_framework.models import ComponentModel
from pipeline.variable_framework.models import VariableModel

from gcloud.core.models import Business, Project, ProjectCounter
from gcloud.core.permissions import project_resource
from gcloud.webservice3.serializers import AppSerializer

logger = logging.getLogger('root')


class GCloudModelResource(BkSaaSLabeledDataResourceMixin, ModelResource):
    login_exempt = False

    def wrap_view(self, view):
        view = super(GCloudModelResource, self).wrap_view(view)
        setattr(view, "login_exempt", self.login_exempt)
        return view

    def determine_format(self, request):
        """
        @summary: 强制指定返回数据格式为json
        """
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

    class Meta:
        serializer = AppSerializer()
        always_return_data = True
        # 控制 Resource 一次显示多少个结果。默认值为 API_LIMIT_PER_PAGE 设置（如果设置）或20（如果未设置）
        limit = 0
        # 控制 Resource 一次显示的最大结果数。如果用户指定的 limit 高于 max_limit，它将被限制为 max_limit
        max_limit = 0


class BusinessResource(GCloudModelResource):
    class Meta(GCloudModelResource.Meta):
        queryset = Business.objects.exclude(status='disabled') \
            .exclude(life_cycle__in=[Business.LIFE_CYCLE_CLOSE_DOWN, _("停运")])
        authorization = ReadOnlyAuthorization()
        resource_name = 'business'
        detail_uri_name = 'cc_id'
        filtering = {
            "cc_id": ALL,
            "cc_name": ALL,
            "cc_owner": ALL,
            "cc_company": ALL,
        }


class ProjectForm(forms.Form):
    name = forms.CharField(max_length=256)
    desc = forms.CharField(max_length=512, required=False)


class ProjectResource(GCloudModelResource):
    create_at = fields.DateTimeField(attribute='create_at', readonly=True)
    from_cmdb = fields.BooleanField(attribute='from_cmdb', readonly=True)
    bk_biz_id = fields.IntegerField(attribute='bk_biz_id', readonly=True)

    ALLOW_UPDATE_FIELD = ['desc', 'is_disable']

    class Meta(GCloudModelResource.Meta):
        queryset = Project.objects.all().order_by('-id')
        validation = FormValidation(form_class=ProjectForm)
        resource_name = 'project'
        auth_resource = project_resource
        authorization = BkSaaSLooseAuthorization(auth_resource=auth_resource,
                                                 read_action_id='view',
                                                 update_action_id='edit')
        filtering = {
            "id": ALL,
            "name": ALL,
            "creator": ALL,
            "from_cmdb": ALL,
            "bk_biz_id": ALL,
            "is_disable": ALL,
        }
        q_fields = ['id', 'name', 'desc', 'creator']

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


class ComponentModelResource(GCloudModelResource):
    group_icon = fields.CharField(
        attribute='group_icon',
        readonly=True,
        null=True)

    class Meta(GCloudModelResource.Meta):
        queryset = ComponentModel.objects.filter(status=True).order_by('name')
        resource_name = 'component'
        excludes = ['status', 'id']
        detail_uri_name = 'code'
        authorization = ReadOnlyAuthorization()

    def build_filters(self, filters=None, ignore_bad_filters=False):
        orm_filters = super(ComponentModelResource, self).build_filters(filters=filters,
                                                                        ignore_bad_filters=ignore_bad_filters)
        if filters and 'version' in filters:
            orm_filters['version'] = filters.get('version') or LEGACY_PLUGINS_VERSION

        return orm_filters

    def get_detail(self, request, **kwargs):
        kwargs['version'] = request.GET.get('version', None)
        return super(ComponentModelResource, self).get_detail(request, **kwargs)

    def alter_list_data_to_serialize(self, request, data):
        for bundle in data['objects']:
            component = ComponentLibrary.get_component_class(bundle.data['code'], bundle.data['version'])
            bundle.data['output'] = component.outputs_format()
            bundle.data['form'] = component.form
            bundle.data['desc'] = component.desc
            bundle.data['form_is_embedded'] = component.form_is_embedded()
            # 国际化
            name = bundle.data['name'].split('-')
            bundle.data['group_name'] = _(name[0])
            bundle.data['name'] = _(name[1])

        return data

    def alter_detail_data_to_serialize(self, request, data):
        data = super(ComponentModelResource, self).alter_detail_data_to_serialize(request, data)
        bundle = data
        component = ComponentLibrary.get_component_class(bundle.data['code'], bundle.data['version'])
        bundle.data['output'] = component.outputs_format()
        bundle.data['form'] = component.form
        bundle.data['desc'] = component.desc
        bundle.data['form_is_embedded'] = component.form_is_embedded()
        # 国际化
        name = bundle.data['name'].split('-')
        bundle.data['group_name'] = _(name[0])
        bundle.data['name'] = _(name[1])

        return data


class VariableModelResource(GCloudModelResource):
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

    class Meta(GCloudModelResource.Meta):
        queryset = VariableModel.objects.filter(status=True)
        resource_name = 'variable'
        excludes = ['status', 'id']
        detail_uri_name = 'code'
        authorization = ReadOnlyAuthorization()


class CommonProjectResource(GCloudModelResource):
    project = fields.ForeignKey(
        ProjectResource,
        'project',
        full=True
    )

    class Meta(GCloudModelResource.Meta):
        queryset = ProjectCounter.objects.all().order_by('-count')
        resource_name = 'common_use_project'
        auth_resource = project_resource
        authorization = BkSaaSReadOnlyAuthorization(auth_resource=auth_resource,
                                                    read_action_id='view',
                                                    resource_f='project')
        allowed_methods = ['get']
        filtering = {
            "id": ALL,
            "username": ALL,
            "count": ALL,
        }
        q_fields = ['id', 'username', 'count']

    @staticmethod
    def get_default_projects(empty_query, username):
        """初始化并返回用户有权限的项目"""

        authorized_projects = project_resource.backend.search_authorized_resources(
            resource=project_resource,
            principal_type=PRINCIPAL_TYPE_USER,
            principal_id=username,
            action_ids=[project_resource.actions.view.id],
        )

        if not authorized_projects['result']:
            logger.error("Get authorized projects error: {error}".format(
                error=authorized_projects['message']
            ))
            project_ids = []
        else:
            project_ids = [
                int(ap[0]['resource_id'])
                for ap in authorized_projects['data'][0]['resource_ids']
            ]

        if not len(project_ids):
            return empty_query

        # 过滤脏数据
        project_ids = list(Project.objects.filter(id__in=project_ids).values_list('id', flat=True))

        # 初始化用户有权限的项目
        ProjectCounter.objects.bulk_create([
            ProjectCounter(username=username, project_id=project_id)
            for project_id in project_ids
        ])

        return ProjectCounter.objects.filter(username=username, project_id__in=project_ids, project__is_disable=False)

    def get_object_list(self, request):

        query = super(GCloudModelResource, self).get_object_list(request)
        query = query.filter(username=request.user.username, project__is_disable=False)

        # 第一次访问或无被授权的项目
        if not query.exists():
            query = self.get_default_projects(query, request.user.username)

        return query
