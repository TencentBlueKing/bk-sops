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

from __future__ import absolute_import

import Queue
import ujson as json
import zlib
import hashlib
import logging
import copy

from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.db import models, transaction
from django.utils.module_loading import import_string

from pipeline.service import task_service
from pipeline.utils.uniqid import uniqid, node_uniqid
from pipeline.parser.utils import replace_all_id
from pipeline.parser.context import get_pipeline_context
from pipeline.utils.graph import Graph
from pipeline.exceptions import SubprocessRefError
from pipeline.engine.utils import calculate_elapsed_time, ActionResult
from pipeline.core.constants import PE
from pipeline.conf import settings

MAX_LEN_OF_NAME = 128
logger = logging.getLogger('root')


class CompressJSONField(models.BinaryField):
    def __init__(self, compress_level=6, *args, **kwargs):
        super(CompressJSONField, self).__init__(*args, **kwargs)
        self.compress_level = compress_level

    def get_prep_value(self, value):
        value = super(CompressJSONField, self).get_prep_value(value)
        return zlib.compress(json.dumps(value), self.compress_level)

    def to_python(self, value):
        value = super(CompressJSONField, self).to_python(value)
        return json.loads(zlib.decompress(value))

    def from_db_value(self, value, expression, connection, context):
        return self.to_python(value)


class SnapshotManager(models.Manager):
    def create_or_get_snapshot(self, data):
        h = hashlib.md5()
        h.update(json.dumps(data))
        snapshot, created = self.get_or_create(md5sum=h.hexdigest())
        if created:
            snapshot.data = data
            snapshot.save()
        return snapshot, created

    def data_for_snapshot(self, snapshot_id):
        return self.get(id=snapshot_id).data


class Snapshot(models.Model):
    """
    数据快照
    """
    md5sum = models.CharField(_(u"快照字符串的md5sum"), max_length=32, unique=True)
    create_time = models.DateTimeField(_(u"创建时间"), auto_now_add=True)
    data = CompressJSONField(null=True, blank=True)

    objects = SnapshotManager()

    class Meta:
        verbose_name = _(u"模板快照")
        verbose_name_plural = _(u"模板快照")
        ordering = ['-id']
        app_label = 'pipeline'

    def __unicode__(self):
        return unicode(self.md5sum)

    def has_change(self, data):
        """
        检测 data 的 md5 是否和当前存储的不一致
        @param data:
        @return: 新的 md5，md5 是否有变化
        """
        h = hashlib.md5()
        h.update(json.dumps(data))
        md5 = h.hexdigest()
        return md5, self.md5sum != md5


class TreeInfo(models.Model):
    """
    pipeline 数据信息
    """
    data = CompressJSONField(null=True, blank=True)


def get_subprocess_act_list(pipeline_data):
    """
    获取 pipeline 结构中所有的子流程节点
    @param pipeline_data: 流程结构数据
    @return: 子流程节点
    """
    activities = pipeline_data[PE.activities]
    act_ids = filter(lambda act_id: activities[act_id][PE.type] == PE.SubProcess, activities)
    return [activities[act_id] for act_id in act_ids]


def _act_id_in_graph(act):
    """
    获取子流程节点引用的模板 ID
    @param act: 子流程节点
    @return: 模板 ID:版本 或 模板ID
    """
    return '%s:%s' % (act['template_id'], act['version']) if act.get('version') else act['template_id']


class TemplateManager(models.Manager):

    def subprocess_ref_validate(self, data, root_id=None, root_name=None):
        """
        验证子流程引用是否合法
        @param data:
        @param root_id:
        @param root_name:
        @return: 引用是否合法，相关信息
        """
        try:
            sub_refs, name_map = self.construct_subprocess_ref_graph(data, root_id=root_id,
                                                                     root_name=root_name)
        except PipelineTemplate.DoesNotExist as e:
            return False, e.message

        nodes = sub_refs.keys()
        flows = []
        for node in nodes:
            for ref in sub_refs[node]:
                if ref in nodes:
                    flows.append([node, ref])
        graph = Graph(nodes, flows)
        # circle reference check
        trace = graph.get_cycle()
        if trace:
            name_trace = u" → ".join(map(lambda proc_id: name_map[proc_id], trace))
            return False, _(u"子流程引用链中存在循环引用：%s") % name_trace

        return True, ''

    def create_model(self, structure_data, **kwargs):
        """
        创建流程模板对象
        @param structure_data: pipeline 结构数据
        @param kwargs: 其他参数
        @return: 流程模板
        """
        result, msg = self.subprocess_ref_validate(structure_data)

        if not result:
            raise SubprocessRefError(msg)

        snapshot, _ = Snapshot.objects.create_or_get_snapshot(structure_data)
        kwargs['snapshot'] = snapshot
        kwargs['template_id'] = node_uniqid()
        obj = self.create(**kwargs)
        # version track
        # TemplateVersion.objects.track(obj)

        return obj

    def delete_model(self, template_ids):
        """
        删除模板对象
        @param template_ids: 模板对象 ID 列表或 ID
        @return:
        """
        if not isinstance(template_ids, list):
            template_ids = [template_ids]
        qs = self.filter(template_id__in=template_ids)
        for template in qs:
            template.is_deleted = True
            template.name = uniqid()
            template.save()

    def construct_subprocess_ref_graph(self, pipeline_data, root_id=None, root_name=None):
        """
        构造子流程引用图
        @param pipeline_data: pipeline 结构数据
        @param root_id: 所有引用开始的根流程 ID
        @param root_name: 根流程名
        @return: 子流程引用图，模板 ID -> 模板姓名映射字典
        """
        subprocess_act = get_subprocess_act_list(pipeline_data)
        tid_queue = Queue.Queue()
        graph = {}
        version = {}
        name_map = {}

        if root_id:
            graph[root_id] = [_act_id_in_graph(act) for act in subprocess_act]
            name_map[root_id] = root_name

        for act in subprocess_act:
            tid_queue.put(_act_id_in_graph(act))
            version[_act_id_in_graph(act)] = act.get('version')

        while not tid_queue.empty():
            tid = tid_queue.get()
            template = self.get(template_id=tid.split(':')[0])
            name_map[tid] = template.name
            subprocess_act = get_subprocess_act_list(template.data_for_version(version[tid]))

            for act in subprocess_act:
                ref_tid = _act_id_in_graph(act)
                graph.setdefault(tid, []).append(ref_tid)
                version[_act_id_in_graph(act)] = act.get('version')
                if ref_tid not in graph:
                    tid_queue.put(ref_tid)
            if not subprocess_act:
                graph[tid] = []

        return graph, name_map

    def unfold_subprocess(self, pipeline_data):
        """
        展开 pipeline 数据中所有的子流程
        @param pipeline_data: pipeline 数据
        @return:
        """
        replace_all_id(pipeline_data)
        activities = pipeline_data[PE.activities]
        for act_id, act in activities.items():
            if act[PE.type] == PE.SubProcess:
                subproc_data = self.get(template_id=act['template_id']) \
                    .data_for_version(act.get('version'))

                self.unfold_subprocess(subproc_data)

                subproc_data['id'] = act_id
                act['pipeline'] = subproc_data

    def replace_id(self, pipeline_data):
        """
        替换 pipeline 中所有 ID
        @param pipeline_data: pipeline 数据
        @return:
        """
        replace_all_id(pipeline_data)
        activities = pipeline_data[PE.activities]
        for act_id, act in activities.items():
            if act[PE.type] == PE.SubProcess:
                subproc_data = act['pipeline']
                self.unfold_subprocess(subproc_data)
                subproc_data['id'] = act_id
                act['pipeline'] = subproc_data


class PipelineTemplate(models.Model):
    """
    流程模板
    """
    template_id = models.CharField(_(u"模板ID"), max_length=32, unique=True)
    name = models.CharField(_(u"模板名称"), max_length=MAX_LEN_OF_NAME, default='default_template')
    create_time = models.DateTimeField(_(u"创建时间"), auto_now_add=True)
    creator = models.CharField(_(u"创建者"), max_length=32)
    description = models.TextField(_(u"描述"), null=True, blank=True)
    editor = models.CharField(_(u"修改者"), max_length=32, null=True, blank=True)
    edit_time = models.DateTimeField(_(u"修改时间"), auto_now=True)
    snapshot = models.ForeignKey(Snapshot, verbose_name=_(u"模板结构数据"), related_name='snapshot_templates')
    has_subprocess = models.BooleanField(_(u"是否含有子流程"), default=False)
    is_deleted = models.BooleanField(
        _(u"是否删除"),
        default=False,
        help_text=_(u"表示当前模板是否删除")
    )

    objects = TemplateManager()

    class Meta:
        verbose_name = _(u"Pipeline模板")
        verbose_name_plural = _(u"Pipeline模板")
        ordering = ['-edit_time']
        app_label = 'pipeline'

    def __unicode__(self):
        return '%s-%s' % (self.template_id, self.name)

    @property
    def data(self):
        return self.snapshot.data

    @property
    def version(self):
        return self.snapshot.md5sum

    @property
    def subprocess_version_info(self):
        # 1. get all subprocess
        subprocess_info = TemplateRelationship.objects.get_subprocess_info(self.template_id).values(
            'descendant_template_id',
            'subprocess_node_id',
            'version'
        )
        info = {
            'subproc_has_update': False,
            'details': []
        }
        if not subprocess_info:
            return info

        # 2. check whether subprocess is expired
        temp_current_versions = {
            item.template_id: item for item in
            TemplateCurrentVersion.objects.filter(
                template_id__in=[item['descendant_template_id'] for item in subprocess_info])
        }

        expireds = []
        for item in subprocess_info:
            item['expired'] = False if item['version'] is None else \
                (item['version'] != temp_current_versions[item['descendant_template_id']].current_version)
            info['details'].append(item)
            expireds.append(item['expired'])

        info['subproc_has_update'] = any(expireds)

        # 3. return
        return info

    @property
    def subprocess_has_update(self):
        return self.subprocess_version_info['subproc_has_update']

    def data_for_version(self, version):
        """
        获取某个版本的模板数据
        @param version: 版本号
        @return: 模板数据
        """
        if not version:
            return self.data
        return Snapshot.objects.get(md5sum=version).data

    def referencer(self):
        """
        获取引用了该模板的其他模板
        @return: 引用了该模板的其他模板 ID 列表
        """
        referencer = TemplateRelationship.objects.referencer(self.template_id)
        template_id = self.__class__.objects.filter(template_id__in=referencer, is_deleted=False).values_list(
            'template_id', flat=True)
        return list(template_id)

    def clone_data(self):
        """
        获取该模板数据的克隆
        @return: ID 替换过后的模板数据
        """
        data = self.data
        replace_all_id(self.data)
        return data

    def update_template(self, structure_data, **kwargs):
        """
        更新当前模板的模板数据
        @param structure_data: pipeline 结构数据
        @param kwargs: 其他参数
        @return:
        """
        result, msg = PipelineTemplate.objects.subprocess_ref_validate(structure_data, self.template_id, self.name)
        if not result:
            raise SubprocessRefError(msg)

        snapshot, _ = Snapshot.objects.create_or_get_snapshot(structure_data)
        kwargs['snapshot'] = snapshot
        kwargs['edit_time'] = timezone.now()
        exclude_keys = ['template_id', 'creator', 'create_time', 'is_deleted']
        for key in exclude_keys:
            kwargs.pop(key, None)
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.save()

    def gen_instance(self, inputs=None, **kwargs):
        """
        使用该模板创建实例
        @param inputs: 自定义输入
        @param kwargs: 其他参数
        @return: 实例对象
        """
        return PipelineInstance.objects.create_instance(
            template=self,
            exec_data=copy.deepcopy(self.data),
            inputs=inputs,
            **kwargs
        )

    def set_has_subprocess_bit(self):
        acts = self.data[PE.activities].values()
        self.has_subprocess = any([act['type'] == PE.SubProcess for act in acts])


class TemplateRelationShipManager(models.Manager):
    def get_subprocess_info(self, template_id):
        """
        获取某个模板中所有的子流程信息
        @param template_id: 模板 ID
        @return: 该模板所引用的子流程相关信息
        """
        return self.filter(ancestor_template_id=template_id)

    def referencer(self, template_id):
        """
        获取引用了某个模板的其他模板
        @param template_id: 被引用的模板
        @return: 引用了该模板的其他模板 ID 列表
        """
        return list(set(self.filter(descendant_template_id=template_id).values_list('ancestor_template_id', flat=True)))


class TemplateRelationship(models.Model):
    """
    流程模板引用关系：直接引用
    """
    ancestor_template_id = models.CharField(_(u"根模板ID"), max_length=32, db_index=True)
    descendant_template_id = models.CharField(_(u"子流程模板ID"), max_length=32, null=False)
    subprocess_node_id = models.CharField(_(u"子流程节点 ID"), max_length=32, null=False)
    version = models.CharField(_(u"快照字符串的md5"), max_length=32, null=False)

    objects = TemplateRelationShipManager()


class TemplateCurrentVersionManager(models.Manager):
    def update_current_version(self, template):
        """
        更新某个模板的当前版本
        @param template: 模板对象
        @return: 记录模板当前版本的对象
        """
        obj, __ = self.update_or_create(template_id=template.template_id,
                                        defaults={
                                            'current_version': template.version
                                        })
        return obj


class TemplateCurrentVersion(models.Model):
    """
    记录流程模板当前版本的表
    """
    template_id = models.CharField(_(u"模板ID"), max_length=32, db_index=True)
    current_version = models.CharField(_(u"快照字符串的md5"), max_length=32, null=False)

    objects = TemplateCurrentVersionManager()


class TemplateVersionManager(models.Manager):
    def track(self, template):
        """
        记录模板的版本号
        @param template: 被记录模板
        @return: 版本跟踪对象
        """
        if not template.snapshot:
            return None

        # don't track if latest version is same as current version
        versions = self.filter(template_id=template.id).order_by('-id')
        if versions and versions[0].md5 == template.snapshot.md5sum:
            return versions[0]

        return self.create(template=template, snapshot=template.snapshot, md5=template.snapshot.md5sum)


class TemplateVersion(models.Model):
    """
    模板版本号记录节点
    """
    template = models.ForeignKey(PipelineTemplate, verbose_name=_(u"模板 ID"), null=False)
    snapshot = models.ForeignKey(Snapshot, verbose_name=_(u"模板数据 ID"), null=False)
    md5 = models.CharField(_(u"快照字符串的md5"), max_length=32, db_index=True)
    date = models.DateTimeField(_(u"添加日期"), auto_now_add=True)

    objects = TemplateVersionManager()


class TemplateScheme(models.Model):
    """
    模板执行方案
    """
    template = models.ForeignKey(PipelineTemplate, verbose_name=_(u"对应模板 ID"), null=False, blank=False)
    unique_id = models.CharField(_(u"方案唯一ID"), max_length=97, unique=True, null=False, blank=True)
    name = models.CharField(_(u"方案名称"), max_length=64, null=False, blank=False)
    edit_time = models.DateTimeField(_(u"修改时间"), auto_now=True)
    data = CompressJSONField(verbose_name=_(u"方案数据"))


class InstanceManager(models.Manager):

    def create_instance(self, template, exec_data, spread=False, inputs=None, **kwargs):
        """
        创建流程实例对象
        @param template: 流程模板
        @param exec_data: 执行用流程数据
        @param spread: exec_data 是否已经展开
        @param kwargs: 其他参数
        @param inputs: 自定义输入
        @return: 实例对象
        """
        if not spread:
            PipelineTemplate.objects.unfold_subprocess(exec_data)
        else:
            PipelineTemplate.objects.replace_id(exec_data)

        inputs = inputs or {}

        for key, val in inputs.items():
            if key in exec_data['data']['inputs']:
                exec_data['data']['inputs'][key]['value'] = val

        instance_id = node_uniqid()
        exec_data['id'] = instance_id
        exec_snapshot, _ = Snapshot.objects.create_or_get_snapshot(exec_data)
        TreeInfo.objects.create()
        kwargs['template'] = template
        kwargs['instance_id'] = instance_id
        kwargs['snapshot_id'] = template.snapshot.id
        kwargs['execution_snapshot_id'] = exec_snapshot.id
        return self.create(**kwargs)

    def delete_model(self, instance_ids):
        """
        删除流程实例对象
        @param instance_ids: 实例 ID 或 ID 列表
        @return:
        """
        if not isinstance(instance_ids, list):
            instance_ids = [instance_ids]
        qs = self.filter(instance_id__in=instance_ids)
        for instance in qs:
            instance.is_deleted = True
            instance.name = uniqid()
            instance.save()

    def set_started(self, instance_id, executor):
        """
        将实例的状态设置为已开始
        @param instance_id: 实例 ID
        @param executor: 执行者
        @return:
        """
        with transaction.atomic():
            instance = self.select_for_update().get(instance_id=instance_id)
            if instance.is_started:
                return False
            instance.start_time = timezone.now()
            instance.is_started = True
            instance.executor = executor
            instance.save()
        return True

    def set_finished(self, instance_id):
        """
        将实例的状态设置为已完成
        @param instance_id: 实例 ID
        @return:
        """
        with transaction.atomic():
            try:
                instance = self.select_for_update().get(instance_id=instance_id)
            except PipelineInstance.DoesNotExist:
                return None
            instance.finish_time = timezone.now()
            instance.is_finished = True
            instance.save()
        return instance


class PipelineInstance(models.Model):
    """
    流程实例对象
    """
    template = models.ForeignKey(PipelineTemplate, verbose_name=_(u"Pipeline模板"))
    instance_id = models.CharField(_(u"实例ID"), max_length=32, unique=True)
    name = models.CharField(_(u"实例名称"), max_length=MAX_LEN_OF_NAME, default='default_instance')
    creator = models.CharField(_(u"创建者"), max_length=32, blank=True)
    create_time = models.DateTimeField(_(u"创建时间"), auto_now_add=True)
    executor = models.CharField(_(u"执行者"), max_length=32, blank=True)
    start_time = models.DateTimeField(_(u"启动时间"), null=True, blank=True)
    finish_time = models.DateTimeField(_(u"结束时间"), null=True, blank=True)
    description = models.TextField(_(u"描述"), blank=True)
    is_started = models.BooleanField(_(u"是否已经启动"), default=False)
    is_finished = models.BooleanField(_(u"是否已经完成"), default=False)
    is_deleted = models.BooleanField(
        _(u"是否已经删除"),
        default=False,
        help_text=_(u"表示当前实例是否删除")
    )
    snapshot = models.ForeignKey(
        Snapshot,
        related_name='snapshot_instances',
        verbose_name=_(u"实例结构数据，指向实例对应的模板的结构数据")
    )
    execution_snapshot = models.ForeignKey(
        Snapshot,
        null=True,
        related_name='execution_snapshot_instances',
        verbose_name=_(u"用于实例执行的结构数据")
    )
    tree_info = models.ForeignKey(
        TreeInfo,
        null=True,
        related_name='tree_info_instances',
        verbose_name=_(u"提前计算好的一些流程结构数据")
    )

    objects = InstanceManager()

    class Meta:
        verbose_name = _(u"Pipeline实例")
        verbose_name_plural = _(u"Pipeline实例")
        ordering = ['-create_time']
        app_label = 'pipeline'

    def __unicode__(self):
        return '%s-%s' % (self.instance_id, self.name)

    @property
    def data(self):
        return self.snapshot.data

    @property
    def execution_data(self):
        return self.execution_snapshot.data

    @property
    def node_id_set(self):
        if not self.tree_info:
            self.calculate_tree_info(save=True)
        return self.tree_info.data['node_id_set']

    @property
    def elapsed_time(self):
        return calculate_elapsed_time(self.start_time, self.finish_time)

    def set_execution_data(self, data):
        """
        设置实例的执行用流程数据
        @param data: 执行用流程数据
        @return:
        """
        self.execution_snapshot.data = data
        self.execution_snapshot.save()

    def _replace_id(self, exec_data):
        """
        替换执行用流程数据中的所有 ID
        @param exec_data: 执行用流程数据
        @return:
        """
        replace_all_id(exec_data)
        activities = exec_data[PE.activities]
        for act_id, act in activities.items():
            if act[PE.type] == PE.SubProcess:
                self._replace_id(act['pipeline'])
                act['pipeline']['id'] = act_id

    def clone(self, creator, **kwargs):
        """
        返回当前实例对象的克隆
        @param creator: 创建者
        @param kwargs: 其他参数
        @return: 当前实例对象的克隆
        """
        name = kwargs.get('name') or timezone.localtime(timezone.now()).strftime('clone%Y%m%d%H%m%S')
        instance_id = node_uniqid()

        exec_data = self.execution_data
        self._replace_id(exec_data)
        # replace root id
        exec_data['id'] = instance_id
        new_snapshot, _ = Snapshot.objects.create_or_get_snapshot(exec_data)

        return self.__class__.objects.create(template=self.template, instance_id=instance_id,
                                             name=name, creator=creator,
                                             description=self.description, snapshot=self.snapshot,
                                             execution_snapshot=new_snapshot)

    def start(self, executor, check_workers=True):
        """
        启动当前流程
        @param executor: 执行者
        @param check_workers: 是否检测 worker 的状态
        @return: 执行结果
        """

        with transaction.atomic():
            instance = self.__class__.objects.select_for_update().get(id=self.id)
            if instance.is_started:
                return ActionResult(result=False, message='pipeline instance already started.')

            pipeline_data = instance.execution_data

            try:
                parser_cls = import_string(settings.PIPELINE_PARSER_CLASS)
            except ImportError:
                return ActionResult(result=False, message='invalid parser class: %s' % settings.PIPELINE_PARSER_CLASS)

            instance.start_time = timezone.now()
            instance.is_started = True
            instance.executor = executor

            parser = parser_cls(pipeline_data)
            pipeline = parser.parse(root_pipeline_data=get_pipeline_context(instance,
                                                                            obj_type='instance',
                                                                            data_type='data'),
                                    root_pipeline_context=get_pipeline_context(instance,
                                                                               obj_type='instance',
                                                                               data_type='context')
                                    )

            # calculate tree info
            instance.calculate_tree_info()

            instance.save()

        act_result = task_service.run_pipeline(pipeline)

        if not act_result.result:
            with transaction.atomic():
                instance = self.__class__.objects.select_for_update().get(id=self.id)
                instance.start_time = None
                instance.is_started = False
                instance.executor = ''
                instance.save()

        return act_result

    def _get_node_id_set(self, node_id_set, data):
        """
        递归获取当前实例中所有节点的 ID（包括子流程中的节点）
        @param node_id_set: 节点 ID 集合
        @param data: 流程数据
        @return:
        """
        node_id_set.add(data[PE.start_event]['id'])
        node_id_set.add(data[PE.end_event]['id'])
        for gid in data[PE.gateways]:
            node_id_set.add(gid)
        for aid, act_data in data[PE.activities].items():
            node_id_set.add(aid)
            if act_data[PE.type] == PE.SubProcess:
                self._get_node_id_set(node_id_set, act_data['pipeline'])

    def calculate_tree_info(self, save=False):
        """
        计算当前流程实例执行用流程数据中的一些基本信息
        @param save: 是否在计算完后保存实例对象
        @return:
        """
        self.tree_info = TreeInfo.objects.create()
        node_id_set = set({})

        # get node id set
        self._get_node_id_set(node_id_set, self.execution_data)

        tree_info = {
            'node_id_set': node_id_set
        }
        self.tree_info.data = tree_info
        self.tree_info.save()

        if save:
            self.save()
