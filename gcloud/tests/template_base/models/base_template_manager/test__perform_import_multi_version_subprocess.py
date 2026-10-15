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


def _biz_record(tid, pipeline_str_id, name):
    return {
        "category": "Default",
        "executor_proxy": "",
        "id": tid,
        "notify_type": '{"success":[],"fail":[]}',
        "pipeline_template_id": pipeline_str_id,
        "pipeline_template_str_id": pipeline_str_id,
        "project_id": 1,
        "time_out": 20,
        "name": name,
    }


def build_template_data(with_orphan):
    """构造导入数据。

    with_orphan=True 模拟「同一子流程被两个父流程按不同版本引用、同一次导出」：
    pipeline 层会为子流程生成两个导出键（原始 sub + 版本专属 sub_uniq），但业务层按 template_id 去重只有一条，
    导致 sub_uniq 对应的 PipelineTemplate 成为孤儿。
    """
    pipeline_template = {
        "parent_a": {"template_id": "parent_a", "name": "父流程A"},
        "parent_b": {"template_id": "parent_b", "name": "父流程B"},
        # 子流程首次出现的版本沿用原始 template_id 作为导出键，与业务记录的 pipeline_template_str_id 一致
        "sub": {"template_id": "sub", "name": "子流程"},
    }
    if with_orphan:
        pipeline_template["sub_uniq"] = {"template_id": "sub", "name": "子流程"}

    template = {
        "10": _biz_record(10, "parent_a", "父流程A"),
        "11": _biz_record(11, "parent_b", "父流程B"),
        "12": _biz_record(12, "sub", "子流程"),
    }
    return {
        "exporter_version": 1,
        "template_source": "project",
        "pipeline_template_data": {"template": pipeline_template},
        "template": template,
    }


# pipeline 层导出键 -> 导入后新 PipelineTemplate id
# 注意：orphan_key("sub_uniq") 对应的新 pipeline_template_id 固定为 "new_sub_uniq"，
# 用于模拟同一份导出文件重复覆盖导入时，pipeline 层复用同一个 PipelineTemplate(template_id 不变)
MOCK_ID_MAP = {
    PipelineTemplateWebWrapper.ID_MAP_KEY: {
        "parent_a": "new_parent_a",
        "parent_b": "new_parent_b",
        "sub": "new_sub",
        "sub_uniq": "new_sub_uniq",
    }
}


class MockTemplateModel(object):
    # 注意：__name__ 不能在这里赋值，它会被元类 type 的 __name__ 描述符覆盖（详见文件末尾的赋值）
    objects = None

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        if not hasattr(self, "id"):
            self.id = 999
        if not hasattr(self, "name"):
            self.name = "name"

    def save(self):
        return True

    @classmethod
    def create(cls, **kwargs):
        return cls(**kwargs)


class MockQuerySet(object):
    def __init__(self, objs):
        self._objs = objs

    def first(self):
        return self._objs[0] if self._objs else None


class MockObjects(object):
    def __init__(self):
        # 模拟持久化存储：记录所有通过 create() 新建的业务记录，用于验证「孤儿业务记录是否被复用」
        self.created_records = []

    def reset(self):
        self.created_records = []

    def filter(
        self,
        id__in=None,
        is_deleted=None,
        pipeline_template_id__in=None,
        template_id__in=None,
        pipeline_template_id=None,
    ):
        if pipeline_template_id is not None:
            matched = [
                obj
                for obj in self.created_records
                if getattr(obj, "pipeline_template_id", None) == pipeline_template_id
            ]
            return MockQuerySet(matched)
        if pipeline_template_id__in is not None:
            return [
                MockTemplateModel(pipeline_template_id=pid, id=abs(hash(pid)) % 100000, name="n")
                for pid in pipeline_template_id__in
            ]
        return self

    def values_list(self, field, flat):
        return []

    def update_or_create(self, id, defaults):
        return MockTemplateModel(**defaults), True

    def update(self, creator):
        return True

    def bulk_create(self, new_objects):
        return True

    def create(self, **kwargs):
        obj = MockTemplateModel(**kwargs)
        self.created_records.append(obj)
        return obj


MockTemplateModel.objects = MockObjects()
# 模拟 TaskTemplate：__name__ 在类体里赋值会被元类 type 的 __name__ 描述符覆盖，必须创建后再赋值，
# 否则 _perform_import 中 self.model.__name__ 仍为 "MockTemplateModel"，会走 COMMON 分支，
# 导致 template_recreated_info 的键是 "common" 而非断言使用的 "project"。
MockTemplateModel.__name__ = "TaskTemplate"


class MultiVersionSubprocessImportTest(TestCase):
    def _run(self, with_orphan, override, reset_store=True):
        if reset_store:
            MockTemplateModel.objects.reset()

        base_template_manager = BaseTemplateManager()
        base_template_manager.model = MockTemplateModel
        base_template_manager.update_or_create = lambda id, defaults: (MockTemplateModel(**defaults), True)

        template_data = build_template_data(with_orphan)
        check_info = {
            "can_override": True,
            "new_template": [
                {"id": 10, "name": "父流程A"},
                {"id": 11, "name": "父流程B"},
                {"id": 12, "name": "子流程"},
            ],
            "override_template": [],
        }
        if with_orphan:
            check_info["new_template"].append({"id": "sub_uniq", "name": "子流程"})

        def defaults_getter(template_dict):
            return {
                "category": template_dict["category"],
                "notify_type": template_dict["notify_type"],
                "time_out": template_dict["time_out"],
                "pipeline_template_id": template_dict["pipeline_template_id"],
                "is_deleted": False,
            }

        with mock.patch(
            "pipeline_web.wrapper.PipelineTemplateWebWrapper.import_templates",
            mock.Mock(return_value=MOCK_ID_MAP),
        ), mock.patch(
            "gcloud.iam_auth.resource_creator_action.signals.batch_create.send",
            mock.Mock(return_value=True),
        ):
            return base_template_manager._perform_import(
                template_data=template_data,
                check_info=check_info,
                override=override,
                defaults_getter=defaults_getter,
                operator="admin",
            )

    def test_normal_no_orphan(self):
        """正常场景（无多版本子流程）：行为与改动前一致，不补孤儿。"""
        result = self._run(with_orphan=False, override=False)
        self.assertTrue(result["result"])
        self.assertEqual(result["data"]["count"], 3)
        self.assertNotIn("sub_uniq", result["id_map"]["template_recreated_info"].get("project", {}))

    def test_no_override_multi_version_subprocess(self):
        """多版本子流程、非覆盖导入：补齐孤儿业务记录，导入结果包含第 4 个流程。"""
        result = self._run(with_orphan=True, override=False)
        self.assertTrue(result["result"])
        # 父A + 父B + 子流程 + 孤儿版本 = 4
        self.assertEqual(result["data"]["count"], 4)
        # 孤儿业务记录已补齐，且能定位到对应的 PipelineTemplate（不再 DoesNotExist）
        orphan_info = result["id_map"]["template_recreated_info"]["project"]["sub_uniq"]
        self.assertEqual(orphan_info["import_data"]["pipeline_template_id"], "new_sub_uniq")

    def test_override_multi_version_subprocess(self):
        """多版本子流程、覆盖导入：同样补齐孤儿，且非数字导出键走新建而非 update_or_create(id=...)。"""
        result = self._run(with_orphan=True, override=True)
        self.assertTrue(result["result"])
        self.assertEqual(result["data"]["count"], 4)
        orphan_info = result["id_map"]["template_recreated_info"]["project"]["sub_uniq"]
        self.assertEqual(orphan_info["import_data"]["pipeline_template_id"], "new_sub_uniq")

        # 版本导出键（非数字）不应混入 flows：下游 audit_imported_templates() 会对 flows 的键执行
        # int() 转换，非数字键会抛异常导致本次导入的整批审计事件都不产生
        self.assertNotIn("sub_uniq", result["data"]["flows"])
        # flows 改为使用真实创建的业务 ID 作为键
        real_new_id = abs(hash("new_sub_uniq")) % 100000
        self.assertIn(real_new_id, result["data"]["flows"])

    def test_override_multi_version_subprocess_repeat_import_reuses_orphan_record(self):
        """多版本子流程、覆盖导入、重复执行同一份导出文件：孤儿业务记录应被复用，而不是每次都新建一条。

        模拟场景：同一份 .dat 文件被反复覆盖导入；pipeline 层对版本专属导出键（非数字）复用同一个
        PipelineTemplate（template_id 不变），因此业务层也应按 pipeline_template_id 查找并复用已存在的
        业务记录，否则同一个 pipeline_template_id 会堆积出多条业务记录，后续按
        pipeline_template__template_id 反查时会因 MultipleObjectsReturned 而 500。
        """
        MockTemplateModel.objects.reset()

        result1 = self._run(with_orphan=True, override=True, reset_store=False)
        result2 = self._run(with_orphan=True, override=True, reset_store=False)

        self.assertTrue(result1["result"])
        self.assertTrue(result2["result"])

        orphan_pipeline_template_id = "new_sub_uniq"
        matched = [
            obj
            for obj in MockTemplateModel.objects.created_records
            if getattr(obj, "pipeline_template_id", None) == orphan_pipeline_template_id
        ]
        # 两次覆盖导入后，孤儿业务记录只应存在一条（第二次应复用第一次创建的记录，而非新建）
        self.assertEqual(len(matched), 1)
