# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
import datetime
import ujson as json

from django.utils import timezone
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.http.response import HttpResponseForbidden, HttpResponse
from django.contrib.auth import get_user_model
from guardian.shortcuts import get_objects_for_user
from haystack.query import SearchQuerySet
from tastypie import fields
from tastypie.authorization import Authorization, ReadOnlyAuthorization
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.exceptions import BadRequest, NotFound, ImmediateHttpResponse
from tastypie.resources import ModelResource
from tastypie.serializers import Serializer

from bk_api import is_user_functor

from gcloud import exceptions
from gcloud.core.models import Business
from gcloud.core.utils import name_handler, prepare_user_business
from gcloud.tasktmpl3.models import (TaskTemplate,
                                     CREATE_TASK_PERM_NAME)
from gcloud.taskflow3.models import TaskFlowInstance
from pipeline.component_framework.library import ComponentLibrary
from pipeline.component_framework.models import ComponentModel
from pipeline.core.data.library import VariableLibrary
from pipeline.exceptions import PipelineException
from pipeline.models import TemplateScheme, PipelineTemplate, PipelineInstance, VariableModel
from pipeline.validators.base import validate_web_pipeline_tree

TEMPLATE_NODE_NAME_MAX_LENGTH = 30
TASK_NAME_MAX_LENGTH = 50


def pipeline_node_name_handle(pipeline_tree):
    for _, value in pipeline_tree.items():
        if isinstance(value, dict):
            for _, info in value.items():
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
    _perms = []
    for perm in perms:
        _perms.append('.'.join([Business._meta.app_label, perm]))
    return get_objects_for_user(user, _perms, any_perm=True)


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
            raise exceptions.BadResourceClass("Model %s.%s need foreign key 'business'." % (
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
        return bundle.obj in self.read_list(object_list, bundle)


class GCloudGenericAuthorization(GCloudReadOnlyAuthorization):

    def create_list(self, object_list, bundle):
        return []

    def create_detail(self, object_list, bundle):
        if isinstance(bundle.obj, Business):
            business = bundle.obj
        elif hasattr(bundle.obj, 'business'):
            business = getattr(bundle.obj, 'business')
        else:
            raise exceptions.BadResourceClass("Model %s.%s need foreign key 'business'." % (
                bundle.obj.__class__._meta.app_label,
                bundle.obj.__class__.__name__))

        return self._get_business_for_user(
            bundle.request.user,
            perms=['manage_business']
        ).filter(pk=business.pk).exists()

    def update_list(self, object_list, bundle):
        return self._generic_write_list(object_list, bundle)

    def update_detail(self, object_list, bundle):
        return self.update_list(object_list, bundle).filter(pk=bundle.obj.pk).exists()

    def delete_list(self, object_list, bundle):
        return self._generic_write_list(object_list, bundle)

    def delete_detail(self, object_list, bundle):
        return self.delete_list(object_list, bundle).filter(pk=bundle.obj.pk).exists()


class TaskflowAuthorization(GCloudGenericAuthorization):
    def create_detail(self, object_list, bundle):
        if isinstance(bundle.obj, Business):
            business = bundle.obj
        elif hasattr(bundle.obj, 'business'):
            business = getattr(bundle.obj, 'business')
        else:
            raise exceptions.BadResourceClass("Model %s.%s need foreign key 'business'." % (
                bundle.obj.__class__._meta.app_label,
                bundle.obj.__class__.__name__))

        return self._get_business_for_user(
            bundle.request.user,
            perms=['view_business']
        ).filter(pk=business.pk).exists()


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
            except bundle.obj.DoesNotExist:
                raise NotFound(
                    "A model instance matching the "
                    "provided arguments could not be found.")

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
        queryset = Business.objects.all()
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
        # fetch business from CMDB
        try:
            biz_list = prepare_user_business(request)
        except exceptions.Unauthorized:
            return HttpResponse(status=401)
        except exceptions.Forbidden:
            # target business does not exist (irregular request)
            return HttpResponseForbidden()
        except exceptions.APIError as e:
            return HttpResponse(status=503, content=e.error)
        # TODO: 职能化获取的业务列表如何去掉配置平台已删除的业务
        if is_user_functor(request):
            return super(BusinessResource, self).get_object_list(request).exclude(life_cycle__in=['3', _(u"停运")])
        else:
            cc_id_list = [biz.cc_id for biz in biz_list]
            return super(BusinessResource, self).get_object_list(request).filter(cc_id__in=cc_id_list)


class PipelineTemplateResource(ModelResource):
    class Meta:
        queryset = PipelineTemplate.objects.filter(is_deleted=False)
        resource_name = 'pipeline_template'
        authorization = ReadOnlyAuthorization()
        serializer = AppSerializer()
        filtering = {
            'name': ALL,
        }
        limit = 0


class TaskTemplateResource(GCloudModelResource):
    business = fields.ForeignKey(
        BusinessResource,
        'business',
        full=True)
    pipeline_template = fields.ForeignKey(
        PipelineTemplateResource,
        'pipeline_template')
    name = fields.CharField(
        attribute='name',
        readonly=True,
        null=True)
    category_name = fields.CharField(
        attribute='category_name',
        readonly=True,
        null=True)
    creator_name = fields.CharField(
        attribute='creator_name',
        readonly=True,
        null=True)
    editor_name = fields.CharField(
        attribute='editor_name',
        readonly=True,
        null=True)
    create_time = fields.DateTimeField(
        attribute='create_time',
        readonly=True,
        null=True)
    edit_time = fields.DateTimeField(
        attribute='edit_time',
        readonly=True,
        null=True)
    pipeline_tree = fields.DictField(
        attribute='pipeline_tree',
        use_in='detail',
        readonly=True,
        null=True)
    template_id = fields.IntegerField(
        attribute='template_id',
        readonly=True)
    subprocess_info = fields.DictField(
        attribute='subprocess_info',
        use_in='detail',
        readonly=True
    )
    version = fields.CharField(
        attribute='version',
        readonly=True,
        null=True
    )
    subprocess_has_update = fields.BooleanField(
        attribute='subprocess_has_update',
        use_in='list',
        readonly=True
    )

    class Meta:
        queryset = TaskTemplate.objects.filter(pipeline_template__isnull=False, is_deleted=False)
        resource_name = 'template'
        authorization = GCloudGenericAuthorization()
        always_return_data = True
        serializer = AppSerializer()
        filtering = {
            "id": ALL,
            "business": ALL_WITH_RELATIONS,
            "name": ALL,
            "category": ALL,
            "pipeline_template": ALL_WITH_RELATIONS,
        }
        q_fields = ["id", "pipeline_template__name"]
        limit = 0

    @staticmethod
    def handle_template_name_attr(data):
        data['name'] = name_handler(data['name'],
                                    TEMPLATE_NODE_NAME_MAX_LENGTH)
        pipeline_node_name_handle(data['pipeline_tree'])

    def dehydrate_pipeline_tree(self, bundle):
        return json.dumps(bundle.data['pipeline_tree'])

    def get_object_list(self, request):
        if is_user_functor(request):
            # 职能化用户只返回有创建任务权限的模板
            templates = super(TaskTemplateResource, self).get_object_list(request)
            return get_objects_for_user(request.user, CREATE_TASK_PERM_NAME, templates)
        else:
            return super(TaskTemplateResource, self).get_object_list(request)

    def alter_list_data_to_serialize(self, request, data):
        user_model = get_user_model()
        user = request.user
        collected_templates = user_model.objects.get(username=user.username) \
            .tasktemplate_set.all() \
            .values_list('id', flat=True)
        for bundle in data['objects']:
            if bundle.obj.id in collected_templates:
                bundle.data['is_add'] = 1
            else:
                bundle.data['is_add'] = 0

        return data

    def obj_create(self, bundle, **kwargs):
        model = bundle.obj.__class__
        try:
            pipeline_template_kwargs = {
                'name': bundle.data.pop('name'),
                'creator': bundle.request.user.username,
                'pipeline_tree': json.loads(bundle.data.pop('pipeline_tree')),
                'description': bundle.data.pop('description', ''),
            }
        except (KeyError, ValueError) as e:
            raise BadRequest(e.message)
        # XSS handle
        self.handle_template_name_attr(pipeline_template_kwargs)
        # validate pipeline tree
        try:
            validate_web_pipeline_tree(pipeline_template_kwargs['pipeline_tree'])
        except PipelineException as e:
            raise BadRequest(e.message)
        # Note: tastypie won't use model's create method
        try:
            pipeline_template = model.objects.__class__.create_pipeline_template(
                **pipeline_template_kwargs)
        except PipelineException as e:
            raise BadRequest(e.message)
        except TaskTemplate.DoesNotExist:
            raise BadRequest('Template referred by SubProcess does not exist')
        kwargs['pipeline_template_id'] = pipeline_template.template_id
        return super(TaskTemplateResource, self).obj_create(bundle, **kwargs)

    def obj_update(self, bundle, skip_errors=False, **kwargs):
        obj = bundle.obj
        try:
            pipeline_template_kwargs = {
                'name': bundle.data.pop('name'),
                'editor': bundle.request.user.username,
                'pipeline_tree': json.loads(bundle.data.pop('pipeline_tree')),
            }
            if 'description' in bundle.data:
                pipeline_template_kwargs['description'] = bundle.data.pop('description')
        except (KeyError, ValueError) as e:
            raise BadRequest(e.message)
        # XSS handle
        self.handle_template_name_attr(pipeline_template_kwargs)
        try:
            obj.update_pipeline_template(**pipeline_template_kwargs)
        except PipelineException as e:
            raise BadRequest(e.message)
        bundle.data['pipeline_template'] = '/api/v3/pipeline_template/%s/' % obj.pipeline_template.pk
        return super(TaskTemplateResource, self).obj_update(bundle, **kwargs)


class TemplateSchemeResource(ModelResource):
    class Meta:
        queryset = TemplateScheme.objects.all()
        resource_name = 'schemes'
        authorization = Authorization()
        always_return_data = True
        serializer = AppSerializer()

        filtering = {
            'template': ALL,
        }
        limit = 0

    def build_filters(self, filters=None, **kwargs):
        orm_filters = super(TemplateSchemeResource, self).build_filters(filters, **kwargs)
        try:
            template_id = filters.pop('template__template_id')[0]
            biz_cc_id = filters.pop('biz_cc_id')[0]
            template = TaskTemplate.objects.get(pk=template_id, business__cc_id=biz_cc_id)
            orm_filters.update({'template__template_id': template.pipeline_template.template_id})
        except:
            pass
        return orm_filters

    def alter_list_data_to_serialize(self, request, data):
        for bundle in data['objects']:
            bundle.data.pop('data')

        return data

    def obj_create(self, bundle, **kwargs):
        try:
            template_id = bundle.data.pop('template_id', '')
            biz_cc_id = bundle.data.pop('biz_cc_id')
            template = TaskTemplate.objects.get(pk=template_id, business__cc_id=biz_cc_id)
        except Exception:
            raise BadRequest('template[id=%s] in business[%s] does not exist' % (template_id, biz_cc_id))
        business = get_business_for_user(bundle.request.user, ['view_business'])
        if not business.filter(cc_id=biz_cc_id).exists():
            raise ImmediateHttpResponse(HttpResponseForbidden('you have no permissions to make such operation'))
        bundle.data['name'] = name_handler(bundle.data['name'], TEMPLATE_NODE_NAME_MAX_LENGTH)
        kwargs['unique_id'] = '%s-%s' % (template_id, bundle.data['name'])
        if TemplateScheme.objects.filter(unique_id=kwargs['unique_id']).exists():
            raise BadRequest('template scheme name has existed, please change the name')
        kwargs['template'] = template.pipeline_template
        return super(TemplateSchemeResource, self).obj_create(bundle, **kwargs)

    def obj_delete(self, bundle, **kwargs):
        try:
            scheme_id = kwargs['pk']
            scheme = TemplateScheme.objects.get(pk=scheme_id)
            template = TaskTemplate.objects.get(pipeline_template=scheme.template)
        except Exception:
            raise BadRequest('scheme or template does not exist')
        business = get_business_for_user(bundle.request.user, ['manage_business'])
        if not business.filter(cc_id=template.business.cc_id).exists():
            raise ImmediateHttpResponse(HttpResponseForbidden('you have no permissions to make such operation'))
        return super(TemplateSchemeResource, self).obj_delete(bundle, **kwargs)


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
        bundle.data['form'] = var.form

        return data


class PipelineInstanceResource(ModelResource):
    class Meta:
        queryset = PipelineInstance.objects.filter(is_deleted=False)
        resource_name = 'pipeline_instance'
        authorization = ReadOnlyAuthorization()
        serializer = AppSerializer()
        filtering = {
            'name': ALL,
            'is_finished': ALL,
        }
        limit = 0


class TaskFlowInstanceResource(GCloudModelResource):
    business = fields.ForeignKey(
        BusinessResource,
        'business',
        full=True)
    pipeline_instance = fields.ForeignKey(
        PipelineInstanceResource,
        'pipeline_instance')
    name = fields.CharField(
        attribute='name',
        readonly=True,
        null=True)
    instance_id = fields.IntegerField(
        attribute='instance_id',
        readonly=True)
    category_name = fields.CharField(
        attribute='category_name',
        readonly=True)
    create_time = fields.DateTimeField(
        attribute='create_time',
        readonly=True,
        null=True)
    start_time = fields.DateTimeField(
        attribute='start_time',
        readonly=True,
        null=True)
    finish_time = fields.DateTimeField(
        attribute='finish_time',
        readonly=True,
        null=True)
    elapsed_time = fields.IntegerField(
        attribute='elapsed_time',
        readonly=True)
    is_started = fields.BooleanField(
        attribute='is_started',
        readonly=True,
        null=True)
    is_finished = fields.BooleanField(
        attribute='is_finished',
        readonly=True,
        null=True)
    creator_name = fields.CharField(
        attribute='creator_name',
        readonly=True,
        null=True)
    executor_name = fields.CharField(
        attribute='executor_name',
        readonly=True,
        null=True)
    pipeline_tree = fields.DictField(
        attribute='pipeline_tree',
        use_in='detail',
        readonly=True,
        null=True)
    subprocess_info = fields.DictField(
        attribute='subprocess_info',
        use_in='detail',
        readonly=True
    )

    class Meta:
        queryset = TaskFlowInstance.objects.filter(pipeline_instance__isnull=False, is_deleted=False)
        resource_name = 'taskflow'
        authorization = TaskflowAuthorization()
        always_return_data = True
        serializer = AppSerializer()
        filtering = {
            "id": ALL,
            "business": ALL_WITH_RELATIONS,
            "name": ALL,
            "category": ALL,
            "create_method": ALL,
            "create_info": ALL,
            "template_id": ALL,
            "pipeline_instance": ALL_WITH_RELATIONS,
        }
        q_fields = ["id", "pipeline_instance__name"]
        limit = 0

    @staticmethod
    def handle_task_name_attr(data):
        data['name'] = name_handler(data['name'],
                                    TASK_NAME_MAX_LENGTH)
        pipeline_node_name_handle(data['pipeline_tree'])

    def dehydrate_pipeline_tree(self, bundle):
        return json.dumps(bundle.data['pipeline_tree'])

    def obj_create(self, bundle, **kwargs):
        model = bundle.obj.__class__
        try:
            template_id = bundle.data['template_id']
            creator = bundle.request.user.username
            pipeline_instance_kwargs = {
                'name': bundle.data.pop('name'),
                'creator': creator,
                'pipeline_tree': json.loads(bundle.data.pop('pipeline_tree')),
            }
            if 'description' in bundle.data:
                pipeline_instance_kwargs['description'] = bundle.data.pop('description')
        except (KeyError, ValueError) as e:
            raise BadRequest(e.message)
        # XSS handle
        self.handle_task_name_attr(pipeline_instance_kwargs)
        # validate pipeline tree
        try:
            validate_web_pipeline_tree(pipeline_instance_kwargs['pipeline_tree'])
        except PipelineException as e:
            raise BadRequest(e.message)
        try:
            template = TaskTemplate.objects.get(id=template_id)
        except TaskTemplate.DoesNotExist:
            raise BadRequest('template[id=%s] does not exist' % template_id)
        if not bundle.request.user.has_perm(CREATE_TASK_PERM_NAME, template):
            raise ImmediateHttpResponse(HttpResponseForbidden('You have no permissions to create task'))
        try:
            pipeline_instance = model.objects.__class__.create_pipeline_instance(
                template,
                **pipeline_instance_kwargs
            )
        except PipelineException as e:
            raise BadRequest(e.message)
        kwargs['category'] = template.category
        if bundle.data['flow_type'] == 'common_func':
            kwargs['current_flow'] = 'func_claim'
        else:
            kwargs['current_flow'] = 'execute_task'
        kwargs['pipeline_instance_id'] = pipeline_instance.id
        super(TaskFlowInstanceResource, self).obj_create(bundle, **kwargs)
        return bundle
