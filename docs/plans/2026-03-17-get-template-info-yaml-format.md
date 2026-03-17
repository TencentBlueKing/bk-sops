# 网关接口 YAML 格式导出/导入 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 在 `get_template_info` 网关接口增加 `format=yaml` 参数导出 YAML，在 `create_template` 网关接口增加 `format=yaml` 参数导入 YAML。

**Architecture:** 导出：在 `get_template_info` view 中增加分支，`format=yaml` 时调用 `export_templates` + `YamlSchemaConverterHandler.convert()` 将 pipeline_tree 转换为 YAML schema 字符串。导入：在 `create_template` view 中增加分支，`format=yaml` 时调用 `load_yaml_docs` + `reconvert` 将 YAML schema 还原为 pipeline_tree。

**Tech Stack:** Django, DRF serializers, PyYAML, YamlSchemaConverterHandler

---

### Task 1: Serializer 增加 format 字段

**Files:**
- Modify: `gcloud/apigw/serializers.py:26-32`

**Step 1: 在 IncludeTemplateSerializer 增加 format 字段**

在 `IncludeTemplateSerializer` 中添加：

```python
format = serializers.ChoiceField(
    required=False,
    choices=["json", "yaml"],
    default="json",
    help_text="pipeline_tree 的返回格式，json 返回原始对象，yaml 返回 YAML schema 字符串",
)
```

**Step 2: Commit**

```bash
git add gcloud/apigw/serializers.py
git commit -m "feat: IncludeTemplateSerializer 增加 format 字段"
```

---

### Task 2: View 实现 YAML 转换逻辑

**Files:**
- Modify: `gcloud/apigw/views/get_template_info.py`

**Step 1: 添加 YAML 转换逻辑**

在 `get_template_info` 函数中，正常构造 `data` 之后、return 之前，增加判断：

```python
import yaml
from gcloud.exceptions import FlowExportError
from gcloud.template_base.domains.converter_handler import YamlSchemaConverterHandler
from gcloud.utils.yaml import NoAliasSafeDumper

# ... 现有代码构造 data 之后 ...

output_format = serializer.validated_data["format"]
if output_format == "yaml":
    template_model_cls = CommonTemplate if template_source not in NON_COMMON_TEMPLATE_TYPES else TaskTemplate
    try:
        templates_data = template_model_cls.objects.export_templates(
            [int(template_id)], project_id=project.id if template_source in NON_COMMON_TEMPLATE_TYPES else None
        )
        converter_handler = YamlSchemaConverterHandler("v1")
        convert_result = converter_handler.convert(templates_data)
    except FlowExportError as e:
        return {
            "result": False,
            "message": "export yaml failed: {}".format(str(e)),
            "code": err_code.UNKNOWN_ERROR.code,
        }

    if not convert_result["result"]:
        return {
            "result": False,
            "message": "convert yaml failed: {}".format(convert_result["message"]),
            "code": err_code.UNKNOWN_ERROR.code,
        }

    yaml_content = yaml.dump_all(
        convert_result["data"], allow_unicode=True, sort_keys=False, Dumper=NoAliasSafeDumper
    )
    data["pipeline_tree"] = yaml_content
```

需要注意：`mcp_apigw(trim_responses={"pipeline_tree": trim_pipeline_tree})` 装饰器在 `format=yaml` 时，`pipeline_tree` 是字符串。`trim_pipeline_tree` 函数应该能安全处理（传入字符串时原样返回），需要确认。如果不能，则在 `trim_pipeline_tree` 中增加类型判断。

**Step 2: 确认 trim_pipeline_tree 兼容性**

检查 `gcloud/utils/pipeline_tree_trimmer.py` 中 `trim_pipeline_tree` 函数，确保传入字符串时不会报错。如果需要，增加类型守卫：

```python
def trim_pipeline_tree(pipeline_tree):
    if not isinstance(pipeline_tree, dict):
        return pipeline_tree
    # ... 原有逻辑 ...
```

**Step 3: Commit**

```bash
git add gcloud/apigw/views/get_template_info.py gcloud/utils/pipeline_tree_trimmer.py
git commit -m "feat: get_template_info 支持 format=yaml 参数导出 YAML 格式 pipeline_tree"
```

---

### Task 3: 单元测试

**Files:**
- Modify: `gcloud/tests/apigw/views/test_get_template_info.py`

**Step 1: 增加 format=yaml 成功场景测试**

```python
@mock.patch(PROJECT_GET, MagicMock(return_value=MockProject(...)))
def test_get_template_info__format_yaml(self):
    """format=yaml 时 pipeline_tree 应为 YAML 字符串"""
    pt1 = MockPipelineTemplate(id=1, name="pt1")
    tmpl = MockTaskTemplate(id=1, pipeline_template=pt1)

    mock_export_data = {"template_data": "mock"}
    mock_convert_result = {"result": True, "data": [{"schema_version": "v1", "meta": {}, "spec": {}}]}

    with mock.patch(TASKTEMPLATE_SELECT_RELATE, MagicMock(return_value=MockQuerySet(get_result=tmpl))), \
         mock.patch("gcloud.tasktmpl3.models.TaskTemplate.objects.export_templates", return_value=mock_export_data), \
         mock.patch("gcloud.apigw.views.get_template_info.YamlSchemaConverterHandler") as mock_handler_cls:
        mock_handler = MagicMock()
        mock_handler.convert.return_value = mock_convert_result
        mock_handler_cls.return_value = mock_handler

        response = self.client.get(
            path=self.url().format(template_id=TEST_TEMPLATE_ID, project_id=TEST_PROJECT_ID),
            data={"format": "yaml"},
        )
        data = json.loads(response.content)
        self.assertTrue(data["result"])
        self.assertIsInstance(data["data"]["pipeline_tree"], str)
        self.assertIn("schema_version", data["data"]["pipeline_tree"])
```

**Step 2: 增加 format=yaml 转换失败测试**

**Step 3: 运行测试**

```bash
python -m pytest gcloud/tests/apigw/views/test_get_template_info.py -v
```

**Step 4: Commit**

```bash
git add gcloud/tests/apigw/views/test_get_template_info.py
git commit -m "test: get_template_info format=yaml 单元测试"
```

---

### Task 4: 网关资源定义更新

**Files:**
- Modify: `apigw/bk_apigw_resources_bk-sops_mcp_supplement.yaml`

**Step 1: 在 get_template_info 的 parameters 中增加 format 参数**

在 `/get_template_info/{template_id}/{bk_biz_id}/` 的 `parameters` 列表中，`include_pipeline_tree` 之后添加：

```yaml
      - in: query
        name: format
        required: false
        schema:
          type: string
          enum:
          - json
          - yaml
          default: json
        description: pipeline_tree 的返回格式。json（默认）返回原始 JSON 对象；yaml 返回与页面导出一致的
          YAML schema 字符串（含 schema_version/meta/spec 结构）
```

同时更新 `pipeline_tree` 的 schema description，说明 format=yaml 时为字符串。

**Step 2: YAML 语法校验**

```bash
python3 -c "import yaml; yaml.safe_load(open('apigw/bk_apigw_resources_bk-sops_mcp_supplement.yaml')); print('YAML is valid')"
```

**Step 3: Commit**

```bash
git add apigw/bk_apigw_resources_bk-sops_mcp_supplement.yaml
git commit -m "feat: 网关资源定义补充 get_template_info format 参数"
```

---

### Task 5: API 文档更新

**Files:**
- Modify: `docs/apidoc/zh_hans/get_template_info.md`
- Modify: `docs/apidoc/en/get_template_info.md`

**Step 1: 中文文档在接口参数表增加 format 行**

在参数表中添加：

```
| format | string | 否 | pipeline_tree 的返回格式，可选值 json（默认）、yaml。设为 yaml 时，pipeline_tree 字段返回与页面导出一致的 YAML schema 字符串 |
```

**Step 2: 英文文档同步**

**Step 3: 文档打包**

```bash
cd /root/Projects/bk-sops
tmpdir=$(mktemp -d)
mkdir -p "$tmpdir/zh" "$tmpdir/en"
cp docs/apidoc/zh_hans/*.md "$tmpdir/zh/"
cp docs/apidoc/en/*.md "$tmpdir/en/"
cd "$tmpdir"
tar -czf /root/Projects/bk-sops/gcloud/apigw/docs/apigw-docs.tgz zh/ en/
rm -rf "$tmpdir"
```

**Step 4: Commit**

```bash
git add docs/apidoc/zh_hans/get_template_info.md docs/apidoc/en/get_template_info.md gcloud/apigw/docs/apigw-docs.tgz
git commit -m "docs: get_template_info 增加 format=yaml 参数文档"
```

---

## Part 2: create_template YAML 导入

### Task 6: View 实现 YAML 导入逻辑

**Files:**
- Modify: `gcloud/apigw/views/create_template.py`

**Step 1: 添加 YAML 导入逻辑**

在 `create_template` 函数中，解析 `pipeline_tree` 之前，增加 `format` 判断：

```python
from gcloud.template_base.domains.converter_handler import YamlSchemaConverterHandler

input_format = params.get("format", "json")
if input_format == "yaml":
    if not isinstance(pipeline_tree, str):
        return error: "pipeline_tree must be a YAML string when format=yaml"
    converter_handler = YamlSchemaConverterHandler("v1")
    load_result = converter_handler.load_yaml_docs(pipeline_tree)
    if not load_result["result"]:
        return error
    convert_result = converter_handler.reconvert(load_result["data"])
    if not convert_result["result"]:
        return error
    # 取第一个模板
    template_order = convert_result["data"]["template_order"]
    templates = convert_result["data"]["templates"]
    first_template = templates[template_order[0]]
    pipeline_tree = first_template["tree"]
    name = name or first_template.get("name")
    description = description or first_template.get("description", "")
else:
    # 现有 JSON 逻辑不变
    if isinstance(pipeline_tree, str):
        pipeline_tree = json.loads(pipeline_tree)
```

**Step 2: Commit**

```bash
git add gcloud/apigw/views/create_template.py
git commit -m "feat: create_template 支持 format=yaml 参数导入 YAML 格式流程"
```

---

### Task 7: 网关资源定义更新

**Files:**
- Modify: `apigw/bk_apigw_resources_bk-sops_create_template.yaml`

**Step 1: 在 requestBody properties 中增加 format 字段**

```yaml
format:
  type: string
  description: pipeline_tree 的输入格式
  enum: [json, yaml]
  default: json
```

同时将 `pipeline_tree` 的 schema 改为 `oneOf: [type: object, type: string]`。

**Step 2: YAML 语法校验**

**Step 3: Commit**

---

### Task 8: API 文档更新

**Files:**
- Modify: `docs/apidoc/zh_hans/create_template.md`
- Modify: `docs/apidoc/en/create_template.md`

**Step 1: 中英文文档在接口参数表增加 format 行**

**Step 2: 文档打包**

**Step 3: Commit**

```bash
git add gcloud/apigw/views/create_template.py apigw/bk_apigw_resources_bk-sops_create_template.yaml \
  docs/apidoc/zh_hans/create_template.md docs/apidoc/en/create_template.md gcloud/apigw/docs/apigw-docs.tgz
git commit -m "feat: create_template 网关接口支持 format=yaml 参数导入 YAML 格式流程"
```
