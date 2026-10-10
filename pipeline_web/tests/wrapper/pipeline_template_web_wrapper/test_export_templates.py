# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import datetime

from mock import MagicMock, patch

from django.test import TestCase

from pipeline_web.wrapper import PipelineTemplateWebWrapper


class FakePipelineTemplate(object):
    """测试用流程模板对象"""

    def __init__(self, template_id, name, version, tree):
        self.id = 1
        self.template_id = template_id
        self.name = name
        self.version = version
        self.data = tree
        self.create_time = datetime.datetime(2020, 1, 1)
        self.edit_time = datetime.datetime(2020, 1, 1)
        self.creator = "admin"
        self.editor = "admin"
        self.description = ""
        self.is_deleted = False


def subprocess_tree(node_id, subprocess_template_id, version, always_use_latest=False):
    act = {
        "id": node_id,
        "type": "SubProcess",
        "name": node_id,
        "template_id": subprocess_template_id,
        "version": version,
    }
    if always_use_latest:
        act["always_use_latest"] = True
    return {"activities": {node_id: act}, "constants": {}, "outputs": []}


class ExportTemplatesTestCase(TestCase):
    def setUp(self):
        self.maxDiff = None
        self.subprocess_tree_v1 = {"activities": {}, "constants": {"${v}": {"value": 1}}, "outputs": []}
        self.subprocess_tree_v2 = {"activities": {}, "constants": {"${v}": {"value": 2}}, "outputs": []}
        self.subprocess = FakePipelineTemplate("subproc", "S", "subprocess_version_v2", self.subprocess_tree_v2)

    def _export(self, template_objs):
        snapshots = {
            "subprocess_version_v1": MagicMock(data=self.subprocess_tree_v1),
            "subprocess_version_v2": MagicMock(data=self.subprocess_tree_v2),
        }

        def snapshot_filter(md5sum=None, **kwargs):
            chain = MagicMock()
            chain.order_by.return_value.first.return_value = snapshots.get(md5sum)
            return chain

        snapshot_mock = MagicMock()
        snapshot_mock.objects.filter = MagicMock(side_effect=snapshot_filter)

        pipeline_template_mock = MagicMock()
        pipeline_template_mock.objects.filter.return_value.select_related.return_value = template_objs
        pipeline_template_mock.objects.get = MagicMock(return_value=self.subprocess)

        with patch.multiple(
            "pipeline_web.wrapper",
            PipelineWebTreeCleaner=MagicMock(),
            NodeAttr=MagicMock(),
            NodeInTemplate=MagicMock(),
            TemplateScheme=MagicMock(),
            Snapshot=snapshot_mock,
            PipelineTemplate=pipeline_template_mock,
        ):
            return PipelineTemplateWebWrapper.export_templates([template.template_id for template in template_objs])

    def test_export_multi_version_subprocess(self):
        """同一子流程被引用到不同版本时，两个版本都需要被导出"""
        root_a = FakePipelineTemplate(
            "root_a", "A", "root_a_version", subprocess_tree("node_1", "subproc", "subprocess_version_v1")
        )
        root_b = FakePipelineTemplate(
            "root_b", "B", "root_b_version", subprocess_tree("node_2", "subproc", "subprocess_version_v2")
        )

        data = self._export([root_a, root_b])
        templates = data["template"]

        # 两个根流程 + 同一子流程的两个版本
        self.assertEqual(len(templates), 4)
        self.assertIn("root_a", templates)
        self.assertIn("root_b", templates)
        self.assertIn("subproc", templates)
        subprocess_keys = [key for key in templates if key not in ("root_a", "root_b", "subproc")]
        self.assertEqual(len(subprocess_keys), 1)
        multi_version_key = subprocess_keys[0]

        # 导出键会作为导入时的模板 ID 使用，长度不能超过 32
        self.assertLessEqual(len(multi_version_key), 32)

        # 两个版本的内容都被保留，且都能对应回原始模板 ID
        self.assertDictEqual(templates["subproc"]["tree"], self.subprocess_tree_v1)
        self.assertDictEqual(templates[multi_version_key]["tree"], self.subprocess_tree_v2)
        self.assertEqual(templates["subproc"]["template_id"], "subproc")
        self.assertEqual(templates[multi_version_key]["template_id"], "subproc")

        # 父流程节点分别指向自己引用的子流程版本
        self.assertEqual(templates["root_a"]["tree"]["activities"]["node_1"]["template_id"], "subproc")
        self.assertEqual(templates["root_b"]["tree"]["activities"]["node_2"]["template_id"], multi_version_key)

        # 引用关系与流程导出键保持一致
        self.assertDictEqual(data["refs"]["subproc"], {"root_a": ["node_1"]})
        self.assertDictEqual(data["refs"][multi_version_key], {"root_b": ["node_2"]})

    def test_export_same_version_subprocess(self):
        """多个父流程引用同一子流程的同一版本时，只导出一份，导出键沿用模板 ID"""
        root_a = FakePipelineTemplate(
            "root_a", "A", "root_a_version", subprocess_tree("node_1", "subproc", "subprocess_version_v2")
        )
        root_b = FakePipelineTemplate(
            "root_b", "B", "root_b_version", subprocess_tree("node_2", "subproc", "subprocess_version_v2")
        )

        data = self._export([root_a, root_b])

        # 顶层流程位于其子流程之前，子流程只有一份
        self.assertEqual(list(data["template"].keys()), ["root_a", "subproc", "root_b"])
        self.assertDictEqual(data["refs"]["subproc"], {"root_a": ["node_1"], "root_b": ["node_2"]})

    def test_export_subprocess_without_version(self):
        """子流程节点未指定版本（总是使用最新版本）时，导出子流程的最新版本"""
        root_a = FakePipelineTemplate(
            "root_a",
            "A",
            "root_a_version",
            subprocess_tree("node_1", "subproc", "subprocess_version_v1", always_use_latest=True),
        )

        data = self._export([root_a])

        self.assertEqual(list(data["template"].keys()), ["root_a", "subproc"])
        self.assertDictEqual(data["template"]["subproc"]["tree"], self.subprocess_tree_v2)
        self.assertEqual(data["template"]["root_a"]["tree"]["activities"]["node_1"]["template_id"], "subproc")
