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
import ujson as json

from django.utils.translation import ugettext_lazy as _
from tastypie import fields
from tastypie.authorization import ReadOnlyAuthorization
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.exceptions import BadRequest

from pipeline.engine import states
from pipeline.exceptions import PipelineException
from pipeline.models import PipelineInstance
from pipeline_web.parser.validator import validate_web_pipeline_tree
from pipeline_web.exceptions import ParserException

from gcloud.core.utils import name_handler
from gcloud.core.constant import TASK_NAME_MAX_LENGTH
from gcloud.commons.template.models import CommonTemplate, CommonTmplPerm
from gcloud.commons.template.constants import PermNm
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.taskflow3.models import TaskFlowInstance
from gcloud.contrib.appmaker.models import AppMaker
from gcloud.webservice3.resources import (
    GCloudModelResource,
    GCloudGenericAuthorization,
    AppSerializer,
    pipeline_node_name_handle,
    BusinessResource,
)

logger = logging.getLogger('root')


class TaskflowAuthorization(GCloudGenericAuthorization):
    def create_detail(self, object_list, bundle):
        business = getattr(bundle.obj, 'business')
        template_id = bundle.data['template_id']
        template_source = bundle.data.get('template_source', 'business')
        # 业务流程
        if template_source == 'business':
            try:
                template = TaskTemplate.objects.get(pk=str(template_id),
                                                    business=business,
                                                    is_deleted=False)
            except TaskTemplate.DoesNotExist:
                raise BadRequest('template[pk=%s] does not exist' % template_id)
            if not bundle.request.user.has_perm(PermNm.CREATE_TASK_PERM_NAME, template):
                return False

            if bundle.data['create_method'] == 'app_maker':
                try:
                    app_maker = AppMaker.objects.get(pk=bundle.data['create_info'])
                except AppMaker.DoesNotExist:
                    raise BadRequest('Mini-APP[pk=%s] does not exist, that is the value of create_info' %
                                     bundle.data['create_info'])
                if app_maker.task_template.id != int(template_id):
                    raise BadRequest('Template[pk=%s] does not match the template[pk=%s] used to creating '
                                     'Mini-APP[pk=%s]' % (template_id,
                                                          app_maker.task_template.id,
                                                          bundle.data['create_info'])
                                     )
        # 公共流程
        else:
            if not CommonTemplate.objects.filter(pk=str(template_id), is_deleted=False).exists():
                raise BadRequest('common template[pk=%s] does not exist' % template_id)
            template_perm, _ = CommonTmplPerm.objects.get_or_create(common_template_id=template_id,
                                                                    biz_cc_id=business.cc_id)
            perm = 'common_%s' % PermNm.CREATE_TASK_PERM_NAME
            if not bundle.request.user.has_perm(perm, template_perm):
                return False

        return self._get_business_for_user(
            bundle.request.user,
            perms=['view_business']
        ).filter(pk=business.pk).exists()


class PipelineInstanceResource(GCloudModelResource):
    class Meta:
        queryset = PipelineInstance.objects.filter(is_deleted=False)
        resource_name = 'pipeline_instance'
        authorization = ReadOnlyAuthorization()
        serializer = AppSerializer()
        filtering = {
            'name': ALL,
            'is_finished': ALL,
            'creator': ALL,
            'category': ALL,
            'subprocess_has_update': ALL,
            'edit_time': ['gte', 'lte'],
            'executor': ALL,
            'is_started': ALL,
            'start_time': ['gte', 'lte']
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
            'id': ALL,
            'business': ALL_WITH_RELATIONS,
            'name': ALL,
            'category': ALL,
            'create_method': ALL,
            'create_info': ALL,
            'template_source': ALL,
            'template_id': ALL,
            'pipeline_instance': ALL_WITH_RELATIONS,
        }
        q_fields = ['id', 'pipeline_instance__name']
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
            template_source = bundle.data.get('template_source', 'business')
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
        except ParserException as e:
            raise BadRequest(e.message)

        if template_source == 'business':
            try:
                template = TaskTemplate.objects.get(pk=template_id)
            except TaskTemplate.DoesNotExist:
                raise BadRequest('template[pk=%s] does not exist' % template_id)
        else:
            try:
                template = CommonTemplate.objects.get(pk=str(template_id),
                                                      is_deleted=False)
            except CommonTemplate.DoesNotExist:
                raise BadRequest('common template[pk=%s] does not exist' % template_id)

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

    def obj_delete(self, bundle, **kwargs):
        try:
            taskflow = TaskFlowInstance.objects.get(id=kwargs['pk'])
        except Exception:
            raise BadRequest('taskflow does not exits')

        raw_state = taskflow.raw_state

        if raw_state and raw_state not in states.ARCHIVED_STATES:
            raise BadRequest(_(u"无法删除未进入完成或撤销状态的流程"))

        return super(TaskFlowInstanceResource, self).obj_delete(bundle, **kwargs)
