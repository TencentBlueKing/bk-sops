# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
""" # noqa
from __future__ import absolute_import

import Queue
import ujson as json
import zlib
import hashlib
import logging
import datetime
import copy

from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.db import models, transaction

from pipeline.utils.uniqid import uniqid, node_uniqid
from pipeline.parser.utils import replace_all_id
from pipeline.utils.graph import Graph
from pipeline.exceptions import SubprocessRefError, SubprocessExpiredError
from pipeline.engine.utils import calculate_elapsed_time
from pipeline.core.constants import PE

MAX_LEN_OF_NAME = 64
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
        h = hashlib.md5()
        h.update(json.dumps(data))
        md5 = h.hexdigest()
        return md5, self.md5sum != md5


class TreeInfo(models.Model):
    data = CompressJSONField(null=True, blank=True)


def get_subprocess_act_list(pipeline_data):
    activities = pipeline_data['activities']
    act_ids = filter(lambda act_id: activities[act_id]['type'] == 'SubProcess', activities)
    return [activities[act_id] for act_id in act_ids]


class TemplateManager(models.Manager):
    SERIALIZE_DATE_FORMAT = '%Y-%m-%d %H:%M:%S %Z'

    def subprocess_ref_validate(self, data, root_id=None, root_name=None):
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
            name_trace = u' → '.join(map(lambda proc_id: name_map[proc_id], trace))
            return False, _(u"子流程引用链中存在循环引用：%s") % name_trace

        return True, ''

    def create_model(self, structure_data, **kwargs):
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
        if not isinstance(template_ids, list):
            template_ids = [template_ids]
        qs = self.filter(template_id__in=template_ids)
        for template in qs:
            template.is_deleted = True
            template.name = uniqid()
            template.save()

    def _act_id_in_graph(self, act):
        return '%s:%s' % (act['template_id'], act['version']) if act.get('version') else act['template_id']

    def construct_subprocess_ref_graph(self, pipeline_data, root_id=None, root_name=None):
        subprocess_act = get_subprocess_act_list(pipeline_data)
        tid_queue = Queue.Queue()
        graph = {}
        version = {}
        name_map = {}

        if root_id:
            graph[root_id] = [self._act_id_in_graph(act) for act in subprocess_act]
            name_map[root_id] = root_name

        for act in subprocess_act:
            tid_queue.put(self._act_id_in_graph(act))
            version[self._act_id_in_graph(act)] = act.get('version')

        while not tid_queue.empty():
            tid = tid_queue.get()
            template = self.get(template_id=tid.split(':')[0])
            name_map[tid] = template.name
            subprocess_act = get_subprocess_act_list(template.data_for_version(version[tid]))

            for act in subprocess_act:
                ref_tid = self._act_id_in_graph(act)
                graph.setdefault(tid, []).append(ref_tid)
                version[self._act_id_in_graph(act)] = act.get('version')
                if ref_tid not in graph:
                    tid_queue.put(ref_tid)
            if not subprocess_act:
                graph[tid] = []

        return graph, name_map

    def _export_template(self, template_id, subprocess, refs, root=True):
        template_obj = self.get(template_id=template_id)
        if template_obj.subprocess_has_update:
            raise SubprocessExpiredError(
                'template %s has expired subprocess, please update it before exporting.' % template_obj.name)
        template = {
            'create_time': template_obj.create_time.strftime(self.SERIALIZE_DATE_FORMAT),
            'edit_time': template_obj.edit_time.strftime(self.SERIALIZE_DATE_FORMAT),
            'creator': template_obj.creator,
            'description': template_obj.description,
            'editor': template_obj.editor,
            'is_deleted': template_obj.is_deleted,
            'name': template_obj.name,
            'template_id': template_obj.template_id
        }
        tree = template_obj.data

        for act_id, act in tree['activities'].iteritems():
            if act['type'] == PE.SubProcess:
                # record referencer id
                # referenced template -> referencer -> reference act
                refs.setdefault(act['template_id'], {}) \
                    .setdefault(template['template_id'], set()) \
                    .add(act_id)
                self._export_template(act['template_id'], subprocess, refs, False)

        template['tree'] = tree
        if not root:
            subprocess[template['template_id']] = template
            return

        return template, subprocess, refs

    def export_templates(self, template_id_list):
        data = {
            'template': {},
            'refs': {}
        }
        for template_id in template_id_list:
            template, subprocess, refs = self._export_template(template_id, {}, {})
            data['template'][template['template_id']] = template
            data['template'].update(subprocess)
            for be_ref, ref_info in refs.items():
                for tmp_key, nodes in ref_info.items():
                    data['refs'].setdefault(be_ref, ref_info) \
                        .setdefault(tmp_key, nodes) \
                        .update(nodes)
        # convert set to list
        for be_ref, ref_info in data['refs'].items():
            for tmp_key in ref_info:
                data['refs'][be_ref][tmp_key] = list(data['refs'][be_ref][tmp_key])

        return data

    def _kwargs_for_template_dict(self, template_dict, include_str_id):
        snapshot, __ = Snapshot.objects.create_or_get_snapshot(template_dict['tree'])
        defaults = {
            'name': template_dict['name'],
            'create_time': datetime.datetime.strptime(template_dict['create_time'],
                                                      self.SERIALIZE_DATE_FORMAT),
            'creator': template_dict['creator'],
            'description': template_dict['description'],
            'editor': template_dict['editor'],
            'edit_time': datetime.datetime.strptime(template_dict['edit_time'],
                                                    self.SERIALIZE_DATE_FORMAT),
            'snapshot': snapshot
        }
        if include_str_id:
            defaults['template_id'] = template_dict['template_id']

        return defaults

    def _update_order_from_refs(self, refs, id_maps=None):
        id_maps = id_maps or {}
        forward_refs = {}
        for be_referenced, referencers in refs.items():
            for r in referencers:
                forward_refs.setdefault(id_maps.get(r, r), []).append(id_maps.get(be_referenced, be_referenced))

        referenced_weight = {}
        for referencer, be_referenced in forward_refs.items():
            referenced_weight.setdefault(referencer, 0)
            referenced_weight[referencer] -= 1
            for ref in be_referenced:
                referenced_weight.setdefault(ref, 0)
                referenced_weight[ref] += 1

        return [i[0] for i in sorted(referenced_weight.items(), cmp=lambda x, y: cmp(x[1], y[1]), reverse=True)]

    def _update_or_create_version(self, template, order):
        for tid in order:
            for act_id, act in template[tid]['tree'][PE.activities].items():
                if act['type'] == PE.SubProcess:
                    subprocess_data = template[act['template_id']]['tree']
                    h = hashlib.md5()
                    h.update(json.dumps(subprocess_data))
                    md5sum = h.hexdigest()
                    act['version'] = md5sum

    def import_templates(self, template_data, override=False, tid_to_reuse=None):
        template_data_copy = copy.deepcopy(template_data)

        template = template_data_copy['template']
        refs = template_data_copy['refs']

        temp_id_old_to_new = {}

        if not override:
            template_id_list = template.keys()
            exist_str_id = self.filter(template_id__in=template_id_list).values_list('template_id', flat=True)
            old_id_list = template.keys()

            # replace id
            if exist_str_id:

                # 1st round: replace template id
                for tid in exist_str_id:
                    old_template_id = tid
                    new_template_id = uniqid()
                    temp_id_old_to_new[old_template_id] = new_template_id

                    # update subprocess template id
                    for referencer_id, act_ids in refs.get(tid, {}).iteritems():
                        for act_id in act_ids:
                            template[referencer_id]['tree']['activities'][act_id]['template_id'] = new_template_id

                # 2nd round: replace all node id
                for tid in exist_str_id:
                    temp = template[tid]
                    new_id = temp_id_old_to_new[temp['template_id']]
                    temp['template_id'] = new_id
                    replace_all_id(temp['tree'])
                    template[new_id] = template.pop(tid)

            # add id which do not conflict
            for old_id in old_id_list:
                if old_id not in temp_id_old_to_new:
                    temp_id_old_to_new[old_id] = old_id

            self._update_or_create_version(template, self._update_order_from_refs(refs, temp_id_old_to_new))

            # import template
            for tid, template_dict in template.items():
                defaults = self._kwargs_for_template_dict(template_dict, include_str_id=True)
                self.create(**defaults)
        else:

            # 1. replace subprocess template id
            tid_to_reuse = tid_to_reuse or {}
            for import_id, reuse_id in tid_to_reuse.items():
                # referenced template -> referencer -> reference act
                referencer_info_dict = refs.get(import_id, {})
                for referencer, nodes in referencer_info_dict.items():
                    for node_id in nodes:
                        template[referencer]['tree'][PE.activities][node_id]['template_id'] = reuse_id

            # 2. replace template id
            # use new dict to prevent override in template_id exchange
            new_template = {}
            for import_id, reuse_id in tid_to_reuse.items():
                temp = template.pop(import_id)
                temp['template_id'] = reuse_id
                temp['old_id'] = import_id
                new_template[reuse_id] = temp
            # add rest template
            new_template.update(template)
            template = new_template

            self._update_or_create_version(template, self._update_order_from_refs(refs, tid_to_reuse))

            # override
            for tid, template_dict in template.items():
                defaults = self._kwargs_for_template_dict(template_dict, include_str_id=False)

                self.update_or_create(template_id=tid,
                                      defaults=defaults)
                temp_id_old_to_new[template_dict.get('old_id', tid)] = tid

        return {
            self.model.ID_MAP_KEY: temp_id_old_to_new,
        }


class PipelineTemplate(models.Model):
    template_id = models.CharField(_(u'模板ID'), max_length=32, unique=True)
    name = models.CharField(_(u'模板名称'), max_length=MAX_LEN_OF_NAME, default='default_template')
    create_time = models.DateTimeField(_(u'创建时间'), auto_now_add=True)
    creator = models.CharField(_(u'创建者'), max_length=32)
    description = models.TextField(_(u'描述'), null=True, blank=True)
    editor = models.CharField(_(u'修改者'), max_length=32, null=True, blank=True)
    edit_time = models.DateTimeField(_(u'修改时间'), auto_now=True)
    snapshot = models.ForeignKey(Snapshot, verbose_name=_(u'模板结构数据'))
    is_deleted = models.BooleanField(
        _(u'是否删除'),
        default=False,
        help_text=_(u'表示当前模板是否删除')
    )

    objects = TemplateManager()

    ID_MAP_KEY = 'id_to_id'

    class Meta:
        verbose_name = _(u'Pipeline模板')
        verbose_name_plural = _(u'Pipeline模板')
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
        if not version:
            return self.data
        return Snapshot.objects.get(md5sum=version).data

    def clone_data(self):
        data = self.data
        replace_all_id(self.data)
        return data

    def update_template(self, structure_data, **kwargs):
        result, msg = PipelineTemplate.objects.subprocess_ref_validate(structure_data, self.template_id, self.name)
        if not result:
            raise SubprocessRefError(msg)

        snapshot, _ = Snapshot.objects.create_or_get_snapshot(structure_data)
        kwargs['snapshot'] = snapshot
        kwargs['edit_time'] = timezone.now()
        exclude_keys = ['template_id', 'creator', 'create_time', 'is_deleted']
        for key in exclude_keys:
            kwargs.pop(key, None)
        for key, value in kwargs.iteritems():
            setattr(self, key, value)
        self.save()
        # version track
        # TemplateVersion.objects.track(self)

    def get_form(self, version=None):
        data = self.data_for_version(version)
        form = {}
        for key, var_info in data['constants'].iteritems():
            if var_info['show_type'] == 'show':
                form[key] = var_info
        return form

    def get_outputs(self):
        data = self.data
        outputs_key = data['outputs']
        outputs = {}
        for key in outputs_key:
            if key in data['constants']:
                outputs[key] = data['constants'][key]
        return outputs


class TemplateRelationShipManager(models.Manager):
    def get_subprocess_info(self, template_id):
        return self.filter(ancestor_template_id=template_id)


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
        obj, __ = self.update_or_create(template_id=template.template_id,
                                        defaults={
                                            'current_version': template.version
                                        })
        return obj


class TemplateCurrentVersion(models.Model):
    template_id = models.CharField(_(u"模板ID"), max_length=32, db_index=True)
    current_version = models.CharField(_(u"快照字符串的md5"), max_length=32, null=False)

    objects = TemplateCurrentVersionManager()


class TemplateVersionManager(models.Manager):
    def track(self, template):
        if not template.snapshot:
            return None

        # don't track if latest version is same as current version
        versions = self.filter(template_id=template.id).order_by('-id')
        if versions and versions[0].md5 == template.snapshot.md5sum:
            return versions[0]

        return self.create(template=template, snapshot=template.snapshot, md5=template.snapshot.md5sum)

    def _track_old_templates(self):
        templates = PipelineTemplate.objects.all()
        for t in templates:
            self.track(t)


class TemplateVersion(models.Model):
    template = models.ForeignKey(PipelineTemplate, verbose_name=_(u"模板 ID"), null=False)
    snapshot = models.ForeignKey(Snapshot, verbose_name=_(u"模板数据 ID"), null=False)
    md5 = models.CharField(_(u"快照字符串的md5"), max_length=32, db_index=True)
    date = models.DateTimeField(_(u"添加日期"), auto_now_add=True)

    objects = TemplateVersionManager()


class TemplateScheme(models.Model):
    template = models.ForeignKey(PipelineTemplate, verbose_name=_(u"对应模板 ID"), null=False, blank=False)
    unique_id = models.CharField(_(u"方案唯一ID"), max_length=97, unique=True, null=False, blank=True)
    name = models.CharField(_(u"方案名称"), max_length=64, null=False, blank=False)
    edit_time = models.DateTimeField(_(u"修改时间"), auto_now=True)
    data = CompressJSONField(verbose_name=_(u"方案数据"))


def unfold_subprocess(pipeline_data):
    replace_all_id(pipeline_data)
    activities = pipeline_data['activities']
    for act_id, act in activities.iteritems():
        if act['type'] == 'SubProcess':
            subproc_data = PipelineTemplate.objects.get(template_id=act['template_id']) \
                .data_for_version(act.get('version'))
            constants_inputs = act.pop('constants')
            # replace show constants with inputs
            for key, info in constants_inputs.iteritems():
                if 'form' in info:
                    info.pop('form')
                subproc_data['constants'][key] = info
            unfold_subprocess(subproc_data)

            subproc_data['id'] = act_id
            act['pipeline'] = subproc_data


class InstanceManager(models.Manager):

    def create_instance(self, template, exec_data, **kwargs):
        unfold_subprocess(exec_data)
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
        if not isinstance(instance_ids, list):
            instance_ids = [instance_ids]
        qs = self.filter(instance_id__in=instance_ids)
        for instance in qs:
            instance.is_deleted = True
            instance.name = uniqid()
            instance.save()

    def set_started(self, instance_id, executor):
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
    template = models.ForeignKey(PipelineTemplate, verbose_name=_(u'Pipeline模板'))
    instance_id = models.CharField(_(u'实例ID'), max_length=32, unique=True)
    name = models.CharField(_(u'实例名称'), max_length=MAX_LEN_OF_NAME, default='default_instance')
    creator = models.CharField(_(u'创建者'), max_length=32, blank=True)
    create_time = models.DateTimeField(_(u'创建时间'), auto_now_add=True)
    executor = models.CharField(_(u'执行者'), max_length=32, blank=True)
    start_time = models.DateTimeField(_(u'启动时间'), null=True, blank=True)
    finish_time = models.DateTimeField(_(u'结束时间'), null=True, blank=True)
    description = models.TextField(_(u'描述'), blank=True)
    is_started = models.BooleanField(_(u'是否已经启动'), default=False)
    is_finished = models.BooleanField(_(u'是否已经完成'), default=False)
    is_deleted = models.BooleanField(
        _(u'是否已经删除'),
        default=False,
        help_text=_(u'表示当前实例是否删除')
    )
    snapshot = models.ForeignKey(
        Snapshot,
        related_name='snapshot',
        verbose_name=_(u'实例结构数据')
    )
    execution_snapshot = models.ForeignKey(
        Snapshot,
        null=True,
        related_name='execution_snapshot',
        verbose_name=_(u'用于实例执行的结构数据')
    )
    tree_info = models.ForeignKey(
        TreeInfo,
        null=True,
        related_name='tree_info',
        verbose_name=_(u'提前计算好的一些流程结构数据')
    )

    objects = InstanceManager()

    class Meta:
        verbose_name = _(u'Pipeline实例')
        verbose_name_plural = _(u'Pipeline实例')
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
        self.execution_snapshot.data = data
        self.execution_snapshot.save()

    def _replace_id(self, exec_data):
        replace_all_id(exec_data)
        activities = exec_data['activities']
        for act_id, act in activities.iteritems():
            if act['type'] == 'SubProcess':
                self._replace_id(act['pipeline'])
                act['pipeline']['id'] = act_id

    def clone(self, creator):
        # name = self.name[10:] if len(self.name) >= MAX_LEN_OF_NAME - 10 else self.name
        name = timezone.now().strftime('clone%Y%m%d%H%m%S')
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

    def start(self, executor):
        from pipeline.parser import pipeline_parser
        from pipeline.engine import api
        from pipeline.utils.context import get_pipeline_context
        from pipeline.engine.models import FunctionSwitch
        if FunctionSwitch.objects.is_frozen():
            return False, 'engine has been freeze, try later please'

        with transaction.atomic():
            instance = self.__class__.objects.select_for_update().get(id=self.id)
            if instance.is_started:
                return False, 'pipeline instance already started.'
            instance.start_time = timezone.now()
            instance.is_started = True
            instance.executor = executor

            # calculate tree info
            instance.calculate_tree_info()

            pipeline_data = instance.execution_data
            parser = pipeline_parser.WebPipelineAdapter(pipeline_data)
            pipeline = parser.parser(get_pipeline_context(instance, 'instance'))

            instance.save()

        api.start_pipeline(pipeline)

        return True, {}

    def _get_node_id_set(self, node_id_set, data):
        node_id_set.add(data['start_event']['id'])
        node_id_set.add(data['end_event']['id'])
        for gid in data['gateways']:
            node_id_set.add(gid)
        for aid, act_data in data['activities'].iteritems():
            node_id_set.add(aid)
            if act_data['type'] == 'SubProcess':
                self._get_node_id_set(node_id_set, act_data['pipeline'])

    def calculate_tree_info(self, save=False):
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


class VariableModel(models.Model):
    """
    注册的变量
    """
    code = models.CharField(_(u"变量编码"), max_length=255, unique=True)
    status = models.BooleanField(_(u"变量是否可用"), default=True)

    class Meta:
        verbose_name = _(u"Variable变量")
        verbose_name_plural = _(u"Variable变量")
        ordering = ['-id']
        app_label = 'pipeline'

    def __unicode__(self):
        return self.code
