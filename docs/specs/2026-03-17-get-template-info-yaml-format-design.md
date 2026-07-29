# 网关接口增加 YAML 格式导出/导入支持

## 背景

标准运维页面已支持将流程模板导出为 YAML 格式文件（经 `YamlSchemaConverterHandler` 转换，包含 `schema_version` / `meta` / `spec` 结构），以及从 YAML 格式文件导入流程模板。但网关（apigw）层目前没有 YAML 格式的导出/导入接口，API 调用方无法通过网关以 YAML 格式操作模板数据。

## 方案一：get_template_info 导出 YAML

在现有 `get_template_info` 网关接口上增加 `format` 查询参数（`json` / `yaml`，默认 `json`）。当 `format=yaml` 时，响应结构不变，仅将 `pipeline_tree` 字段从 JSON 对象替换为转换后的 YAML schema 字符串（与页面导出文件内容一致）。

### 请求参数变更

`IncludeTemplateSerializer` 新增字段：

```python
format = serializers.ChoiceField(
    required=False,
    choices=["json", "yaml"],
    default="json",
    help_text="pipeline_tree 的返回格式",
)
```

### 响应结构

`format=json`（默认）：行为不变，`pipeline_tree` 为 JSON 对象。

`format=yaml`：`pipeline_tree` 为 YAML schema 字符串，其余字段不变。

```json
{
  "result": true,
  "data": {
    "id": 123,
    "name": "示例流程",
    "pipeline_tree": "schema_version: v1\nmeta:\n  name: 示例流程\nspec:\n  nodes:\n  - ...\n",
    "project_id": 1,
    "..."
  }
}
```

### 处理逻辑

`format=yaml` 时：

1. 调用 `TaskTemplate.objects.export_templates([template_id], project_id=project.id)` 获取导出数据
2. 调用 `YamlSchemaConverterHandler("v1").convert(templates_data)` 转换为 YAML schema
3. `yaml.dump_all(yaml_data, ...)` 序列化为字符串
4. 替换 `data["pipeline_tree"]` 为该字符串

### 涉及文件

| 文件 | 变更 |
|---|---|
| `gcloud/apigw/serializers.py` | `IncludeTemplateSerializer` 增加 `format` 字段 |
| `gcloud/apigw/views/get_template_info.py` | 读取 `format`，`yaml` 时走转换逻辑 |
| `apigw/bk_apigw_resources_bk-sops_mcp_supplement.yaml` | 网关资源定义补充 `format` 参数 |
| `docs/apidoc/zh_hans/get_template_info.md` | 中文文档补充说明 |
| `docs/apidoc/en/get_template_info.md` | 英文文档补充说明 |

### 注意事项

- `format=yaml` 时 `pipeline_tree` 已为字符串，`mcp_apigw` 的 `trim_pipeline_tree` 裁剪需兼容（判断类型跳过）。
- 转换失败时返回错误 JSON 响应，不影响默认行为。
- 仅支持项目模板（`template_source=project`），公共模板走 `get_common_template_info` 暂不涉及。

---

## 方案二：create_template 导入 YAML

在现有 `create_template` 网关接口的请求体中增加 `format` 参数（`json` / `yaml`，默认 `json`）。当 `format=yaml` 时，`pipeline_tree` 字段接受 YAML schema 字符串（与页面导出格式、`get_template_info` 导出格式一致），服务端自动解析并 reconvert 为内部 pipeline_tree 结构。

### 请求参数变更

请求体新增字段：

```
format: string, 可选, 默认 "json"
  - json: pipeline_tree 为 JSON 对象或 JSON 字符串（现有行为不变）
  - yaml: pipeline_tree 为 YAML schema 字符串（含 schema_version/meta/spec 结构）
```

### 处理逻辑

`format=yaml` 时：

1. 校验 `pipeline_tree` 必须为字符串类型
2. 调用 `YamlSchemaConverterHandler("v1").load_yaml_docs(pipeline_tree)` 解析 YAML 文档
3. 调用 `converter_handler.reconvert(yaml_docs)` 将 YAML schema 还原为内部导入格式
4. 从 reconvert 结果中提取第一个模板的 `tree` 作为 `pipeline_tree`
5. 若请求未指定 `name` / `description`，从 YAML meta 中自动提取

`format=json`（默认）：现有逻辑不变。

### 响应结构

与现有 `create_template` 响应一致，不做变更。

### 涉及文件

| 文件 | 变更 |
|---|---|
| `gcloud/apigw/views/create_template.py` | 读取 `format`，`yaml` 时走 load_yaml_docs + reconvert 逻辑 |
| `apigw/bk_apigw_resources_bk-sops_create_template.yaml` | 网关资源定义增加 `format` 参数，`pipeline_tree` 改为 oneOf |
| `docs/apidoc/zh_hans/create_template.md` | 中文文档补充 `format` 参数说明 |
| `docs/apidoc/en/create_template.md` | 英文文档补充 `format` 参数说明 |

### 注意事项

- YAML 导入仅支持单模板场景：取 `template_order` 中第一个模板进行创建。
- `name` 和 `description` 的优先级：请求体参数 > YAML meta 中的值 > 默认值。
- reconvert 失败时返回错误 JSON 响应，不影响默认的 JSON 导入行为。
