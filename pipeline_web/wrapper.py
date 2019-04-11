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
import hashlib
import copy
import ujson as json

from pipeline.core.constants import PE
from pipeline.utils.uniqid import uniqid
from pipeline.parser.utils import replace_all_id
from pipeline.models import PipelineTemplate, Snapshot
from pipeline.exceptions import SubprocessExpiredError


class PipelineTemplateWebWrapper(object):
    SERIALIZE_DATE_FORMAT = '%Y-%m-%d %H:%M:%S %Z'
    ID_MAP_KEY = 'id_to_id'

    def __init__(self, template):
        self.template = template

    def get_form(self, version=None):
        """
        获取模板中用于渲染前端表单的变量
        @param version: 模板版本
        @return: 用于渲染表单的变量信息
        """
        data = self.template.data_for_version(version)

        form = {}
        for key, var_info in data['constants'].items():
            if var_info['show_type'] == 'show':
                form[key] = var_info
        return form

    def get_outputs(self, version=None):
        """
        获取模板的所有输出参数
        @param version: 模板版本
        @return: 输出参数信息
        """
        data = self.template.data_for_version(version)

        if 'constants' not in data:
            return {}

        outputs_key = data['outputs']
        outputs = {}
        for key in outputs_key:
            if key in data['constants']:
                outputs[key] = data['constants'][key]
        return outputs

    @classmethod
    def unfold_subprocess(cls, pipeline_data):
        """
        展开 pipeline 数据中所有的子流程
        @param pipeline_data: pipeline 数据
        @return:
        """
        replace_all_id(pipeline_data)
        activities = pipeline_data[PE.activities]
        for act_id, act in activities.items():
            if act[PE.type] == PE.SubProcess:
                subproc_data = PipelineTemplate.objects.get(template_id=act['template_id']) \
                    .data_for_version(act.get('version'))

                if 'constants' in pipeline_data:
                    constants_inputs = act.pop('constants')
                    # replace show constants with inputs
                    for key, info in constants_inputs.items():
                        if 'form' in info:
                            info.pop('form')
                        subproc_data['constants'][key] = info

                cls.unfold_subprocess(subproc_data)

                subproc_data['id'] = act_id
                act['pipeline'] = subproc_data

    @classmethod
    def _export_template(cls, template_id, subprocess, refs, root=True):
        """
        导出模板 wrapper 函数
        @param template_id: 需要导出的模板 id
        @param subprocess: 子流程记录字典
        @param refs: 引用关系记录字典: 被引用模板 -> 引用模板 -> 引用节点
        @param root: 是否是根模板
        @return: 模板数据，模板引用的子流程数据，引用关系
        """
        template_obj = PipelineTemplate.objects.get(template_id=template_id)
        if template_obj.subprocess_has_update:
            raise SubprocessExpiredError(
                'template %s has expired subprocess, please update it before exporting.' % template_obj.name)
        template = {
            'create_time': template_obj.create_time.strftime(cls.SERIALIZE_DATE_FORMAT),
            'edit_time': template_obj.edit_time.strftime(cls.SERIALIZE_DATE_FORMAT),
            'creator': template_obj.creator,
            'description': template_obj.description,
            'editor': template_obj.editor,
            'is_deleted': template_obj.is_deleted,
            'name': template_obj.name,
            'template_id': template_obj.template_id
        }
        tree = template_obj.data

        for act_id, act in tree[PE.activities].items():
            if act[PE.type] == PE.SubProcess:
                # record referencer id
                # referenced template -> referencer -> reference act
                refs.setdefault(act['template_id'], {}) \
                    .setdefault(template['template_id'], set()) \
                    .add(act_id)
                cls._export_template(act['template_id'], subprocess, refs, False)

        template['tree'] = tree
        if not root:
            subprocess[template['template_id']] = template
            return

        return template, subprocess, refs

    @classmethod
    def export_templates(cls, template_id_list):
        """
        导出模板接口
        @param template_id_list: 需要导出的模板 id 列表
        @return: 模板数据
        """
        data = {
            'template': {},
            'refs': {}
        }
        for template_id in template_id_list:
            template, subprocess, refs = cls._export_template(template_id, {}, {})
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

    @classmethod
    def _kwargs_for_template_dict(cls, template_dict, include_str_id):
        """
        根据模板数据字典返回创建模板所需的关键字参数
        @param template_dict: 模板数据字典
        @param include_str_id: 数据中是否包括模板 ID
        @return: 关键字参数字典
        """
        snapshot, __ = Snapshot.objects.create_or_get_snapshot(template_dict['tree'])
        defaults = {
            'name': template_dict['name'],
            'create_time': datetime.datetime.strptime(template_dict['create_time'],
                                                      cls.SERIALIZE_DATE_FORMAT),
            'creator': template_dict['creator'],
            'description': template_dict['description'],
            'editor': template_dict['editor'],
            'edit_time': datetime.datetime.strptime(template_dict['edit_time'],
                                                    cls.SERIALIZE_DATE_FORMAT),
            'snapshot': snapshot
        }
        if include_str_id:
            defaults['template_id'] = template_dict['template_id']

        return defaults

    @classmethod
    def _update_order_from_refs(cls, refs, id_maps=None):
        """
        根据模板间的引用关系返回模板数据的更新顺序
        @param refs: 引用关系字典
        @param id_maps: 模板 ID 映射表
        @return: 返回权重由大至小的模板 ID 序列
        """
        id_maps = id_maps or {}
        forward_refs = {}
        for be_referenced, referencers in refs.items():
            for r in referencers:
                forward_refs.setdefault(id_maps.get(r, r), []).append(id_maps.get(be_referenced, be_referenced))

        referenced_weight = {}
        for referencer, be_referenced in forward_refs.items():
            referenced_weight.setdefault(referencer, 0)
            # 引用者权重 -1
            referenced_weight[referencer] -= 1
            for ref in be_referenced:
                referenced_weight.setdefault(ref, 0)
                # 被引用者权重 +1
                referenced_weight[ref] += 1

        return [i[0] for i in sorted(referenced_weight.items(), cmp=lambda x, y: cmp(x[1], y[1]), reverse=True)]

    @classmethod
    def _update_or_create_version(cls, template, order):
        """
        根据传入的顺序更新子流程引用模板的版本
        @param template: 模板数据字典
        @param order: 更新顺序
        @return:
        """
        for tid in order:
            for act_id, act in template[tid]['tree'][PE.activities].items():
                if act[PE.type] == PE.SubProcess:
                    subprocess_data = template[act['template_id']]['tree']
                    h = hashlib.md5()
                    h.update(json.dumps(subprocess_data))
                    md5sum = h.hexdigest()
                    act['version'] = md5sum

    @classmethod
    def import_templates(cls, template_data, override=False, tid_to_reuse=None):
        """
        导入模板数据
        @param template_data: 模板数据
        @param override: 是否复用数据中的模板 ID
        @param tid_to_reuse: 能够重用的模板 ID
        @return: 模板导入后模板数据旧 ID -> 新 ID 的映射
        """
        template_data_copy = copy.deepcopy(template_data)

        template = template_data_copy['template']
        refs = template_data_copy['refs']

        temp_id_old_to_new = {}

        if not override:
            template_id_list = template.keys()
            exist_str_id = PipelineTemplate.objects.filter(template_id__in=template_id_list).values_list('template_id',
                                                                                                         flat=True)
            old_id_list = template.keys()
            template_node_id_old_to_new = {}

            # replace id
            if exist_str_id:

                # 1st round: replace template id
                for tid in exist_str_id:
                    old_template_id = tid
                    new_template_id = uniqid()
                    temp_id_old_to_new[old_template_id] = new_template_id

                    # update subprocess template id
                    for referencer_id, act_ids in refs.get(tid, {}).items():
                        for act_id in act_ids:
                            template[referencer_id]['tree'][PE.activities][act_id]['template_id'] = new_template_id

                # 2nd round: replace all node id
                for tid in exist_str_id:
                    temp = template[tid]
                    new_id = temp_id_old_to_new[temp['template_id']]
                    temp['template_id'] = new_id
                    node_id_maps = replace_all_id(temp['tree'])
                    template_node_id_old_to_new[new_id] = node_id_maps
                    # replace subprocess constants field
                    for referencer_id, act_ids in refs.get(tid, {}).items():
                        # can not sure parent id is replaced or not
                        new_referencer_id = temp_id_old_to_new[referencer_id]
                        referencer_id = new_referencer_id if referencer_id not in template else referencer_id
                        for act_id in act_ids:
                            # can not sure parent node id is replaced or not
                            act_id = template_node_id_old_to_new.get(referencer_id, {}).get('activity', {}).get(
                                act_id,
                                act_id)
                            constant_dict = template[referencer_id]['tree'][PE.activities][act_id].get('constants',
                                                                                                       {})
                            for key, constant in constant_dict.items():
                                source_info = constant['source_info']
                                source_id_list = source_info.keys()
                                for old_source_id in source_id_list:
                                    new_source_id = node_id_maps['activity'][old_source_id]
                                    source_info[new_source_id] = source_info.pop(old_source_id)
                    template[new_id] = template.pop(tid)

            # add id which do not conflict
            for old_id in old_id_list:
                if old_id not in temp_id_old_to_new:
                    temp_id_old_to_new[old_id] = old_id

            cls._update_or_create_version(template, cls._update_order_from_refs(refs, temp_id_old_to_new))

            # import template
            for tid, template_dict in template.items():
                defaults = cls._kwargs_for_template_dict(template_dict, include_str_id=True)
                PipelineTemplate.objects.create(**defaults)
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

            cls._update_or_create_version(template, cls._update_order_from_refs(refs, tid_to_reuse))

            # override
            for tid, template_dict in template.items():
                defaults = cls._kwargs_for_template_dict(template_dict, include_str_id=False)

                PipelineTemplate.objects.update_or_create(template_id=tid,
                                                          defaults=defaults)
                temp_id_old_to_new[template_dict.get('old_id', tid)] = tid

        return {
            cls.ID_MAP_KEY: temp_id_old_to_new,
        }


class PipelineInstanceWebWrapper(object):
    def __init__(self, instance):
        self.instance = instance
