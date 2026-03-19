# get_template_info unfold_subprocess 实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 在 `get_template_info` 接口新增 `unfold_subprocess` 参数，允许一次调用返回完整递归展开的子流程 pipeline_tree。

**Architecture:** 在 `IncludeTemplateSerializer` 中新增字段，在 `format_template_data` 中新增处理分支：先获取 `template.pipeline_tree`（已做用户 ID 转换），将 SubProcess 节点 template_id 转回内部 UUID，再调用现有 `PipelineTemplateWebWrapper.unfold_subprocess` 展开，最后用新增的 `replace_template_id_recursive` 将整棵树转回用户可见 pk。

**Tech Stack:** Django REST Framework Serializer、`pipeline_web.wrapper.PipelineTemplateWebWrapper`、现有 `replace_template_id` 工具函数。

---

## Task 1: Serializer 新增字段

**Files:**
- Modify: `gcloud/apigw/serializers.py:26-31`

### Step 1: 修改 serializer，新增字段

在 `IncludeTemplateSerializer` 末尾加一行：

```python
class IncludeTemplateSerializer(serializers.Serializer):
    include_executor_proxy = serializers.BooleanField(required=False, help_text="模板代理信息", default=False)
    include_subprocess = serializers.BooleanField(required=False, help_text="子流程信息", default=False)
    include_constants = serializers.BooleanField(required=False, help_text="全局变量", default=False)
    include_notify = serializers.BooleanField(required=False, help_text="通知信息", default=False)
    include_labels = serializers.BooleanField(required=False, help_text="标签信息", default=False)
    unfold_subprocess = serializers.BooleanField(required=False, help_text="是否展开子流程完整配置", default=False)
```

### Step 2: 验证 serializer 正确解析新字段

```bash
cd /root/Projects/bk-sops
python -c "
from gcloud.apigw.serializers import IncludeTemplateSerializer
s = IncludeTemplateSerializer(data={'unfold_subprocess': 'true'})
assert s.is_valid(), s.errors
assert s.validated_data['unfold_subprocess'] is True
s2 = IncludeTemplateSerializer(data={})
assert s2.is_valid()
assert s2.validated_data['unfold_subprocess'] is False
print('OK')
"
```
Expected: `OK`

### Step 3: Commit

```bash
git add gcloud/apigw/serializers.py
git commit -m "feat: add unfold_subprocess field to IncludeTemplateSerializer"
```

---

## Task 2: 新增 `replace_template_id_recursive` 工具函数

**Files:**
- Modify: `gcloud/apigw/views/utils.py`
- Test: `gcloud/tests/apigw/views/test_utils.py`（新建）

### Step 1: 在 `utils.py` 新增函数

在 `gcloud/apigw/views/utils.py` 中，在现有 import 区域补充导入，并在文件末尾添加新函数：

需要在文件顶部导入区域已有的导入后面补充（如果没有则添加）：

```python
from django.apps import apps
from gcloud.constants import COMMON
from gcloud.template_base.utils import replace_template_id
```

新增函数放在 `format_template_data` 之前：

```python
def replace_template_id_recursive(template_model, pipeline_data, reverse=False):
    """对整棵 pipeline_tree（含所有层级的 act["pipeline"]）递归执行 ID 转换。

    unfold_subprocess 展开后，各层子流程数据位于 act["pipeline"]，
    现有 replace_template_id 只处理顶层 activities，此函数补充递归逻辑。
    """
    replace_template_id(template_model, pipeline_data, reverse=reverse)
    for act in pipeline_data.get("activities", {}).values():
        if act.get("type") == "SubProcess" and "pipeline" in act:
            subprocess_template_model = (
                apps.get_model("template", "CommonTemplate")
                if act.get("template_source") == "common"
                else template_model
            )
            replace_template_id_recursive(subprocess_template_model, act["pipeline"], reverse=reverse)
```

### Step 2: 新建测试文件，写失败测试

新建 `gcloud/tests/apigw/views/test_utils.py`：

```python
# -*- coding: utf-8 -*-
from unittest import TestCase
from unittest.mock import MagicMock, patch, call

REPLACE_TEMPLATE_ID = "gcloud.apigw.views.utils.replace_template_id"


class ReplaceTemplateIdRecursiveTest(TestCase):

    def test_no_subprocess_activities(self):
        """无子流程时，只调用一次顶层 replace_template_id"""
        from gcloud.apigw.views.utils import replace_template_id_recursive
        template_model = MagicMock()
        pipeline_data = {
            "activities": {
                "node1": {"type": "ServiceActivity"},
            }
        }
        with patch(REPLACE_TEMPLATE_ID) as mock_replace:
            replace_template_id_recursive(template_model, pipeline_data, reverse=True)
            mock_replace.assert_called_once_with(template_model, pipeline_data, reverse=True)

    def test_subprocess_without_pipeline_key(self):
        """SubProcess 节点没有 pipeline 字段时，不递归"""
        from gcloud.apigw.views.utils import replace_template_id_recursive
        template_model = MagicMock()
        pipeline_data = {
            "activities": {
                "node1": {"type": "SubProcess", "template_id": "123"},
            }
        }
        with patch(REPLACE_TEMPLATE_ID) as mock_replace:
            replace_template_id_recursive(template_model, pipeline_data, reverse=True)
            mock_replace.assert_called_once_with(template_model, pipeline_data, reverse=True)

    def test_subprocess_with_pipeline_key_recursion(self):
        """SubProcess 有 pipeline 字段时，递归处理子流程"""
        from gcloud.apigw.views.utils import replace_template_id_recursive
        template_model = MagicMock()
        sub_pipeline = {"activities": {}}
        pipeline_data = {
            "activities": {
                "node1": {
                    "type": "SubProcess",
                    "template_source": "business",
                    "pipeline": sub_pipeline,
                },
            }
        }
        with patch(REPLACE_TEMPLATE_ID) as mock_replace:
            replace_template_id_recursive(template_model, pipeline_data, reverse=True)
            assert mock_replace.call_count == 2
            mock_replace.assert_any_call(template_model, pipeline_data, reverse=True)
            mock_replace.assert_any_call(template_model, sub_pipeline, reverse=True)

    def test_common_subprocess_uses_common_template_model(self):
        """template_source=common 的子流程使用 CommonTemplate model"""
        from gcloud.apigw.views.utils import replace_template_id_recursive
        template_model = MagicMock()
        mock_common_model = MagicMock()
        sub_pipeline = {"activities": {}}
        pipeline_data = {
            "activities": {
                "node1": {
                    "type": "SubProcess",
                    "template_source": "common",
                    "pipeline": sub_pipeline,
                },
            }
        }
        with patch(REPLACE_TEMPLATE_ID) as mock_replace, \
             patch("gcloud.apigw.views.utils.apps.get_model", return_value=mock_common_model):
            replace_template_id_recursive(template_model, pipeline_data, reverse=True)
            mock_replace.assert_any_call(mock_common_model, sub_pipeline, reverse=True)
```

### Step 3: 运行测试，确认失败

```bash
cd /root/Projects/bk-sops
python -m pytest gcloud/tests/apigw/views/test_utils.py -v 2>&1 | head -30
```
Expected: 4 个测试 FAILED（函数尚未实现）

### Step 4: 实现函数（已在 Step 1 写好），运行测试确认通过

```bash
python -m pytest gcloud/tests/apigw/views/test_utils.py -v
```
Expected: 4 个测试全部 PASSED

### Step 5: Commit

```bash
git add gcloud/apigw/views/utils.py gcloud/tests/apigw/views/test_utils.py
git commit -m "feat: add replace_template_id_recursive utility function"
```

---

## Task 3: 修改 `format_template_data` 支持 unfold_subprocess

**Files:**
- Modify: `gcloud/apigw/views/utils.py:57-104`

### Step 1: 先在测试文件 `test_utils.py` 新增失败测试

在 `gcloud/tests/apigw/views/test_utils.py` 末尾追加：

```python
FORMAT_TEMPLATE_DATA_UNFOLD = "pipeline_web.wrapper.PipelineTemplateWebWrapper.unfold_subprocess"
FORMAT_TEMPLATE_DATA_REPLACE_RECURSIVE = "gcloud.apigw.views.utils.replace_template_id_recursive"
FORMAT_TEMPLATE_DATA_REPLACE = "gcloud.apigw.views.utils.replace_template_id"


class FormatTemplateDataUnfoldSubprocessTest(TestCase):

    def _make_template(self, with_subprocess=False):
        """构造一个包含子流程活动的 mock template"""
        activities = {}
        if with_subprocess:
            activities["node_sub"] = {
                "type": "SubProcess",
                "template_id": "999",
                "template_source": "business",
            }
        pipeline_tree = {
            "line": [],
            "location": [],
            "activities": activities,
            "constants": {},
            "gateways": {},
            "flows": {},
            "start_event": {},
            "end_event": {},
        }
        mock_pt = MagicMock()
        mock_pt.name = "tmpl_name"
        mock_pt.creator = "admin"
        mock_pt.create_time = None
        mock_pt.editor = "admin"
        mock_pt.edit_time = None
        mock_pt.description = ""
        tmpl = MagicMock()
        tmpl.id = 1
        tmpl.category = "Other"
        tmpl.pipeline_template = mock_pt
        tmpl.pipeline_tree = pipeline_tree
        return tmpl, pipeline_tree

    def test_unfold_subprocess_false_does_not_call_unfold(self):
        """unfold_subprocess=False 时不调用 PipelineTemplateWebWrapper.unfold_subprocess"""
        from gcloud.apigw.views.utils import format_template_data
        tmpl, _ = self._make_template()
        with patch(FORMAT_TEMPLATE_DATA_UNFOLD) as mock_unfold, \
             patch("gcloud.apigw.views.utils.varschema"):
            format_template_data(tmpl, unfold_subprocess=False)
            mock_unfold.assert_not_called()

    def test_unfold_subprocess_true_calls_unfold_and_recursive_replace(self):
        """unfold_subprocess=True 时调用 unfold 和 replace_template_id_recursive"""
        from gcloud.apigw.views.utils import format_template_data
        tmpl, pipeline_tree = self._make_template(with_subprocess=True)
        with patch(FORMAT_TEMPLATE_DATA_UNFOLD) as mock_unfold, \
             patch(FORMAT_TEMPLATE_DATA_REPLACE) as mock_replace, \
             patch(FORMAT_TEMPLATE_DATA_REPLACE_RECURSIVE) as mock_replace_recursive, \
             patch("gcloud.apigw.views.utils.varschema"):
            result = format_template_data(tmpl, unfold_subprocess=True)
            # replace_template_id 先调用（user-facing → internal UUID）
            mock_replace.assert_called_once_with(tmpl.__class__, pipeline_tree)
            # unfold_subprocess 调用
            mock_unfold.assert_called_once_with(pipeline_tree, tmpl.__class__)
            # replace_template_id_recursive 最后调用（internal UUID → user-facing）
            mock_replace_recursive.assert_called_once_with(tmpl.__class__, pipeline_tree, reverse=True)
            # line/location 已 pop
            assert "line" not in result["data"]["pipeline_tree"]
            assert "location" not in result["data"]["pipeline_tree"]

    def test_unfold_subprocess_true_exception_propagates(self):
        """unfold_subprocess 内部异常向上冒泡"""
        from gcloud.apigw.views.utils import format_template_data
        from pipeline.exceptions import PipelineException
        tmpl, _ = self._make_template(with_subprocess=True)
        with patch(FORMAT_TEMPLATE_DATA_UNFOLD, side_effect=PipelineException("recursion limit")), \
             patch(FORMAT_TEMPLATE_DATA_REPLACE), \
             patch("gcloud.apigw.views.utils.varschema"):
            with self.assertRaises(PipelineException):
                format_template_data(tmpl, unfold_subprocess=True)
```

### Step 2: 运行新增测试，确认失败

```bash
python -m pytest gcloud/tests/apigw/views/test_utils.py::FormatTemplateDataUnfoldSubprocessTest -v
```
Expected: FAILED（`format_template_data` 尚不支持 `unfold_subprocess` 参数）

### Step 3: 修改 `format_template_data`

在 `gcloud/apigw/views/utils.py` 中修改 `format_template_data`：

在文件顶部 import 区域补充（如果缺少）：

```python
from gcloud.template_base.utils import replace_template_id
```

修改函数签名和逻辑：

```python
def format_template_data(
    template, project=None, include_subprocess=None, tz=None,
    include_executor_proxy=None, include_notify=None, unfold_subprocess=False
):
    if unfold_subprocess:
        from pipeline_web.wrapper import PipelineTemplateWebWrapper
        # 获取已做用户ID转换和 to_web 的 pipeline_tree
        pipeline_tree = template.pipeline_tree
        pipeline_tree.pop("line", None)
        pipeline_tree.pop("location", None)
        # 将顶层 SubProcess.template_id 从用户 pk 转回内部 UUID（unfold_subprocess 需要）
        replace_template_id(template.__class__, pipeline_tree)
        # 递归展开所有子流程，写入 act["pipeline"]
        PipelineTemplateWebWrapper.unfold_subprocess(pipeline_tree, template.__class__)
        # 将整棵树所有层级转回用户可见 pk
        replace_template_id_recursive(template.__class__, pipeline_tree, reverse=True)
    else:
        pipeline_tree = template.pipeline_tree
        pipeline_tree.pop("line")
        pipeline_tree.pop("location")

    varschema.add_schema_for_input_vars(pipeline_tree)

    data = {
        "id": template.id,
        "name": template.pipeline_template.name,
        # ... 以下保持原有字段不变 ...
    }
```

> 注意：只修改函数开头的 `pipeline_tree` 获取逻辑，`data` 字典及后续逻辑保持不变。

### Step 4: 运行测试确认通过

```bash
python -m pytest gcloud/tests/apigw/views/test_utils.py -v
```
Expected: 全部 PASSED

### Step 5: 确认原有测试不受影响

```bash
python -m pytest gcloud/tests/apigw/views/ -v -k "not test_utils"
```
Expected: 全部 PASSED（无回归）

### Step 6: Commit

```bash
git add gcloud/apigw/views/utils.py gcloud/tests/apigw/views/test_utils.py
git commit -m "feat: support unfold_subprocess in format_template_data"
```

---

## Task 4: 更新 `get_template_info` 视图读取新参数并处理异常

**Files:**
- Modify: `gcloud/apigw/views/get_template_info.py`
- Test: `gcloud/tests/apigw/views/test_get_template_info.py`

### Step 1: 先在测试文件追加失败测试

在 `gcloud/tests/apigw/views/test_get_template_info.py` 末尾的 `GetTemplateInfoAPITest` 类中追加两个测试方法：

```python
UNFOLD_SUBPROCESS_PATH = "pipeline_web.wrapper.PipelineTemplateWebWrapper.unfold_subprocess"
REPLACE_RECURSIVE_PATH = "gcloud.apigw.views.utils.replace_template_id_recursive"
REPLACE_PATH = "gcloud.apigw.views.utils.replace_template_id"

@mock.patch(
    PROJECT_GET,
    MagicMock(
        return_value=MockProject(
            project_id=TEST_PROJECT_ID,
            name=TEST_PROJECT_NAME,
            bk_biz_id=TEST_BIZ_CC_ID,
            from_cmdb=True,
        )
    ),
)
def test_get_template_info__unfold_subprocess_true(self):
    """unfold_subprocess=true 时调用 unfold 并返回正常结果"""
    pt1 = MockPipelineTemplate(id=1, name="pt1")
    tmpl = MockTaskTemplate(id=1, pipeline_template=pt1)

    with mock.patch(TASKTEMPLATE_SELECT_RELATE, MagicMock(return_value=MockQuerySet(get_result=tmpl))), \
         mock.patch(UNFOLD_SUBPROCESS_PATH) as mock_unfold, \
         mock.patch(REPLACE_PATH), \
         mock.patch(REPLACE_RECURSIVE_PATH):
        response = self.client.get(
            path=self.url().format(template_id=TEST_TEMPLATE_ID, project_id=TEST_PROJECT_ID),
            data={"unfold_subprocess": "true"},
        )
        data = json.loads(response.content)
        self.assertTrue(data["result"], msg=data)
        mock_unfold.assert_called_once()

@mock.patch(
    PROJECT_GET,
    MagicMock(
        return_value=MockProject(
            project_id=TEST_PROJECT_ID,
            name=TEST_PROJECT_NAME,
            bk_biz_id=TEST_BIZ_CC_ID,
            from_cmdb=True,
        )
    ),
)
def test_get_template_info__unfold_subprocess_exception(self):
    """unfold_subprocess 内部异常时返回 result=False"""
    from pipeline.exceptions import PipelineException
    pt1 = MockPipelineTemplate(id=1, name="pt1")
    tmpl = MockTaskTemplate(id=1, pipeline_template=pt1)

    with mock.patch(TASKTEMPLATE_SELECT_RELATE, MagicMock(return_value=MockQuerySet(get_result=tmpl))), \
         mock.patch(REPLACE_PATH), \
         mock.patch(UNFOLD_SUBPROCESS_PATH, side_effect=PipelineException("recursion limit")):
        response = self.client.get(
            path=self.url().format(template_id=TEST_TEMPLATE_ID, project_id=TEST_PROJECT_ID),
            data={"unfold_subprocess": "true"},
        )
        data = json.loads(response.content)
        self.assertFalse(data["result"])
        self.assertIn("unfold_subprocess", data["message"])
```

### Step 2: 运行新增测试，确认失败

```bash
python -m pytest gcloud/tests/apigw/views/test_get_template_info.py::GetTemplateInfoAPITest::test_get_template_info__unfold_subprocess_true \
                 gcloud/tests/apigw/views/test_get_template_info.py::GetTemplateInfoAPITest::test_get_template_info__unfold_subprocess_exception \
                 -v
```
Expected: FAILED

### Step 3: 修改视图函数

修改 `gcloud/apigw/views/get_template_info.py`：

在 import 区域顶部补充（如缺少）：

```python
import logging
logger = logging.getLogger("root")
```

修改视图函数：

```python
def get_template_info(request, template_id, project_id):
    project = request.project
    serializer = IncludeTemplateSerializer(data=request.GET)
    if not serializer.is_valid():
        return {"result": False, "message": serializer.errors, "code": err_code.REQUEST_PARAM_INVALID.code}
    template_source = request.GET.get("template_source", PROJECT)
    include_subprocess = serializer.validated_data["include_subprocess"]
    include_constants = serializer.validated_data["include_constants"]
    include_executor_proxy = serializer.validated_data["include_executor_proxy"]
    include_notify = serializer.validated_data["include_notify"]
    unfold_subprocess = serializer.validated_data["unfold_subprocess"]   # 新增
    if template_source in NON_COMMON_TEMPLATE_TYPES:
        try:
            tmpl = TaskTemplate.objects.select_related("pipeline_template").get(
                id=template_id, project_id=project.id, is_deleted=False
            )
        except TaskTemplate.DoesNotExist:
            return {
                "result": False,
                "message": "template[id={template_id}] of project[project_id={project_id}, biz_id={biz_id}] "
                "does not exist".format(
                    template_id=template_id, project_id=project.id, biz_id=project.bk_biz_id,
                ),
                "code": err_code.CONTENT_NOT_EXIST.code,
            }
    else:
        try:
            tmpl = CommonTemplate.objects.select_related("pipeline_template").get(id=template_id, is_deleted=False)
        except CommonTemplate.DoesNotExist:
            return {
                "result": False,
                "message": "common template[id={template_id}] does not exist".format(template_id=template_id),
                "code": err_code.CONTENT_NOT_EXIST.code,
            }

    try:
        data = format_template_data(
            tmpl, project, include_subprocess,
            include_executor_proxy=include_executor_proxy,
            include_notify=include_notify,
            unfold_subprocess=unfold_subprocess,     # 新增
        )
    except Exception as e:
        logger.exception("[get_template_info] unfold_subprocess error: template_id=%s", template_id)
        return {
            "result": False,
            "message": "unfold_subprocess failed: {}".format(str(e)),
            "code": err_code.UNKNOWN_ERROR.code,
        }

    if include_constants:
        data["template_constants"] = process_pipeline_constants(data["pipeline_tree"])

    return {"result": True, "data": data, "code": err_code.SUCCESS.code}
```

### Step 4: 运行全部 get_template_info 测试，确认通过

```bash
python -m pytest gcloud/tests/apigw/views/test_get_template_info.py -v
```
Expected: 全部 PASSED

### Step 5: Commit

```bash
git add gcloud/apigw/views/get_template_info.py gcloud/tests/apigw/views/test_get_template_info.py
git commit -m "feat: get_template_info supports unfold_subprocess parameter"
```

---

## Task 5: 更新文档和 Skill 参考

**Files:**
- Modify: `docs/apidoc/zh_hans/get_template_info.md`
- Modify: `.cursor/skills/references/get_template_info.md`

### Step 1: 更新 `docs/apidoc/zh_hans/get_template_info.md`

在接口参数表中新增一行（在 `include_notify` 行之后）：

```markdown
| unfold_subprocess | bool | 否 | 是否展开 pipeline_tree 中所有子流程的完整配置，默认 false。为 true 时，pipeline_tree.activities 中每个 SubProcess 类型节点会新增 `pipeline` 字段，包含该子流程的完整结构并递归展开。 |
```

在返回结果示例中，找到 `pipeline_tree.activities` 部分，在 SubProcess 类型节点示例里新增 `pipeline` 字段说明：

```json
"node_sub_example": {
    "type": "SubProcess",
    "template_id": "456",
    "name": "子流程示例",
    "pipeline": {
        "activities": {},
        "constants": {},
        "flows": {},
        "gateways": {},
        "start_event": {},
        "end_event": {}
    }
}
```

在返回结果说明表格中新增 `data.pipeline_tree.activities[].pipeline` 字段描述：

```markdown
| pipeline_tree.activities[type=SubProcess].pipeline | dict | unfold_subprocess=true 时存在，子流程的完整 pipeline_tree 结构，递归展开 |
```

### Step 2: 更新 `.cursor/skills/references/get_template_info.md`

在查询参数表格中新增：

```markdown
| unfold_subprocess | bool | 否 | 是否展开子流程完整配置，默认 false。为 true 时 SubProcess 节点新增 `pipeline` 字段 |
```

在文件末尾的注意事项区域补充：

```markdown
- `unfold_subprocess=true` 时，`pipeline_tree.activities` 中每个 `type=SubProcess` 节点会包含 `pipeline` 字段，结构与顶层 `pipeline_tree` 完全一致，可递归读取
- 对于嵌套层数较多的复杂模板，响应体可能较大，建议仅在需要分析完整流程结构时使用
```

### Step 3: Commit

```bash
git add docs/apidoc/zh_hans/get_template_info.md .cursor/skills/references/get_template_info.md
git commit -m "docs: update get_template_info docs for unfold_subprocess parameter"
```

---

## 完成验证

所有任务完成后，执行全量回归确认无破坏：

```bash
python -m pytest gcloud/tests/apigw/views/ -v
```
Expected: 全部 PASSED，包含所有原有测试。
