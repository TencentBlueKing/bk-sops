

`pipeline_tree` 是标准运维在前端画布、模板存储、任务创建、执行预览和引擎实例化之间传递流程定义的核心协议。它描述的是“Web 侧流程树”，不是最终进入 bamboo engine 的内部执行树。后端会在保存、预览或创建任务时把 Web 侧结构转换成引擎结构。

本文基于当前前后端代码整理，重点回答四类问题：

- 一个可保存、可编辑的 `pipeline_tree` 必须长什么样。
- 哪些字段是前端画布协议，哪些字段会进入后端执行语义。
- 前端保存校验、后端模板校验、任务创建转换分别检查什么。
- 常见脏数据应如何修复。

## 代码地图

主要入口：

源码地址：https://github.com/TencentBlueKing/bk-sops/tree/master

- 前端协议 schema：`frontend/desktop/src/constants/pipelineTreeSchema.js`
- 前端附加校验：`frontend/desktop/src/utils/validatePipeline.js`
- 前端模板状态读写：`frontend/desktop/src/store/modules/template.js`
- 前端变量编辑：`frontend/desktop/src/pages/template/TemplateEdit/TemplateSetting/TabGlobalVariables/`
- 前端节点输入/输出变量勾选：`frontend/desktop/src/pages/template/TemplateEdit/NodeConfig/InputParams.vue`、`OutputParams.vue`
- 后端 Web tree schema：`pipeline_web/parser/schemas.py`
- 后端 Web tree 校验：`pipeline_web/parser/validator.py`
- Web tree 到引擎 tree 转换：`pipeline_web/parser/format.py`
- 模板保存/读取清洗：`pipeline_web/parser/clean.py`、`pipeline_web/wrapper.py`、`gcloud/template_base/models.py`
- 模板创建/更新领域逻辑：`gcloud/template_base/domains/template_manager.py`
- 任务创建和实例化：`gcloud/apigw/views/create_task.py`、`gcloud/apigw/validators/fast_create_task.py`、`gcloud/taskflow3/models.py`
- 执行方案/可选节点预览：`pipeline_web/preview_base.py`
- AI 简化流程转 `pipeline_tree`：`gcloud/utils/flow_converter.py`、`gcloud/tasktmpl3/agent_utils.py`

## 协议分层

同一个“流程”在代码中有三层常见形态。

### 1. 页面完整对象

AI 生成、模板编辑页或接口返回时，常见数据会包含：

- `name`
- `template_id`
- `projectBaseInfo`
- `notify_receivers`
- `notify_type`
- `time_out`
- `category`
- `description`
- `executor_proxy`
- `template_labels`
- `subprocess_info`
- `internalVariable`
- `default_flow_type`
- `webhook_configs`
- `enable_webhook`
- `activities / constants / flows / line / location / start_event / end_event / gateways / outputs`

这不是纯粹的 `pipeline_tree`。其中只有最后这一组画布和流程结构字段会被前端保存为 `pipeline_tree`。

`internalVariable`、`projectBaseInfo`、通知配置、执行代理人、超时时间等是模板页面或模板模型的辅助字段，不属于保存进 `pipeline_tree` 的主体。

### 2. 前端保存的 Web pipeline_tree

前端 `saveTemplateData` 保存前会组装：

```json
{
  "activities": {},
  "constants": {},
  "end_event": {},
  "flows": {},
  "gateways": {},
  "line": [],
  "location": [],
  "outputs": [],
  "start_event": {}
}
```

这是前端保存校验的最小顶层结构。前端 schema 要求这些字段全部存在。

保存时还会做两件事：

- `location` 会被剔除冗余字段，只保留 `id/type/name/stage_name/x/y/group/icon`。
- `gateways.default_condition` 对应的默认分支 condition 会被从 `conditions` 中剔除。

因此，节点的执行配置不要只写在 `location` 里；`activities` 和 `gateways` 才是流程语义源。

### 3. 引擎内部 pipeline tree

后端在创建模板或任务实例时，会通过 `format_web_data_to_pipeline` 把 Web tree 转成引擎 tree：

- 顶层 `constants` 会转成 `data.inputs`。
- 顶层 `outputs` 会转成 `data.outputs`。
- `ServiceActivity.component.data` 会转成 `ServiceActivity.component.inputs`。
- `component_outputs` 类型变量会转成节点 `global_outputs`。
- `SubProcess.constants` 会转成子流程 `params`，并递归转换子流程 `pipeline`。

所以不要把 Web tree 和执行实例中的 engine tree 混用。

## 顶层字段

| 字段 | 类型 | 前端保存 | 后端模板校验 | 说明 |
| --- | --- | --- | --- | --- |
| `activities` | object | 必填 | 必填 | 任务节点和子流程节点，key 为节点 ID |
| `constants` | object | 必填 | 必填 | 用户定义的全局变量，不包含系统变量/项目变量 |
| `flows` | object | 必填 | 运行图必需 | 执行图边，key 为线 ID |
| `gateways` | object | 必填 | 必填 | 分支、并行、汇聚网关 |
| `line` | array | 必填 | API 响应常会剔除 | 前端画布线段，和 `flows` 同 ID |
| `location` | array | 必填 | API 响应常会剔除 | 前端画布节点坐标 |
| `start_event` | object | 必填 | 必填 | 开始事件 |
| `end_event` | object | 必填 | 必填 | 结束事件 |
| `outputs` | array | 必填 | 必填 | 暴露给父流程/外部引用的全局变量 key 列表 |

后端 `validate_web_pipeline_tree` 的 schema 对 `line/location` 不敏感，因为它们是 Web 渲染字段；API 获取模板信息时也会经常移除 `line/location`。但是前端模板编辑页保存要求二者存在。

## ID 规范

前端 schema 的 ID 正则比后端更严格：

- 节点 ID：以 `n` 开头即可匹配，例如 `nodexxxx`、`nxxxx`。
- 线 ID：以 `l` 开头即可匹配，例如 `linexxxx`、`lxxxx`。
- 变量 key：`${xxx}` 格式，前端 schema 允许点号和下划线。

实际前端默认生成：

- 节点：`node` + uuid
- 线：`line` + uuid

旧数据如果 ID 不是字母开头，前端 `setPipelineTree` 会通过 `nodeFilter.convertInvalidIdData` 尝试替换成合法 ID，并同步替换节点引用、线引用和网关条件 key。

后端变量 key 规则更严格：自定义模板变量不能使用 `${_env_xxx}` 或 `${_system.xxx}` 这类系统/项目变量命名空间。系统变量和项目变量通过运行时 context 注入，不应该保存到 `constants`。

## 节点和连线关系

`pipeline_tree` 同时维护两份边信息：

- `flows`：执行语义边，后端校验和引擎转换依赖它。
- `line`：画布线，前端渲染依赖它。

二者必须同步，且节点的 `incoming/outgoing` 必须指向 `flows` 中存在的线。

### flows

```json
"flows": {
  "lineabc": {
    "id": "lineabc",
    "is_default": false,
    "source": "node1",
    "target": "node2"
  }
}
```

字段说明：

- `id` 必须等于对象 key。
- `source` 是源节点 ID。
- `target` 是目标节点 ID。
- `is_default` 前端 schema 必填，普通连线通常为 `false`。

### line

```json
"line": [
  {
    "id": "lineabc",
    "source": { "id": "node1", "arrow": "Right" },
    "target": { "id": "node2", "arrow": "Left" }
  }
]
```

`line` 是画布渲染数据。`source.id/target.id` 应与同 ID 的 `flows[id].source/target` 一致。

### incoming / outgoing

节点中的 `incoming/outgoing` 保存的是 flow ID：

- `start_event.incoming` 固定为空字符串。
- `start_event.outgoing` 指向唯一输出 flow。
- `end_event.incoming` 是一个 flow 或 flow 数组。
- `end_event.outgoing` 固定为空字符串。
- 普通任务节点和子流程节点：`incoming` 可为字符串或数组，`outgoing` 通常为字符串。
- 分支、并行、条件并行网关：`outgoing` 为数组。
- 汇聚网关：`incoming` 为数组，`outgoing` 为字符串。

前端附加校验会逐个检查：

- 节点 `incoming/outgoing` 中的 flow 是否存在。
- flow 的 `source/target` 是否与节点 ID 一致。
- 画布连线数量是否满足节点类型规则。
- 并行网关/条件并行网关是否能在后续路径汇聚。

## location

`location` 只负责前端画布位置和节点显示。

```json
{
  "id": "node1",
  "type": "tasknode",
  "name": "节点名",
  "x": 100,
  "y": 200
}
```

常见 `type`：

- `startpoint`
- `endpoint`
- `tasknode`
- `subflow`
- `branchgateway`
- `parallelgateway`
- `conditionalparallelgateway`
- `convergegateway`

保存时 `location` 会被“瘦身”，不要依赖 `location.optional`、`location.retryable`、`location.auto_retry` 这类字段作为最终语义。加载模板时，前端会从 `activities` 把这些字段复制到 `location` 用于展示。

## 事件节点

### start_event

```json
{
  "id": "node_start",
  "incoming": "",
  "name": "",
  "outgoing": "line_start_to_first",
  "type": "EmptyStartEvent"
}
```

必填字段：`id/name/type/outgoing`。前端 schema 还要求 `incoming` 为空字符串。

### end_event

```json
{
  "id": "node_end",
  "incoming": ["line_last_to_end"],
  "name": "",
  "outgoing": "",
  "type": "EmptyEndEvent"
}
```

必填字段：`id/name/type/incoming`。前端 schema 还要求 `outgoing` 为空字符串。

## ServiceActivity

普通任务节点示例：

```json
{
  "id": "node_task",
  "name": "执行脚本",
  "type": "ServiceActivity",
  "incoming": ["line_prev"],
  "outgoing": "line_next",
  "optional": true,
  "component": {
    "code": "job_fast_execute_script",
    "version": "v2.1",
    "data": {
      "job_content": {
        "hook": false,
        "value": "echo hello"
      }
    }
  },
  "error_ignorable": false,
  "retryable": true,
  "skippable": true,
  "stage_name": "",
  "auto_retry": {
    "enable": false,
    "interval": 0,
    "times": 1
  },
  "timeout_config": {
    "enable": false,
    "seconds": 10,
    "action": "forced_fail"
  },
  "labels": [],
  "loop": null
}
```

关键字段：

- `optional`：前端保存必填；执行方案/可选节点裁剪会读取它。`false` 表示不可被执行方案排除。
- `component.code`：标准插件 code。
- `component.version`：插件版本；旧数据缺失时导入逻辑可能补 `legacy`，但新数据应显式带上。
- `component.data`：标准插件表单值，后端要求每个字段至少是 `{ hook, value }`。
- `retryable/skippable`：新字段。
- `can_retry/isSkipped`：旧字段。前端兼容旧数据，但新数据应使用 `retryable/skippable`。
- `error_ignorable`：失败是否可忽略。
- `auto_retry`：节点自动重试配置。
- `timeout_config`：节点超时配置。
- `labels`：节点标签。保存到 pipeline 模板时会被清理并单独存储到 `NodeInTemplate/NodeAttr`，读取时再还原。

注意：

- `timeout_config.enable=true` 不能同时开启 `error_ignorable=true` 或 `auto_retry.enable=true`，后端转换会拒绝。
- 节点执行代理人如果配置了 `executor_proxy`，转换时会注入到 `component.inputs.__executor_proxy`。
- `component.data` 中的简单值不能直接写成 `"xxx"`，应该包成 `{ "hook": false, "value": "xxx" }`。AI 转换器会自动包装。

## SubProcess

子流程节点示例：

```json
{
  "id": "node_sub",
  "name": "子流程",
  "type": "SubProcess",
  "template_id": "12345",
  "template_source": "business",
  "version": "v1",
  "constants": {
    "${sub_param}": {
      "key": "${sub_param}",
      "name": "子流程入参",
      "value": "abc",
      "source_type": "custom",
      "custom_type": "input",
      "source_tag": "input.input",
      "source_info": {},
      "show_type": "show",
      "desc": "",
      "validation": "^.+$",
      "index": 0
    }
  },
  "incoming": ["line_prev"],
  "outgoing": "line_next",
  "optional": true,
  "retryable": true,
  "skippable": true,
  "always_use_latest": false,
  "scheme_id_list": []
}
```

字段说明：

- `template_id`：前端和 API 外部看到的是上层模板 ID；保存到 pipeline 层前，后端会转换为 `PipelineTemplate.template_id`。读取时再反向转换。
- `template_source`：`business/project` 或 `common`，用于决定从项目流程还是公共流程查子流程。
- `version`：子流程版本。`always_use_latest=true` 时，展开时会忽略固定版本，取最新版本。
- `constants`：父流程传给子流程的参数集合。只要子流程变量 `show_type=show`，转换时会作为子流程 `params` 传入。
- `pipeline`：不是模板编辑态必填字段。创建任务或展开子流程时，后端会把子流程完整 tree 写入 `act.pipeline`。
- `hooked_constants`、`scheme_id_list` 等字段用于前端展示和执行方案处理。

展开子流程时，后端会：

- 读取子流程对应版本的 `pipeline_tree`。
- 用父节点 `constants` 覆盖子流程中对外暴露的变量。
- 根据 `scheme_id_list` 裁剪子流程节点。
- 递归展开下级子流程。
- 注入 `template_node_id`、`original_template_id`、`original_template_version` 等实例执行辅助信息。

## 网关

网关节点保存在 `gateways`。

### ExclusiveGateway

```json
{
  "id": "node_gateway",
  "name": "分支网关",
  "type": "ExclusiveGateway",
  "incoming": ["line_in"],
  "outgoing": ["line_a", "line_b"],
  "conditions": {
    "line_a": {
      "evaluate": "${flag} == \"yes\""
    },
    "line_b": {
      "evaluate": "True"
    }
  }
}
```

`conditions` 的 key 必须对应 outgoing flow ID。每个 condition 至少需要 `evaluate`。

### ConditionalParallelGateway

结构与 `ExclusiveGateway` 类似，也有 `conditions`，但语义是满足条件的分支并行执行。

### ParallelGateway

```json
{
  "id": "node_parallel",
  "name": "并行网关",
  "type": "ParallelGateway",
  "incoming": ["line_in"],
  "outgoing": ["line_a", "line_b"]
}
```

### ConvergeGateway

```json
{
  "id": "node_converge",
  "name": "汇聚网关",
  "type": "ConvergeGateway",
  "incoming": ["line_a", "line_b"],
  "outgoing": "line_out"
}
```

前端附加校验会沿 `line` 拓扑检查并行/条件并行网关是否存在有效汇聚路径，而不是只看 `converge_gateway_id` 字段。

## constants

`constants` 是用户模板变量集合。系统变量和项目变量不应保存到这里。

标准变量示例：

```json
"${biz_id}": {
  "key": "${biz_id}",
  "name": "业务 ID",
  "index": 0,
  "custom_type": "input",
  "source_type": "custom",
  "source_tag": "input.input",
  "source_info": {},
  "show_type": "show",
  "desc": "",
  "validation": "^.+$",
  "value": "",
  "form_schema": {},
  "version": "legacy",
  "pre_render_mako": false,
  "is_condition_hide": "false"
}
```

前端 schema 必填：

- `custom_type`
- `desc`
- `index`
- `key`
- `name`
- `show_type`
- `source_info`

后端执行语义常用：

- `source_type`
- `source_tag`
- `validation`
- `value`
- `is_meta`
- `meta`
- `pre_render_mako`
- `need_render`

### source_type

| source_type | 含义 | 典型来源 |
| --- | --- | --- |
| `custom` | 用户手动新增变量 | 全局变量面板“新建” |
| `component_inputs` | 节点输入参数勾选为全局变量 | 节点配置输入参数勾选 |
| `component_outputs` | 节点输出参数勾选为全局变量 | 节点配置输出参数勾选 |
| `system` | 系统变量 | 运行时 context，不建议保存进模板 constants |

前端还会把项目变量合并到 `internalVariable` 并标记为 `source_type=project`，但它也不属于保存的 `constants`。

### custom

手动新增变量默认字段：

```json
{
  "custom_type": "input",
  "desc": "",
  "form_schema": {},
  "show_type": "show",
  "source_info": {},
  "source_tag": "input.input",
  "source_type": "custom",
  "validation": "^.+$",
  "is_condition_hide": "false",
  "pre_render_mako": "",
  "value": "",
  "version": "legacy"
}
```

`show_type=show` 表示创建任务时作为入参展示；`hide` 表示流程内部使用。

### component_inputs

节点输入参数勾选成全局变量时，默认字段：

```json
{
  "source_type": "component_inputs",
  "show_type": "show",
  "source_info": {
    "node_id": ["form_tag_code"]
  },
  "source_tag": "plugin_code.form_tag_code"
}
```

意义：

- `source_info` 表示这个变量绑定了哪个节点的哪个输入表单项。
- 节点表单中的值会替换成该变量 key。
- 复制节点时，`component_inputs` 变量会复用，并给新节点追加 `source_info`。

### component_outputs

节点输出参数勾选成全局变量时，默认字段：

```json
{
  "source_type": "component_outputs",
  "show_type": "hide",
  "custom_type": "",
  "source_tag": "",
  "source_info": {
    "node_id": ["output_key"]
  },
  "value": ""
}
```

转换成引擎 tree 时，后端只取 `source_info` 的第一个节点和第一个输出 key：

- `source_act = node_id`
- `source_key = output_key`
- 节点 `global_outputs[source_key] = variable_key`

因此输出变量必须有正确的 `source_info`，否则执行时无法把节点输出写入全局变量。

### show_type

- `show`：变量会作为任务入参展示。子流程内 `show` 变量也会成为父流程传参入口。
- `hide`：变量不在创建任务填参页展示，只在流程内部计算或引用。
- `component_outputs` 应固定为 `hide`。

### source_info

`source_info` 的结构是：

```json
{
  "node_id": ["form_tag_or_output_key"]
}
```

它不是“变量被哪些地方引用”的扫描结果，而是变量来源关系：

- `component_inputs`：来源于节点输入参数。
- `component_outputs`：来源于节点输出参数。
- `custom`：通常为空。

变量被哪些节点/网关/变量引用，由后端 `analysis_pipeline_constants_ref` 扫描 `component.data`、网关条件和变量默认值动态计算。

### value 和引用语法

变量引用语法是 `${key}`。节点参数、网关条件、变量默认值都可以引用变量。

后端会校验：

- 常量不能自引用。
- 常量之间不能循环引用。
- 自定义变量 key 必须与对象 key 一致。
- `outputs` 中的 key 必须满足变量 key 规则。

系统变量和项目变量由 context 注入：

- 系统变量上下文形式：`${_system.task_id}`、`${_system.executor}` 等。
- 项目变量上下文形式：`${_env_xxx}`。

它们可以被引用，但不应作为模板自定义变量存入 `constants`。

### pre_render_mako

`pre_render_mako=true` 的非输出变量会被转换到引擎 tree 的 `data.pre_render_keys`。这类变量在任务启动时预渲染，后续使用保持启动时的值。

## outputs

`outputs` 是变量 key 数组：

```json
"outputs": ["${result}"]
```

含义：

- 当该流程被其他流程作为子流程引用时，`outputs` 中的变量可作为子流程输出。
- `outputs` 中的 key 必须存在于 `constants`。
- 预览裁剪可选节点时，未被引用的输出可能被移除；若设置 `remove_outputs_without_refs=false`，自定义输出变量会被保留。

## 系统变量和项目变量

系统变量由 `/taskflow/api/context/` 提供，前端通过 `loadInternalVariable` 加载。典型字段：

- `${_system.task_url}`
- `${_system.task_start_time}`
- `${_system.language}`
- `${_system.bk_biz_id}`
- `${_system.bk_biz_name}`
- `${_system.operator}`
- `${_system.executor}`
- `${_system.task_id}`
- `${_system.task_name}`

项目变量由 `api/v3/project_constants/` 加载，前端会转成 `${_env_key}` 并与系统变量一起放入 `internalVariable`。

保存模板时：

- `internalVariable` 不会进入 `pipeline_tree.constants`。
- 任务执行时，后端通过 `get_instance_context` 和 `get_project_constants_context` 注入系统/项目 context。

如果把 `${_system.xxx}` 或 `${_env_xxx}` 写进 `constants`，前端详情可能能展示，但后端模板保存或变量 key 校验容易失败。

## 前端加载和保存流程

### 加载模板

`setTemplateData` 会解析接口返回的 `pipeline_tree` 并调用 `setPipelineTree`。

`setPipelineTree` 会做兼容处理：

- 如果 tree 中有 `name`，同步到模板名。
- 修正 `constants.index`，按当前排序重新从 0 编号。
- 修复旧数据中不合法的节点/线 ID。
- 对旧节点补 `can_retry/isSkipped`，兼容没有 `retryable/skippable` 的数据。
- 将 `activities` 中的 `name/stage_name/optional/error_ignorable/retryable/skippable/auto_retry/timeout_config` 同步到 `location` 展示层。

注意：它不会补 `optional`、`desc`、`show_type` 等 schema 必填字段。脏数据缺字段时，详情页或保存校验仍会报错。

### 保存模板

`saveTemplateData` 会：

1. 从 Vuex state 取 `activities/constants/end_event/flows/gateways/line/location/outputs/start_event`。
2. 精简 `location`。
3. 精简默认分支条件。
4. 调用 `validatePipeline.isPipelineDataValid`。
5. 将 fullCanvasData JSON.stringify 后作为 `pipeline_tree` 提交到模板 API。

前端保存校验包含：

- AJV schema 校验。
- `incoming/outgoing` 与 `flows` 一致性校验。
- 并行/条件并行网关汇聚校验。

模板编辑保存前的画布操作还会调用节点连线数校验：

- 开始节点只能一个输出。
- 结束节点至少一个输入、无输出。
- 普通任务/子流程至少一个输入和一个输出。
- 分支/并行类网关至少一个输入和一个输出。
- 汇聚网关至少一个输入和一个输出。

## 后端模板保存和读取

模板创建/更新时，后端会：

1. `standardize_pipeline_node_name` 截断/规范节点名。
2. `validate_web_pipeline_tree` 执行后端 schema 校验。
3. 校验 `constants` key 与对象内 `key` 一致。
4. 校验变量 key 正则和输出 key 正则。
5. 校验常量自引用和循环引用。
6. 调用 pipeline 层 `validate_pipeline_tree` 校验流程图。
7. 将子流程 `template_id` 从外部模板 ID 转换为 pipeline template ID。
8. 用 `PipelineWebTreeCleaner.clean` 清理节点属性，如 `labels`，并写入 `NodeInTemplate`。
9. 创建或更新 `PipelineTemplate`。

读取模板时，后端会：

- 从 `PipelineTemplate.data` 取结构。
- 将子流程 `template_id` 转回用户可见模板 ID。
- 从 `NodeInTemplate/NodeAttr` 还原节点属性到 Web tree。

## 任务创建和执行转换

任务创建有两类路径。

### 基于模板创建任务

通常路径：

1. 读取 `tmpl.pipeline_tree`。
2. 根据执行方案或指定节点列表裁剪可选节点。
3. 用创建任务传入的 `constants` 覆盖模板变量默认值。
4. 处理 meta 变量和简化变量。
5. 创建 pipeline instance。

### 一次性 pipeline_tree 创建任务

APIGW `create_task` 可以直接传 `pipeline_tree`，`fast_create_task` 也使用这个模式。它会：

- 对传入 `pipeline_tree` 做 `standardize_pipeline_node_name`。
- 必要时自动 `draw_pipeline` 补布局。
- 校验 `validate_web_pipeline_tree`。
- 创建一次性任务实例。

`fast_create_task` 会在校验前对 `gateways/constants/outputs` 做 `setdefault`，但这不代表前端编辑页可以缺这些字段。前端保存仍要求完整字段。

### 实例化时的转换

`TaskFlowInstance.objects.create_pipeline_instance` 会：

1. 可选地把子流程转成独立子任务。
2. 将子流程 `template_id` 转为 pipeline template ID。
3. 展开所有子流程到 `act.pipeline`。
4. 注入 `template_node_id`。
5. 清理并保存节点属性。
6. 注入原始模板信息。
7. 调用 pipeline engine 创建实例。
8. 创建 `NodeInInstance`。

在这个阶段，Web tree 会被转换为引擎 tree，`constants/component.data/outputs` 的语义才真正进入执行上下文。

## 执行方案和可选节点预览

`optional` 是执行方案处理的关键字段。

- 执行方案给出要执行的节点集合。
- `PipelineTemplateWebPreviewer.get_template_exclude_task_nodes_with_schemes` 会把不在方案里的活动节点加入排除列表。
- `optional=false` 的节点会从排除列表中移除，保证一定执行。
- 裁剪时如果试图排除 `optional=false` 节点，会抛错。

裁剪可选节点时，后端会：

- 删除被排除的 activity。
- 把该节点的 incoming flows 重定向到后继节点。
- 删除该节点 outgoing flow。
- 同步调整 `line/location`。
- 删除无用并行/汇聚网关。
- 扫描剩余节点、网关条件、变量默认值引用，重建 `constants` 和 `outputs`。

因此，缺失 `optional` 不只是前端保存问题，也会影响执行方案预览和任务创建。

## AI 生成流程和简化格式转换

AI 生成流程先拿到简化数组，再由 `SimpleFlowConverter` 转成完整 `pipeline_tree`。

转换器会：

- 生成合法节点 ID 和 flow ID。
- 生成 `flows` 并填 `is_default=false`。
- 构造 `start_event/end_event/activities/gateways`。
- 给普通节点补默认执行配置：
  - `auto_retry`
  - `timeout_config`
  - `error_ignorable`
  - `retryable`
  - `skippable`
  - `optional`
  - `labels`
  - `loop`
- 把组件 data 中的简单值包装为 `{ hook, need_render, value }`。
- 对 `remote_plugin` 补齐框架字段和 `plugin_code/plugin_version`。
- 给变量补齐 `desc/custom_type/source_type/source_tag/source_info/show_type/validation/form_schema/version`。
- 调用 `draw_pipeline` 自动排版，生成 `line/location`。

AI 转换器返回的对象通常包含页面完整对象字段。用于保存时，仍应按 Web `pipeline_tree` 主体字段裁剪。

## 最小可编辑模板示例

下面是只有一个任务节点的最小结构示例：

```json
{
  "activities": {
    "node_task": {
      "id": "node_task",
      "name": "任务节点",
      "type": "ServiceActivity",
      "incoming": ["line_start_task"],
      "outgoing": "line_task_end",
      "optional": true,
      "component": {
        "code": "job_fast_execute_script",
        "version": "v2.1",
        "data": {
          "job_content": {
            "hook": false,
            "value": "echo hello"
          }
        }
      },
      "error_ignorable": false,
      "retryable": true,
      "skippable": true,
      "stage_name": "",
      "auto_retry": {
        "enable": false,
        "interval": 0,
        "times": 1
      },
      "timeout_config": {
        "enable": false,
        "seconds": 10,
        "action": "forced_fail"
      },
      "labels": [],
      "loop": null
    }
  },
  "constants": {},
  "end_event": {
    "id": "node_end",
    "incoming": ["line_task_end"],
    "name": "",
    "outgoing": "",
    "type": "EmptyEndEvent"
  },
  "flows": {
    "line_start_task": {
      "id": "line_start_task",
      "is_default": false,
      "source": "node_start",
      "target": "node_task"
    },
    "line_task_end": {
      "id": "line_task_end",
      "is_default": false,
      "source": "node_task",
      "target": "node_end"
    }
  },
  "gateways": {},
  "line": [
    {
      "id": "line_start_task",
      "source": { "id": "node_start", "arrow": "Right" },
      "target": { "id": "node_task", "arrow": "Left" }
    },
    {
      "id": "line_task_end",
      "source": { "id": "node_task", "arrow": "Right" },
      "target": { "id": "node_end", "arrow": "Left" }
    }
  ],
  "location": [
    {
      "id": "node_start",
      "type": "startpoint",
      "name": "",
      "x": 60,
      "y": 100
    },
    {
      "id": "node_task",
      "type": "tasknode",
      "name": "任务节点",
      "x": 260,
      "y": 100
    },
    {
      "id": "node_end",
      "type": "endpoint",
      "name": "",
      "x": 460,
      "y": 100
    }
  ],
  "outputs": [],
  "start_event": {
    "id": "node_start",
    "incoming": "",
    "name": "",
    "outgoing": "line_start_task",
    "type": "EmptyStartEvent"
  }
}
```

## 常见脏数据和修复清单

### 1. 点击变量详情时报 `desc.length`

原因：`constants` 变量缺少 `desc`。

修复：给所有变量补 `desc: ""`。

### 2. 保存时报 `activities[...] should have required property 'optional'`

原因：`activities` 中活动节点缺 `optional`。`location.optional` 不算。

修复：给每个 `activities` 下的 `ServiceActivity/SubProcess` 补 `optional: true` 或按业务要求补 `false`。

### 3. 保存时报 flow 缺 `is_default`

原因：前端 `pipelineTreeSchema` 要求 `flows.*.is_default`。

修复：普通连线补 `is_default: false`。

### 4. 画布能显示但保存失败

常见原因：

- `line` 与 `flows` 不一致。
- 节点 `incoming/outgoing` 指向不存在的 flow。
- flow 的 `source/target` 与节点引用不匹配。
- `location` 里有节点，但 `activities/gateways/start_event/end_event` 中没有对应语义节点。

修复原则：以 `flows` 和节点 `incoming/outgoing` 为执行图源，重新同步 `line/location`。

### 5. API 返回的 `pipeline_tree` 不能直接粘到前端保存

原因：APIGW/MCP 响应可能裁剪掉 `line/location`，也可能裁剪一些前端渲染字段。

修复：用于前端编辑时，需要补齐 `line/location`。可以调用自动排版接口或用 `draw_pipeline` 生成。

### 6. 把系统变量/项目变量写进 constants

原因：混淆了 `constants` 和 `internalVariable`。

修复：

- 从 `constants` 删除 `${_system.xxx}`、`${_env_xxx}`。
- 在节点参数、网关条件、变量默认值中直接引用它们即可。
- 系统/项目变量由前端列表展示和后端运行时 context 注入。

### 7. component_outputs 变量缺 source_info

原因：只创建了变量 key，没有记录输出来源。

修复：

```json
"source_type": "component_outputs",
"show_type": "hide",
"source_info": {
  "node_id": ["output_key"]
}
```

否则后端无法生成节点 `global_outputs`。

### 8. component.data 直接写简单值

原因：绕过前端或转换器手工构造。

修复：

```json
"field": {
  "hook": false,
  "value": "实际值"
}
```

如需保持变量引用渲染，建议同时补 `need_render: true`。

### 9. 子流程 template_id 不匹配

原因：外部模板 ID 与 pipeline template ID 混用。

修复：

- Web/API 输入输出一般使用上层 `TaskTemplate.id` 或 `CommonTemplate.id`。
- 模板保存和任务实例化时后端会自动转换为 `PipelineTemplate.template_id`。
- 不要手工把两种 ID 混在同一份 tree 中。

### 10. 默认分支条件保存后丢失

原因：前端保存时会删除 `default_condition.flow_id` 对应的 `conditions[line_id]`。

修复：这是设计行为。默认分支语义应依赖 `default_condition`，不要把默认分支条件当作普通 `conditions` 持久语义。

## 自动修复参考脚本

以下脚本只补规范字段，不增减节点和参数。适合修复旧数据或 AI 拼装数据：

```js
function normalizePipelineTree(tree) {
  Object.values(tree.activities || {}).forEach((node) => {
    if (!Object.prototype.hasOwnProperty.call(node, 'optional')) {
      node.optional = true
    }
    if (node.type === 'ServiceActivity') {
      if (!Object.prototype.hasOwnProperty.call(node, 'error_ignorable')) {
        node.error_ignorable = false
      }
      if (!Object.prototype.hasOwnProperty.call(node, 'retryable')) {
        node.retryable = Object.prototype.hasOwnProperty.call(node, 'can_retry') ? node.can_retry : true
      }
      if (!Object.prototype.hasOwnProperty.call(node, 'skippable')) {
        node.skippable = Object.prototype.hasOwnProperty.call(node, 'isSkipped') ? node.isSkipped : true
      }
      node.auto_retry = node.auto_retry || { enable: false, interval: 0, times: 1 }
      node.timeout_config = node.timeout_config || { enable: false, seconds: 10, action: 'forced_fail' }
      node.labels = node.labels || []
      if (!Object.prototype.hasOwnProperty.call(node, 'loop')) {
        node.loop = null
      }
      Object.values(node.component?.data || {}).forEach((item) => {
        if (!Object.prototype.hasOwnProperty.call(item, 'hook')) {
          item.hook = false
        }
        if (!Object.prototype.hasOwnProperty.call(item, 'value')) {
          item.value = ''
        }
      })
    }
  })

  Object.values(tree.flows || {}).forEach((flow) => {
    if (!Object.prototype.hasOwnProperty.call(flow, 'is_default')) {
      flow.is_default = false
    }
  })

  Object.values(tree.constants || {}).forEach((variable) => {
    if (!Object.prototype.hasOwnProperty.call(variable, 'desc')) {
      variable.desc = ''
    }
    if (!Object.prototype.hasOwnProperty.call(variable, 'custom_type')) {
      variable.custom_type = ''
    }
    if (!Object.prototype.hasOwnProperty.call(variable, 'source_info')) {
      variable.source_info = {}
    }
    if (!Object.prototype.hasOwnProperty.call(variable, 'show_type')) {
      variable.show_type = variable.source_type === 'component_outputs' ? 'hide' : 'show'
    }
    if (!Object.prototype.hasOwnProperty.call(variable, 'source_tag')) {
      if (variable.source_type === 'custom' && ['input', 'textarea'].includes(variable.custom_type)) {
        variable.source_tag = `${variable.custom_type}.${variable.custom_type}`
      } else {
        variable.source_tag = ''
      }
    }
    if (!Object.prototype.hasOwnProperty.call(variable, 'validation')) {
      variable.validation = variable.custom_type === 'input'
        ? '^.+$'
        : variable.custom_type === 'textarea'
          ? '^[\\s\\S]+$'
          : ''
    }
    if (!Object.prototype.hasOwnProperty.call(variable, 'value')) {
      variable.value = ''
    }
    if (!Object.prototype.hasOwnProperty.call(variable, 'form_schema')) {
      variable.form_schema = {}
    }
  })

  tree.gateways = tree.gateways || {}
  tree.constants = tree.constants || {}
  tree.outputs = tree.outputs || []
  tree.line = tree.line || []
  tree.location = tree.location || []

  return tree
}
```

修复脚本不能替代连线一致性校验。补字段后仍应检查：

- `flows` 和 `line` 是否一一对应。
- 节点 `incoming/outgoing` 是否存在于 `flows`。
- `flows.source/target` 是否存在对应节点。
- 非 `input/textarea` 的自定义变量是否补了正确 `source_tag/form_schema`。
- `component_outputs.source_info` 是否指向真实节点输出。
- `outputs` 中所有 key 是否存在于 `constants`。

## 调试建议

排查 `pipeline_tree` 问题时建议按顺序看：

1. 是否是页面完整对象和纯 `pipeline_tree` 混用。
2. 顶层 9 个字段是否齐全。
3. `activities/constants/flows` 是否缺前端 schema 必填字段。
4. `line` 和 `flows` 是否同步。
5. 节点 `incoming/outgoing` 与 `flows.source/target` 是否一致。
6. 变量是否把系统/项目变量误放进 `constants`。
7. `component_outputs` 是否有有效 `source_info`。
8. 子流程 `template_id/template_source/version/constants` 是否与模板类型匹配。
9. 是否经过 APIGW/MCP 裁剪，导致 `line/location` 缺失。
10. 是否是执行方案裁剪导致可选节点、输出变量或 source_info 被重写。