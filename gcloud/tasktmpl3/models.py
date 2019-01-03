# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
import datetime
import json
import re

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Count
from django.utils.translation import ugettext_lazy as _

from blueapps.utils import managermixins
from gcloud.conf import settings
from gcloud.core.constant import TASK_CATEGORY, AE
from gcloud.core.models import Business
from gcloud.core.utils import convert_readable_username, timestamp_to_datetime, format_datetime
from gcloud.tasktmpl3.utils import get_notify_receivers
from gcloud.tasktmpl3.exceptions import TaskTemplateExportError
from pipeline.component_framework.models import ComponentModel
from pipeline.contrib.statistics.models import ComponentInTemplate
from pipeline.models import PipelineTemplate, PipelineInstance, TemplateRelationship
from pipeline.core.constants import PE
from pipeline.parser.utils import replace_all_id
from pipeline.exceptions import SubprocessExpiredError

CREATE_TASK_PERM_NAME = 'create_task'
FILL_PARAMS_PERM_NAME = 'fill_params'
EXECUTE_TASK_PERM_NAME = 'execute_task'


def get_permission_list():
    permission_list = [
        (CREATE_TASK_PERM_NAME, _(u"新建任务")),
        (FILL_PARAMS_PERM_NAME, _(u"填写参数")),
        (EXECUTE_TASK_PERM_NAME, _(u"执行任务")),
    ]
    return permission_list


def replace_template_id(pipeline_data, reverse=False):
    activities = pipeline_data[PE.activities]
    for act_id, act in activities.iteritems():
        if act['type'] == PE.SubProcess:
            if not reverse:
                act['template_id'] = TaskTemplate.objects.get(pk=act['template_id']).pipeline_template.template_id
            else:
                act['template_id'] = str(TaskTemplate.objects.get(pipeline_template__template_id=act['template_id']).pk)


class TaskTemplateManager(models.Manager, managermixins.ClassificationCountMixin):

    @staticmethod
    def create_pipeline_template(**kwargs):
        pipeline_tree = kwargs['pipeline_tree']
        try:
            replace_template_id(pipeline_tree)
        except Exception:
            raise TaskTemplate.DoesNotExist()
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

    def create(self, **kwargs):
        pipeline_template = self.create_pipeline_template(**kwargs)
        task_template = self.model(
            business=kwargs['business'],
            category=kwargs['category'],
            pipeline_template=pipeline_template,
            notify_type=kwargs['notify_type'],
            notify_receivers=kwargs['notify_receivers'],
            time_out=kwargs['time_out'],
        )
        task_template.save()
        return task_template

    def export_templates(self, template_id_list, biz_cc_id):
        data = {}

        pipeline_template_id_list = []
        template = {}
        for template_id in template_id_list:
            temp = self.values().get(id=template_id, business__cc_id=biz_cc_id)
            temp.pop('business_id')

            pipeline_template_id_list.append(temp['pipeline_template_id'])
            temp['pipeline_template_str_id'] = temp['pipeline_template_id']
            template[temp['id']] = temp

        try:
            pipeline_temp_data = PipelineTemplate.objects.export_templates(pipeline_template_id_list)
        except SubprocessExpiredError as e:
            raise TaskTemplateExportError(e.message)

        all_template_ids = set(pipeline_temp_data['template'].keys())
        additional_template_id = all_template_ids - set(pipeline_template_id_list)
        subprocess_temp_list = self.filter(pipeline_template_id__in=additional_template_id).values()
        for sub_temp in subprocess_temp_list:
            sub_temp.pop('business_id')
            sub_temp['pipeline_template_str_id'] = sub_temp['pipeline_template_id']
            template[sub_temp['id']] = sub_temp

        data['template'], data['pipeline_template_data'] = template, pipeline_temp_data
        return data

    def import_operation_check(self, template_data, biz_cc_id):
        result = {
            'can_override': False,
            'new_template': [],
            'override_template': []
        }

        template = template_data['template']

        relate_biz_cc_ids = self.filter(id__in=template.keys(),
                                        is_deleted=False).values_list('business__cc_id', flat=True)
        is_multiple_relate = len(set(relate_biz_cc_ids)) > 1
        is_across_override = relate_biz_cc_ids and relate_biz_cc_ids[0] != int(biz_cc_id)

        result['can_override'] = can_override = not (is_multiple_relate or is_across_override)
        pipeline_template = template_data['pipeline_template_data']['template']

        for t in template.values():
            str_id = t['pipeline_template_str_id']
            pipeline = pipeline_template[str_id]
            result['new_template'].append({
                'id': t['id'],
                'name': pipeline['name']
            })

        if can_override:
            override_template = self.filter(id__in=template.keys(), is_deleted=False)
            for t in override_template:
                result['override_template'].append({
                    'id': t.id,
                    'name': t.pipeline_template.name,
                    'template_id': t.pipeline_template.template_id
                })

        return result

    def import_templates(self, template_data, override, biz_cc_id):
        template = template_data['template']
        business = Business.objects.get(cc_id=biz_cc_id)
        check_info = self.import_operation_check(template_data, biz_cc_id)
        tid_to_reuse = {}

        # operation validation check
        if override and (not check_info['can_override']):
            return {
                'result': False,
                'message': 'Unable to override template across business',
                'data': 0
            }

        # find old template_id for override using
        # import_id -> reuse_id
        for template_to_be_replaced in check_info['override_template']:
            task_template_id = template_to_be_replaced['id']
            template_id = template_data['template'][str(task_template_id)]['pipeline_template_str_id']
            tid_to_reuse[template_id] = template_to_be_replaced['template_id']

        # import pipeline template first
        id_map = PipelineTemplate.objects.import_templates(template_data['pipeline_template_data'],
                                                           override=override,
                                                           tid_to_reuse=tid_to_reuse)
        old_id_to_new_id = id_map[PipelineTemplate.ID_MAP_KEY]

        for tid, template_dict in template.items():
            template_dict['pipeline_template_id'] = old_id_to_new_id[template_dict['pipeline_template_str_id']]
            defaults = {
                'business': business,
                'category': template_dict['category'],
                'notify_type': template_dict['notify_type'],
                'notify_receivers': template_dict['notify_receivers'],
                'time_out': template_dict['time_out'],
                'pipeline_template_id': template_dict['pipeline_template_id'],
                'is_deleted': False
            }
            # use update or create to avoid id conflict
            if override:
                self.update_or_create(id=tid,
                                      defaults=defaults)
            else:
                self.model(**defaults).save()

        return {
            'result': True,
            'data': len(template),
            'message': 'Successfully imported %s templates' % len(template)
        }

    def extend_classified_count(self, group_by, filters=None, page=None, limit=None):
        """
        @summary: 兼容按照任务状态分类的扩展
        @param group_by:
        @param filters:
        @param page:
        @param limit:
        @return:
        """
        # 获得所有类型的dict列表
        category_dict = dict(TASK_CATEGORY)
        if filters is None:
            filters = {}
        tasktmpl_inst_regex = re.compile(r'^name|creator_name|editor_name|'
                                         r'create_time|edit_time|edit_finish_time|finish_time')
        prefix_filters = {}
        for cond in filters:
            # 如果conditions内容为空或为空字符，不可加入查询条件中
            if filters[cond] == 'None' or filters[cond] == '' or cond == 'component_code':
                continue
            if tasktmpl_inst_regex.match(cond):
                filter_cond = 'pipeline_template__%s' % cond
                # 时间需要大于小于
                if cond == 'create_time':
                    filter_cond = '%s__gte' % filter_cond
                    prefix_filters.update({filter_cond: timestamp_to_datetime(filters[cond])})
                    continue
                elif cond == 'finish_time':
                    filter_cond = 'pipeline_template__create_time__lt'
                    prefix_filters.update(
                        {filter_cond: timestamp_to_datetime(filters[cond]) + datetime.timedelta(days=1)})
                    continue
                # 编辑时间与创建时间需要分开查询
                elif cond == 'edit_time':
                    filter_cond = '%s__gte' % filter_cond
                    prefix_filters.update({filter_cond: timestamp_to_datetime(filters[cond])})
                    continue
                elif cond == 'edit_finish_time':
                    filter_cond = 'pipeline_template__edit_time__lt'
                    prefix_filters.update(
                        {filter_cond: timestamp_to_datetime(filters[cond]) + datetime.timedelta(days=1)})
                    continue
            else:
                filter_cond = cond
            prefix_filters.update({filter_cond: filters[cond]})

        # 获得原子dict列表
        component_dict = ComponentModel.objects.get_component_dict()

        if group_by == AE.state:
            try:
                tasktmpl = self.filter(**prefix_filters)
            except Exception as e:
                message = u"query_task_list params conditions[%s] have invalid key or value: %s" % (filters, e)
                return False, message
            total = tasktmpl.count()
            groups = [
                {
                    'code': 'CREATED',
                    'name': _(u"未执行"),
                    'value': tasktmpl.filter(pipeline_template__is_started=False).count()
                },
                {
                    'code': 'EXECUTING',
                    'name': _(u"执行中"),
                    'value': tasktmpl.filter(pipeline_template__is_started=True,
                                             pipeline_template__is_finished=False).count()
                },
                {
                    'code': 'FINISHED',
                    'name': _(u"已完成"),
                    'value': tasktmpl.filter(pipeline_template__is_finished=True).count()
                }
            ]
        elif group_by == AE.business__cc_id:
            cc_name = AE.business__cc_name
            try:
                tasktmpl = self.filter(**prefix_filters)
            except Exception as e:
                message = u"query_task_list params conditions[%s] have invalid key or value: %s" % (filters, e)
                return False, message
            # 获取所有数据
            total = tasktmpl.count()
            queryset = tasktmpl.values(group_by, cc_name).annotate(value=Count(group_by)).order_by("-value")
            groups = []
            for data in queryset:
                groups.append({
                    'code': data.get(group_by),
                    'name': data.get(cc_name),
                    'value': data.get('value', 0)
                })
        elif group_by == AE.atom_cite:
            # 这里没有其他原子节点的内容
            try:
                # 需要获得符合的查询的对应 template_id 列表
                template_list = self.filter(**prefix_filters).values_list("pipeline_template__template_id")
            except Exception as e:
                message = u"query_task_list params conditions[%s] have invalid key or value: %s" % (filters, e)
                return False, message
            component_list = ComponentModel.objects.filter(status=True).values("code")
            # 用 template_id 列表获取所有符合条件的总数
            other_component_list = ComponentInTemplate.objects.filter(template_id__in=template_list).values(
                "component_code").annotate(
                value=Count("component_code")).order_by()
            components_dict = {}
            total = 0
            for component in other_component_list:
                value = component["value"]
                components_dict[component["component_code"]] = value
                # 总数不能通过查询获得，需要通过循环计数
                total += value
            groups = []
            # 循环聚合信息
            for data in component_list:
                code = data.get("code")
                value = components_dict.get(code, 0)
                groups.append({
                    'code': code,
                    'name': component_dict.get(code, None),
                    'value': value
                })
        elif group_by == AE.atom_template:
            # 按起始时间、业务（可选）、类型（可选）、原子查询被引用的流程模板列表(dataTable)
            try:
                # 需要获得符合的查询的对应 template_id 列表
                template_list = self.filter(**prefix_filters).filter()
            except Exception as e:
                message = u"query_task_list params conditions[%s] have invalid key or value: %s" % (filters, e)
                return False, message
            # 获取原子code
            component_code = filters.get("component_code")
            # 获取到组件code对应的template_id_list
            if component_code:
                template_id_list = ComponentInTemplate.objects.filter(component_code=component_code).values_list(
                    "template_id")
            else:
                template_id_list = ComponentInTemplate.objects.all().values_list("template_id")
            total = template_id_list.count()
            template_list = template_list.filter(pipeline_template__template_id__in=template_id_list).values(
                "id",
                "business__cc_id",
                "business__cc_name",
                "pipeline_template__name",
                "category",
                "pipeline_template__edit_time",
                "pipeline_template__editor"
            )[(page - 1) * limit:page * limit]
            groups = []
            # 循环聚合信息
            for data in template_list:
                groups.append({
                    'templateId': data.get("id"),
                    'businessId': data.get("business__cc_id"),
                    'businessName': data.get("business__cc_name"),
                    'templateName': data.get("pipeline_template__name"),
                    'category': category_dict[data.get("category")],  # 需要将code转为名称
                    "editTime": format_datetime(data.get("pipeline_template__edit_time")),
                    "editor": data.get("pipeline_template__editor")
                })
        elif group_by == AE.atom_execute:
            try:
                # 需要获得符合的查询的对应 template_id 列表
                template_list = self.filter(**prefix_filters).filter()
            except Exception as e:
                message = u"query_task_list params conditions[%s] have invalid key or value: %s" % (filters, e)
                return False, message
            # 获取原子code
            component_code = filters.get("component_code")
            # 获取到组件code对应的template_id
            if component_code:
                template_id_list = ComponentInTemplate.objects.filter(component_code=component_code).values_list(
                    "template_id")
            else:
                template_id_list = ComponentInTemplate.objects.all().values_list("template_id")
            total = template_id_list.count()
            template_list = template_list.filter(pipeline_template__template_id__in=template_id_list).values(
                "id",
                "business__cc_name",
                "business__cc_id",
                "pipeline_template__name",
                "category",
                "pipeline_template__edit_time",
                "pipeline_template__editor")[(page - 1) * limit:page * limit]
            groups = []
            # 循环聚合信息
            for data in template_list:
                groups.append({
                    'templateId': data.get("id"),
                    'businessId': data.get("business__cc_id"),
                    'businessName': data.get("business__cc_name"),
                    'templateName': data.get("pipeline_template__name"),
                    'category': category_dict[data.get("category")],
                    "editTime": data.get("pipeline_template__edit_time").strftime("%Y-%m-%d %H:%M:%S"),
                    "editor": data.get("pipeline_template__editor")
                })
        elif group_by == AE.template_cite:
            # 按起始时间、业务（可选）、类型（可选）查询各流程模板被引用为子流程个数、创建轻应用个数、创建任务实例个数
            try:
                # 需要获得符合的查询的对应 template_id 列表
                template_list = self.filter(**prefix_filters).filter()
            except Exception as e:
                message = u"query_task_list params conditions[%s] have invalid key or value: %s" % (filters, e)
                return False, message
            total = template_list.count()
            template_list = template_list[(page - 1) * limit:page * limit]
            # 获取分页的数据
            id_list = list(template_list.values_list("id"))
            t_id_list = list(template_list.values_list("pipeline_template__template_id"))
            n_id_list = []
            for x in t_id_list:
                n_id_list.append(x[0])
            # 轻应用的数据已分页
            appmaker_list = template_list.values("id", "appmaker").annotate(value=Count("appmaker"))
            taskflow_list = PipelineInstance.objects.filter(template_id__in=id_list).values("template_id").annotate(
                value=Count("template_id")).order_by()
            relationship_list = TemplateRelationship.objects.filter(descendant_template_id__in=n_id_list).values(
                "descendant_template_id").annotate(
                value=Count("descendant_template_id")).order_by()
            appmaker_dict = {}
            for appmaker in appmaker_list:
                appmaker_dict[appmaker["id"]] = appmaker["value"]
            relationship_dict = {}
            for relationship in relationship_list:
                relationship_dict[relationship["descendant_template_id"]] = relationship["value"]
            taskflow_dict = {}
            for taskflow in taskflow_list:
                taskflow_dict[taskflow["template_id"]] = taskflow["value"]
            groups = []
            # todo 缺少子流程部分
            for template in template_list:
                id = template.id
                groups.append({
                    'id': template.id,
                    'templateName': template.name,
                    'appmakerTotal': appmaker_dict[id],
                    'relationshipTotal': relationship_dict.get(template.pipeline_template.template_id, 0),
                    'instanceTotal': taskflow_dict.get(id, 0)
                })
        elif group_by == AE.template_node:
            # 按起始时间、业务（可选）、类型（可选）查询各流程模板原子节点个数、子流程节点个数、网关节点数(dataTable)
            try:
                # 需要获得符合的查询的对应 template_id 列表
                template_list = self.filter(**prefix_filters).filter()
            except Exception as e:
                message = u"query_task_list params conditions[%s] have invalid key or value: %s" % (filters, e)
                return False, message
            # 总数
            total = template_list.count()
            groups = []
            # 需要循环执行计算相关节点
            for template in template_list[(page - 1) * limit:page * limit]:
                atom_total = 0
                subprocess_total = 0
                pipeline_tree = template.pipeline_tree
                tree_activities = pipeline_tree["activities"]
                gateways_total = len(pipeline_tree["gateways"])
                for activity in tree_activities:
                    activity_type = tree_activities[activity]["type"]
                    if activity_type == "ServiceActivity":
                        atom_total += 1
                    elif activity_type == "SubProcess":
                        subprocess_total += 1
                pipeline_template = template.pipeline_template
                # 插入信息
                groups.append({
                    'templateId': template.id,
                    'businessId': template.business.cc_id,
                    'businessName': template.business.cc_name,
                    'templateName': pipeline_template.name,
                    'category': category_dict[template.category],
                    "editTime": format_datetime(pipeline_template.edit_time),
                    "creator": pipeline_template.creator,
                    "atomTotal": atom_total,
                    "subprocessTotal": subprocess_total,
                    "gatewaysTotal": gateways_total
                })
        elif group_by in [AE.category, AE.create_method, AE.flow_type]:
            try:
                total, groups = self.classified_count(prefix_filters, group_by)
            except Exception as e:
                message = u"query_task_list params conditions[%s] have invalid key or value: %s" % (filters, e)
                return False, message
        else:
            total, groups = 0, []
        data = {'total': total, 'groups': groups}
        return True, data

    def replace_all_template_tree_node_id(self):
        templates = self.filter(is_deleted=False)
        success = 0
        for template in templates:
            tree_data = template.pipeline_template.data
            try:
                replace_all_id(tree_data)
            except:
                continue
            template.pipeline_template.update_template(tree_data)
            success += 1
        return len(templates), success


class TaskTemplate(models.Model):
    business = models.ForeignKey(Business,
                                 verbose_name=_(u"所属业务"),
                                 blank=True,
                                 null=True,
                                 on_delete=models.SET_NULL)
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

    objects = TaskTemplateManager()

    def __unicode__(self):
        return u'%s_%s' % (self.business, self.pipeline_template or 'None')

    class Meta:
        verbose_name = _(u"流程模板 TaskTemplate")
        verbose_name_plural = _(u"流程模板 TaskTemplate")
        ordering = ['-id']
        permissions = get_permission_list()

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
        replace_template_id(tree, reverse=True)
        # 兼容3.1.18的步骤名称taskName
        activities = tree[PE.activities]
        for act_id, act in activities.iteritems():
            if act.get('taskName') and not act.get('stage_name'):
                act['stage_name'] = act['taskName']
        return tree

    @property
    def template_id(self):
        return str(self.id)

    @property
    def subprocess_info(self):
        return self.pipeline_template.subprocess_version_info

    @property
    def version(self):
        return self.pipeline_template.version

    @property
    def subprocess_has_update(self):
        return self.pipeline_template.subprocess_has_update

    def get_notify_receivers_list(self, username):
        notify_receivers = json.loads(self.notify_receivers)
        receiver_group = notify_receivers.get('receiver_group', [])
        more_receiver = notify_receivers.get('more_receiver', '')
        receivers = get_notify_receivers(username, self.business.cc_id, receiver_group, more_receiver)
        return receivers

    def update_pipeline_template(self, **kwargs):
        pipeline_template = self.pipeline_template
        if pipeline_template is None:
            return
        pipeline_tree = kwargs.pop('pipeline_tree')
        replace_template_id(pipeline_tree)
        pipeline_template.update_template(pipeline_tree, **kwargs)

    def get_clone_pipeline_tree(self):
        clone_tree = self.pipeline_template.clone_data()
        replace_template_id(clone_tree, reverse=True)
        return clone_tree

    def get_form(self, version=None):
        return self.pipeline_template.get_form(version)

    def get_outputs(self):
        return self.pipeline_template.get_outputs()

    def user_collect(self, username, method):
        user_model = get_user_model()
        user = user_model.objects.get(username=username)
        if method == 'add':
            self.collector.add(user)
        else:
            self.collector.remove(user)
        self.save()
        return {'result': True, 'data': ''}
