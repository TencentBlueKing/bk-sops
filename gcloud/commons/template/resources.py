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

import ujson as json

from django.db import transaction
from django.contrib.auth import get_user_model
from django.http.response import HttpResponseForbidden
from tastypie import fields
from tastypie.authorization import Authorization, ReadOnlyAuthorization
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.exceptions import BadRequest, ImmediateHttpResponse, NotFound

from pipeline.exceptions import PipelineException
from pipeline.models import PipelineTemplate, TemplateScheme
from pipeline_web.parser.validator import validate_web_pipeline_tree

from gcloud.core.models import Business
from gcloud.commons.template.models import CommonTemplate
from gcloud.core.constant import TEMPLATE_NODE_NAME_MAX_LENGTH
from gcloud.core.utils import name_handler
from gcloud.webservice3.resources import (
    GCloudModelResource,
    AppSerializer,
    pipeline_node_name_handle,
    TemplateFilterPaginator,
    get_business_for_user
)


class PipelineTemplateResource(GCloudModelResource):
    class Meta:
        queryset = PipelineTemplate.objects.filter(is_deleted=False)
        resource_name = 'pipeline_template'
        authorization = ReadOnlyAuthorization()
        serializer = AppSerializer()
        filtering = {
            'name': ALL,
            'creator': ALL,
            'category': ALL,
            'subprocess_has_update': ALL,
            'edit_time': ['gte', 'lte']
        }
        limit = 0


class CommonAuthorization(Authorization):
    """
    @summary: common authorization
        create/update/delete: only superuser
        read: all users
    """

    def is_superuser(self, bundle):
        if bundle.request.user.is_superuser:
            return True
        raise ImmediateHttpResponse(HttpResponseForbidden('you have no permission to write common flows'))

    def create_list(self, object_list, bundle):
        return []

    def create_detail(self, object_list, bundle):
        return self.is_superuser(bundle)

    def update_list(self, object_list, bundle):
        return self.is_superuser(bundle)

    def update_detail(self, object_list, bundle):
        return self.is_superuser(bundle)

    def delete_list(self, object_list, bundle):
        return self.is_superuser(bundle)

    def delete_detail(self, object_list, bundle):
        return self.is_superuser(bundle)


class CommonTemplateResource(GCloudModelResource):
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
    has_subprocess = fields.BooleanField(
        attribute='has_subprocess',
        readonly=True
    )

    class Meta:
        queryset = CommonTemplate.objects.filter(pipeline_template__isnull=False, is_deleted=False)
        resource_name = 'common_template'
        authorization = CommonAuthorization()
        always_return_data = True
        serializer = AppSerializer()
        filtering = {
            "id": ALL,
            "name": ALL,
            "category": ALL,
            "pipeline_template": ALL_WITH_RELATIONS,
            "subprocess_has_update": ALL,
            "has_subprocess": ALL
        }
        q_fields = ["id", "pipeline_template__name"]
        limit = 0
        paginator_class = TemplateFilterPaginator

    @staticmethod
    def handle_template_name_attr(data):
        data['name'] = name_handler(data['name'],
                                    TEMPLATE_NODE_NAME_MAX_LENGTH)
        pipeline_node_name_handle(data['pipeline_tree'])

    def dehydrate_pipeline_tree(self, bundle):
        return json.dumps(bundle.data['pipeline_tree'])

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
            pipeline_template = model.objects.create_pipeline_template(
                **pipeline_template_kwargs)
        except PipelineException as e:
            raise BadRequest(e.message)
        except CommonTemplate.DoesNotExist:
            raise BadRequest('flow template referred as SubProcess does not exist')
        kwargs['pipeline_template_id'] = pipeline_template.template_id
        return super(CommonTemplateResource, self).obj_create(bundle, **kwargs)

    def obj_update(self, bundle, skip_errors=False, **kwargs):
        with transaction.atomic():
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
            return super(CommonTemplateResource, self).obj_update(bundle, **kwargs)

    def obj_delete(self, bundle, **kwargs):
        try:
            common_tmpl = CommonTemplate.objects.get(id=kwargs['pk'], is_deleted=False)
        except CommonTemplate.DoesNotExist:
            raise NotFound('flow template does not exist')
        referencer = common_tmpl.referencer()
        if referencer:
            flat = ','.join(['%s:%s' % (item['id'], item['name']) for item in referencer])
            raise BadRequest('flow template are referenced by other templates[%s], please delete them first' % flat)
        result = super(CommonTemplateResource, self).obj_delete(bundle, **kwargs)
        if result:
            common_tmpl.set_deleted()
        return result

    def build_filters(self, filters=None, ignore_bad_filters=False):
        filters = super(CommonTemplateResource, self).build_filters(filters=filters,
                                                                    ignore_bad_filters=ignore_bad_filters)

        if 'subprocess_has_update__exact' in filters:
            filters.pop('subprocess_has_update__exact')
        if 'has_subprocess__exact' in filters:
            filters.pop('has_subprocess__exact')

        return filters


class CommonTemplateSchemeResource(GCloudModelResource):
    class Meta:
        queryset = TemplateScheme.objects.all()
        resource_name = 'common_scheme'
        authorization = Authorization()
        always_return_data = True
        serializer = AppSerializer()

        filtering = {
            'template': ALL,
        }
        limit = 0

    def build_filters(self, filters=None, **kwargs):
        orm_filters = super(CommonTemplateSchemeResource, self).build_filters(filters, **kwargs)
        if 'biz_cc_id' in filters and 'template_id' in filters:
            template_id = filters.pop('template_id')[0]
            biz_cc_id = filters.pop('biz_cc_id')[0]
            template = CommonTemplate.objects.get(pk=template_id)
            orm_filters.update({
                'template__template_id': template.pipeline_template.template_id,
                # 这里通过业务ID前缀隔离不同业务在同一个公共流程下的执行方案
                'unique_id__startswith': '%s-' % biz_cc_id,
            })
        elif 'pk' not in filters:
            # 不允许请求全部执行方案
            orm_filters.update({'unique_id': ''})
        return orm_filters

    def alter_list_data_to_serialize(self, request, data):
        for bundle in data['objects']:
            bundle.data.pop('data')

        return data

    def obj_create(self, bundle, **kwargs):
        biz_cc_id = bundle.data.pop('biz_cc_id', None)
        template_id = bundle.data.pop('template_id', None)
        try:
            template = CommonTemplate.objects.get(pk=template_id)
        except Exception:
            raise BadRequest('common template does not exist')
        business = get_business_for_user(bundle.request.user, ['view_business'])
        if not business.filter(cc_id=biz_cc_id).exists():
            raise ImmediateHttpResponse(HttpResponseForbidden('you have no permission to make such operation'))
        bundle.data['name'] = name_handler(bundle.data['name'], TEMPLATE_NODE_NAME_MAX_LENGTH)
        kwargs['unique_id'] = '%s-%s-%s' % (biz_cc_id, template_id, bundle.data['name'])
        if TemplateScheme.objects.filter(unique_id=kwargs['unique_id']).exists():
            raise BadRequest('common template scheme name has existed, please change the name')
        kwargs['template'] = template.pipeline_template
        return super(CommonTemplateSchemeResource, self).obj_create(bundle, **kwargs)

    def obj_delete(self, bundle, **kwargs):
        try:
            scheme_id = kwargs['pk']
            scheme = TemplateScheme.objects.get(pk=scheme_id)
            CommonTemplate.objects.get(pipeline_template=scheme.template)
        except Exception:
            raise BadRequest('common scheme or template does not exist')
        try:
            biz_cc_id = int(scheme['unique_id'].split('-')[0])
        except Exception:
            # maybe old unique id rule
            biz_cc_id = None
        business = get_business_for_user(bundle.request.user, ['manage_business'])
        if Business.objects.filter(cc_id=biz_cc_id) and not business.filter(cc_id=biz_cc_id).exists():
            raise ImmediateHttpResponse(HttpResponseForbidden('you have no permission to make such operation'))
        return super(CommonTemplateSchemeResource, self).obj_delete(bundle, **kwargs)
