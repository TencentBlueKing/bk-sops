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

from django.test import TestCase

from gcloud.template_base.models import BaseTemplateManager
from gcloud.tests.mock import *  # noqa
from gcloud.tests.mock_settings import *  # noqa
from pipeline_web.wrapper import PipelineTemplateWebWrapper


def _biz_record(tid, pipeline_template_id, name="t"):
    return {
        "category": "Default",
        "executor_proxy": "",
        "id": tid,
        "notify_type": '{"success":[],"fail":[]}',
        "pipeline_template_id": pipeline_template_id,
        "pipeline_template_str_id": pipeline_template_id,
        "project_id": 1,
        "time_out": 20,
        "name": name,
    }


class FakeQS(list):
    """模拟 queryset，支持 select_related / values 链式调用"""

    def select_related(self, *args, **kwargs):
        return self

    def values(self, *args, **kwargs):
        return self


class ExportMultiVersionSubprocessTest(TestCase):
    """覆盖 BaseTemplateManager.export_templates 中「多版本子流程导出键 -> 原始模板 ID」的新增逻辑。

    本次改动把收集「所有模板 ID」的方式从「用导出键（pipeline 层生成的版本专属唯一键）」改为
    「用模板原始 template_id」，避免多版本子流程的那个版本专属导出键（uniqid）被误当成
    pipeline_template_id 去查库。
    """

    def _run(self, pipeline_template_data):
        manager = BaseTemplateManager()
        # 用非 TaskTemplate 的 model 让 template_source_type 落为 COMMON，跳过 CommonTemplate 分支
        manager.model = type("CommonTemplateLike", (), {"__name__": "CommonTemplateLike"})()

        filter_calls = []

        def fake_filter(*args, **kwargs):
            filter_calls.append(kwargs)
            if "id__in" in kwargs:
                return FakeQS(self._selected)
            if "pipeline_template_id__in" in kwargs:
                ids = kwargs["pipeline_template_id__in"]
                return FakeQS([s for s in self._subprocess_store if s["pipeline_template_id"] in ids])
            return FakeQS([])

        manager.filter = fake_filter

        with mock.patch.object(
            PipelineTemplateWebWrapper, "export_templates", return_value=pipeline_template_data
        ):
            result = manager.export_templates(template_id_list=[self._selected[0]["id"]])

        # 取出按 pipeline_template_id 反查子流程模板记录的 filter 调用，验证其入参
        additional_call = next(c for c in filter_calls if "pipeline_template_id__in" in c)
        return result, additional_call["pipeline_template_id__in"]

    def test_export_multi_version_subprocess_collapses_to_original_template_id(self):
        """多版本子流程的两个导出键（sub / sub_uniq）在收集模板 ID 时按原始 template_id 收敛为 {"sub"}。

        关键：additional_template_id 不会把版本专属的导出键 "sub_uniq" 当成 pipeline_template_id 去查库；
        旧实现（用导出键集合）会得到 {"sub", "sub_uniq"}，从而查到无效 ID。
        """
        self._selected = [_biz_record(10, "parent_a", "父流程A")]
        self._subprocess_store = [_biz_record(12, "sub", "子流程")]

        # 模拟 pipeline 层导出：同一子流程被两个父流程按不同版本引用 -> 两个导出键，template_id 都是 "sub"
        pipeline_template_data = {
            "template": {
                "parent_a": {"template_id": "parent_a", "name": "父流程A"},
                "sub": {"template_id": "sub", "name": "子流程"},
                "sub_uniq": {"template_id": "sub", "name": "子流程"},
            }
        }

        result, additional_ids = self._run(pipeline_template_data)

        # 按原始 template_id 收敛后，additional 只会是 {"sub"}，不含 "sub_uniq"
        self.assertEqual(additional_ids, {"sub"})
        # 子流程模板记录被补充进导出结果（id=12）
        self.assertIn(12, result["template"])
