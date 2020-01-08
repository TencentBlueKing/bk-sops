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

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext_lazy as _

from blueapps.utils import managermixins
from pipeline.core.constants import PE
from pipeline.exceptions import SubprocessExpiredError
from pipeline.models import PipelineTemplate
from pipeline_web.wrapper import PipelineTemplateWebWrapper

from gcloud.exceptions import FlowExportError
from gcloud.commons.template.constants import PermNm
from gcloud.conf import settings
from gcloud.core.constant import TASK_CATEGORY
from gcloud.core.utils import convert_readable_username


def get_common_permission_list():
    permission_list = [
        ('common_%s' % PermNm.CREATE_TASK_PERM_NAME, 'common template create task'),
        ('common_%s' % PermNm.FILL_PARAMS_PERM_NAME, 'common template fill params'),
        ('common_%s' % PermNm.EXECUTE_TASK_PERM_NAME, 'common template execute task'),
    ]
    return permission_list


def replace_template_id(template_model, pipeline_data, reverse=False):
    activities = pipeline_data[PE.activities]
    for act_id, act in activities.iteritems():
        if act['type'] == PE.SubProcess:
            if not reverse:
                act['template_id'] = template_model.objects.get(pk=act['template_id']).pipeline_template.template_id
            else:
                template = template_model.objects.get(pipeline_template__template_id=act['template_id'])
                act['template_id'] = str(template.pk)


class BaseTemplateManager(models.Manager, managermixins.ClassificationCountMixin):

    def create_pipeline_template(self, **kwargs):
        pipeline_tree = kwargs['pipeline_tree']
        replace_template_id(self.model, pipeline_tree)
        pipeline_template_data = {
            'name': kwargs['name'],
            'creator': kwargs['creator'],
            'description': kwargs['description'],
        }
        pipeline_template = PipelineTemplate.objects.create_model(
            pipeline_tree,
            **pipeline_template_data
        )
        return pipeline_template

    def export_templates(self, template_id_list):
        templates = self.filter(id__in=template_id_list).select_related('pipeline_template').values()
        pipeline_template_id_list = []
        template = {}
        for tmpl in templates:
            pipeline_template_id_list.append(tmpl['pipeline_template_id'])
            tmpl['pipeline_template_str_id'] = tmpl['pipeline_template_id']
            template[tmpl['id']] = tmpl

        try:
            pipeline_temp_data = PipelineTemplateWebWrapper.export_templates(pipeline_template_id_list)
        except SubprocessExpiredError as e:
            raise FlowExportError(e.message)

        all_template_ids = set(pipeline_temp_data['template'].keys())
        additional_template_id = all_template_ids - set(pipeline_template_id_list)
        subprocess_temp_list = self.filter(pipeline_template_id__in=additional_template_id) \
            .select_related('pipeline_template') \
            .values()
        for sub_temp in subprocess_temp_list:
            sub_temp['pipeline_template_str_id'] = sub_temp['pipeline_template_id']
            template[sub_temp['id']] = sub_temp

        result = {
            'template': template,
            'pipeline_template_data': pipeline_temp_data
        }
        return result

    def import_operation_check(self, template_data):

        template = template_data['template']
        pipeline_template = template_data['pipeline_template_data']['template']

        new_template = []
        for tmpl in template.values():
            str_id = tmpl['pipeline_template_str_id']
            pipeline = pipeline_template[str_id]
            new_template.append({
                'id': tmpl['id'],
                'name': pipeline['name']
            })

        override_template = []
        existed_templates = self.filter(pk__in=template.keys(), is_deleted=False) \
            .select_related('pipeline_template')
        for tmpl in existed_templates:
            override_template.append({
                'id': tmpl.id,
                'name': tmpl.pipeline_template.name,
                'template_id': tmpl.pipeline_template.template_id
            })

        result = {
            'can_override': True,
            'new_template': new_template,
            'override_template': override_template
        }
        return result


class BaseTemplate(models.Model):
    """
    @summary: base abstract template，without containing business info
    """
    category = models.CharField(_(u"模板类型"),
                                choices=TASK_CATEGORY,
                                max_length=255,
                                default='Other')
    pipeline_template = models.ForeignKey(PipelineTemplate,
                                          blank=True,
                                          null=True,
                                          on_delete=models.SET_NULL,
                                          to_field='template_id')
    collector = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                       verbose_name=_(u"收藏模板的人"),
                                       blank=True)
    notify_type = models.CharField(_(u"流程事件通知方式"),
                                   max_length=128,
                                   default='[]'
                                   )
    # 形如 json.dumps({'receiver_group': ['Maintainers'], 'more_receiver': 'username1,username2'})
    notify_receivers = models.TextField(_(u"流程事件通知人"),
                                        default='{}'
                                        )
    time_out = models.IntegerField(_(u"流程超时时间(分钟)"),
                                   default=20
                                   )
    is_deleted = models.BooleanField(_(u"是否删除"), default=False)

    class Meta:
        # abstract would not be inherited automatically
        abstract = True
        ordering = ['-id']

    @property
    def category_name(self):
        return self.get_category_display()

    @property
    def creator_name(self):
        return convert_readable_username(self.pipeline_template.creator)

    @property
    def editor_name(self):
        if self.pipeline_template and self.pipeline_template.editor:
            return convert_readable_username(self.pipeline_template.editor)
        else:
            return ''

    @property
    def name(self):
        return self.pipeline_template.name if self.pipeline_template else ''

    @property
    def create_time(self):
        return self.pipeline_template.create_time

    @property
    def edit_time(self):
        return self.pipeline_template.edit_time or self.create_time

    @property
    def pipeline_tree(self):
        tree = self.pipeline_template.data
        replace_template_id(self.__class__, tree, reverse=True)
        return tree

    @property
    def template_id(self):
        return self.id

    @property
    def subprocess_info(self):
        info = self.pipeline_template.subprocess_version_info
        pipeline_temp_ids = [item['descendant_template_id'] for item in info['details']]
        qs = self.__class__.objects.filter(pipeline_template_id__in=pipeline_temp_ids
                                           ).values('pipeline_template_id', 'id')
        pid_to_tid = {item['pipeline_template_id']: item['id'] for item in qs}
        for subprocess_info in info['details']:
            subprocess_info['template_id'] = pid_to_tid[subprocess_info.pop('descendant_template_id')]

        return info

    @property
    def version(self):
        return self.pipeline_template.version

    @property
    def subprocess_has_update(self):
        return self.pipeline_template.subprocess_has_update

    @property
    def template_wrapper(self):
        return PipelineTemplateWebWrapper(self.pipeline_template)

    @property
    def has_subprocess(self):
        return self.pipeline_template.has_subprocess

    def set_deleted(self):
        self.is_deleted = True
        PipelineTemplate.objects.delete_model(self.pipeline_template_id)
        self.save()

    def referencer(self):
        pipeline_template_referencer = self.pipeline_template.referencer()
        if not pipeline_template_referencer:
            return []

        result = self.__class__.objects.filter(pipeline_template_id__in=pipeline_template_referencer,
                                               is_deleted=False).values('id', 'pipeline_template__name')
        for item in result:
            item['name'] = item.pop('pipeline_template__name')
        return result

    def update_pipeline_template(self, **kwargs):
        pipeline_template = self.pipeline_template
        if pipeline_template is None:
            return
        pipeline_tree = kwargs.pop('pipeline_tree')
        replace_template_id(self.__class__, pipeline_tree)
        pipeline_template.update_template(pipeline_tree, **kwargs)

    def get_clone_pipeline_tree(self):
        clone_tree = self.pipeline_template.clone_data()
        replace_template_id(self.__class__, clone_tree, reverse=True)
        return clone_tree

    def get_form(self, version=None):
        return self.template_wrapper.get_form(version)

    def get_outputs(self, version=None):
        return self.template_wrapper.get_outputs(version)

    def user_collect(self, username, method):
        user_model = get_user_model()
        user = user_model.objects.get(username=username)
        if method == 'add':
            self.collector.add(user)
        else:
            self.collector.remove(user)
        self.save()
        return {'result': True, 'data': ''}

    def get_pipeline_tree_by_version(self, version=None):
        tree = self.pipeline_template.data_for_version(version)
        replace_template_id(self.__class__, tree, reverse=True)
        return tree


class CommonTemplateManager(BaseTemplateManager):

    def create(self, **kwargs):
        pipeline_template = self.create_pipeline_template(**kwargs)
        task_template = self.model(
            category=kwargs['category'],
            pipeline_template=pipeline_template,
            notify_type=kwargs['notify_type'],
            notify_receivers=kwargs['notify_receivers'],
            time_out=kwargs['time_out'],
        )
        task_template.save()
        return task_template

    def import_operation_check(self, template_data):
        data = super(CommonTemplateManager, self).import_operation_check(template_data)

        # business template cannot override common template
        has_business_template = any([tmpl.get('business_id') for _, tmpl in template_data['template'].items()])
        if has_business_template:
            data['can_override'] = False
            data['override_template'] = []
        return data

    def import_templates(self, template_data, override):
        template = template_data['template']
        check_info = self.import_operation_check(template_data)
        tid_to_reuse = {}

        # operation validation check
        if override and (not check_info['can_override']):
            return {
                'result': False,
                'message': 'Unable to override common flows or keep ID when importing business flows data',
                'data': 0
            }

        # find old template_id for override using
        # import_id -> reuse_id
        for template_to_be_replaced in check_info['override_template']:
            task_template_id = template_to_be_replaced['id']
            template_id = template_data['template'][str(task_template_id)]['pipeline_template_str_id']
            tid_to_reuse[template_id] = template_to_be_replaced['template_id']

        # import pipeline template first
        id_map = PipelineTemplateWebWrapper.import_templates(template_data['pipeline_template_data'],
                                                             override=override,
                                                             tid_to_reuse=tid_to_reuse)
        old_id_to_new_id = id_map[PipelineTemplateWebWrapper.ID_MAP_KEY]

        new_objects = []
        for tid, tmpl_dict in template.items():
            tmpl_dict['pipeline_template_id'] = old_id_to_new_id[tmpl_dict['pipeline_template_str_id']]
            defaults = {
                'category': tmpl_dict['category'],
                'notify_type': tmpl_dict['notify_type'],
                'notify_receivers': tmpl_dict['notify_receivers'],
                'time_out': tmpl_dict['time_out'],
                'pipeline_template_id': tmpl_dict['pipeline_template_id'],
                'is_deleted': False
            }
            # use update or create to avoid id conflict
            if override:
                self.update_or_create(id=tid, defaults=defaults)
            else:
                new_objects.append(self.model(**defaults))
        self.model.objects.bulk_create(new_objects)

        return {
            'result': True,
            'data': {'count': len(template)},
            'message': 'Successfully imported %s common flows' % len(template)
        }


class CommonTemplate(BaseTemplate):
    """
    @summary: common templates maintained by admin, which all businesses could use to creating tasks
    """
    objects = CommonTemplateManager()

    class Meta(BaseTemplate.Meta):
        verbose_name = _(u"公共流程模板 CommonTemplate")
        verbose_name_plural = _(u"公共流程模板 CommonTemplate")

    def get_notify_receivers_list(self, executor):
        return []


class CommonTmplPerm(models.Model):
    """
    @summary: common templates permissions, to handle person has different perms in different businesses
    """
    common_template_id = models.CharField(_(u"通用流程模板ID"), max_length=255)
    biz_cc_id = models.CharField(_(u"通用流程模板ID"), max_length=255)

    class Meta:
        permissions = get_common_permission_list()
        unique_together = ('common_template_id', 'biz_cc_id')
        index_together = ['common_template_id', 'biz_cc_id']
        verbose_name = _(u"公共流程模板权限 CommonTmplPerm")
        verbose_name_plural = _(u"公共流程模板权限 CommonTmplPerm")
