## 1. 知识库概述

### 1.1 文档目标

本知识库旨在为智能体 LLM 提供完整的 bk-sops（蓝鲸标准运维）流程生成指导。通过本知识库，智能体理解用户的自然语言需求，并生成符合 bk-sops 规范的流程模板，最终由后端 Python 渲染器还原为完整的 JSON 格式，供前端画布渲染。

---

## 2. 简化 JSONL 格式规范

### 2.1 格式设计原则

- **扁平化结构**：去除嵌套的 hook 层级，data 直接为 key-value 格式。
- **JSONL 格式**：每行一个 JSON 对象，便于流式生成和解析。

#### 2.1.1 输出必需组件

| 字段 | 类型 | 值 | 示例 |
| - | - | - | - |
| name  | string  | value  | &#96;{"type":"name","value":"xxx"}&#96;  |

### 2.2 组件类型定义

#### 2.2.1 开始节点 (StartEvent)

```json
{"type":"StartEvent","id":"start","name":"流程开始"}
```

| 字段 | 类型 | 必填 | 说明 |
| - | - | - | - |
| type  | string  | 是  | 固定值 &#96;"StartEvent"&#96;  |
| id  | string  | 是  | 固定值 &#96;"start"&#96;  |
| name  | string  | 否  | 节点名称，默认 &#96;"流程开始"&#96;  |

#### 2.2.2 结束节点 (EndEvent)

```json
{"type":"EndEvent","id":"end","name":"流程结束"}
```

| 字段 | 类型 | 必填 | 说明 |
| - | - | - | - |
| type  | string  | 是  | 固定值 &#96;"EndEvent"&#96;  |
| id  | string  | 是  | 固定值 &#96;"end"&#96;  |
| name  | string  | 否  | 节点名称，默认 &#96;"流程结束"&#96;  |

#### 2.2.3 活动节点 (Activity) — 标准插件

```json
{"type":"Activity","id":"n1","name":"执行脚本","code":"job_fast_execute_script"}
```

| 字段 | 类型 | 必填 | 说明 |
| - | - | - | - |
| type  | string  | 是  | 固定值 &#96;"Activity"&#96;  |
| id  | string  | 是  | 短 ID，格式 &#96;n1&#96;/&#96;n2&#96;/&#96;n3&#96;...  |
| name  | string  | 是  | 节点名称  |
| code  | string  | 是  | 插件编码，来自插件获取工具  |

#### 2.2.4 活动节点 (Activity) — 第三方插件 (remote_plugin)

当插件类型为第三方插件时，`code` 固定为 `"remote_plugin"`，需额外指定 `plugin_code` 和 `plugin_version`。

```json
{"type":"Activity","id":"n1","name":"第三方插件name","code":"remote_plugin","plugin_code":"xxx","plugin_version":"1.0.0","data":{"zone":3,"is_pb":false,"pb_path":"","remark":""}}
```

| 字段 | 类型 | 必填 | 说明 |
| - | - | - | - |
| type  | string  | 是  | 固定值 &#96;"Activity"&#96;                                                                                 |
| id  | string  | 是  | 短 ID，格式 &#96;n1&#96;/&#96;n2&#96;/&#96;n3&#96;...                                                                        |
| name  | string  | 是  | 节点名称                                                                                             |
| code  | string  | 是  | 固定值 &#96;"remote_plugin"&#96;，标识为第三方插件                                                                   |
| plugin_code  | string  | 是  | 第三方插件的唯一标识码 code                                                                                 |
| plugin_version  | string  | 是  | 第三方插件版本号（如 &#96;"1.0.0"&#96;）                                                                            |
| data  | object  | 否  | 扁平化键值对，仅填写业务参数；框架字段（&#96;command&#96;、&#96;input&#96;、&#96;session_code&#96;、&#96;chat_history&#96;、&#96;context&#96;）由后端渲染器自动补全，无需手动填写  |

#### 2.2.5 并行网关 (ParallelGateway)

```json
{"type":"ParallelGateway","id":"pg1","name":"并行分发"}
```

| 字段 | 类型 | 必填 | 说明 |
| - | - | - | - |
| type  | string  | 是  | 固定值 &#96;"ParallelGateway"&#96;  |
| id  | string  | 是  | 短 ID，格式 &#96;pg1&#96;/&#96;pg2&#96;/&#96;pg3&#96;...  |
| name  | string  | 否  | 网关名称  |

#### 2.2.6 分支网关 (ExclusiveGateway)

```json
{"type":"ExclusiveGateway","id":"eg1","name":"条件判断","conditions":[{"evaluate":"${status}=='running'","target":"n2"},{"evaluate":"${status}!='running'","target":"n3"}]}
```

| 字段 | 类型 | 必填 | 说明 |
| - | - | - | - |
| type  | string  | 是  | 固定值 &#96;"ExclusiveGateway"&#96;  |
| id  | string  | 是  | 短 ID，格式 &#96;eg1&#96;/&#96;eg2&#96;/&#96;eg3&#96;...  |
| name  | string  | 否  | 网关名称  |
| conditions  | array  | 是  | 条件数组，&#96;evaluate&#96; 为表达式，&#96;target&#96; 为目标节点 ID  |

#### 2.2.7 汇聚网关 (ConvergeGateway)

```json
{"type":"ConvergeGateway","id":"cg1","name":"汇聚"}
```

| 字段 | 类型 | 必填 | 说明 |
| - | - | - | - |
| type  | string  | 是  | 固定值 &#96;"ConvergeGateway"&#96;  |
| id  | string  | 是  | 短 ID，格式 &#96;cg1&#96;/&#96;cg2&#96;/&#96;cg3&#96;...  |
| name  | string  | 否  | 网关名称  |

#### 2.2.8 条件并行网关 (ExclusiveParallelGateway)

```json
{"type":"ExclusiveParallelGateway","id":"epg1","name":"条件并行","conditions":[{"evaluate":"${condition}=='A'","target":"n1"},{"evaluate":"${condition}=='B'","target":"n2"}]}
```

| 字段 | 类型 | 必填 | 说明 |
| - | - | - | - |
| type  | string  | 是  | 固定值 &#96;"ExclusiveParallelGateway"&#96;  |
| id  | string  | 是  | 短 ID，格式 &#96;epg1&#96;/&#96;epg2&#96;/&#96;epg3&#96;...  |
| name  | string  | 否  | 网关名称  |
| conditions  | array  | 是  | 条件数组，&#96;evaluate&#96; 为表达式，&#96;target&#96; 为目标节点 ID  |

#### 2.2.9 连接线 (Link)

```json
{"type":"Link","source":"start","target":"n1"}
{"type":"Link","source":"eg1","target":"n3","is_default":true}
```

| 字段 | 类型 | 必填 | 说明 |
| - | - | - | - |
| type  | string  | 是  | 固定值 &#96;"Link"&#96;  |
| source  | string  | 是  | 源节点 ID  |
| target  | string  | 是  | 目标节点 ID  |
| is_default  | boolean  | 否  | 是否为排他网关默认分支，仅排他网关需要  |

#### 2.2.10 变量 (Variable)

```json
{"type":"Variable","key":"${ip}","name":"目标服务器IP","value":"","source_type":"custom","custom_type":"input","description":"执行脚本的目标服务器IP"}
```

| 字段 | 类型 | 必填 | 说明 |
| - | - | - | - |
| type  | string  | 是  | 固定值 &#96;"Variable"&#96;  |
| key  | string  | 是  | 变量键名，格式 &#96;${变量名}&#96;  |
| name  | string  | 是  | 变量显示名称  |
| value  | string  | 是  | 默认值  |
| source_type  | string  | 是  | 来源类型：&#96;custom&#96; / &#96;component_outputs&#96; / &#96;system&#96;  |
| custom_type  | string  | 否  | 自定义类型（source_type=custom 时）：&#96;input&#96; / &#96;textarea&#96;  |
| description  | string  | 否  | 变量描述  |

---

## 3. ID 简化规则

### 3.1 ID 映射表

| 节点类型 | 原始格式示例 | 简化格式 |
| - | - | - |
| 开始节点  | &#96;n8a9f3e2d1c4b5a6...&#96;  | &#96;start&#96;  |
| 结束节点  | &#96;n7b8c9d0e1f2a3b3...&#96;  | &#96;end&#96;  |
| 任务节点  | &#96;n64a968d6bf13d72...&#96;  | &#96;n1&#96;, &#96;n2&#96;, &#96;n3&#96;...  |
| 并行网关  | &#96;n65ddfcdfa8a3e58...&#96;  | &#96;pg1&#96;, &#96;pg2&#96;, &#96;pg3&#96;...  |
| 排他网关  | &#96;n981d07571dd3a6e...&#96;  | &#96;eg1&#96;, &#96;eg2&#96;, &#96;eg3&#96;...  |
| 汇聚网关  | &#96;n48d28c6219b31ba...&#96;  | &#96;cg1&#96;, &#96;cg2&#96;, &#96;cg3&#96;...  |
| 连接线  | &#96;l9addaf3938f3a62...&#96;  | 无需 ID  |

### 3.2 命名规范

- 任务节点：按出现顺序编号，`n1` → `n2` → `n3`
- 并行网关：按出现顺序编号，`pg1` → `pg2`
- 排他网关：按出现顺序编号，`eg1` → `eg2`
- 汇聚网关：按出现顺序编号，`cg1` → `cg2`
- 连接线：不需要显式 ID，由 `source` 和 `target` 唯一定位

---

## 4. 完整 System Prompt 模板

以下是为智能体 LLM 设计的完整 System Prompt：

```
# Role
你是bk-sops（蓝鲸标准运维）流程生成助手。你的任务是理解用户的运维需求，获取插件信息，并生成简化的JSONL格式流程描述。

# Workflow
1. 用户提出流程需求后，先获取可用插件
2. 根据需求选择合适的插件
3. 根据用户需求和参数定义，生成JSONL格式流程

# Output Format
输出为JSONL格式，每行一个JSON对象，按以下顺序输出：
   流程名字：{"type":"name","value":"xxx"}
1. 开始节点 (type:"StartEvent")
2. 活动节点 (type:"Activity") 和网关节点 (type:"ParallelGateway"/"ExclusiveGateway"/"ConvergeGateway")，按流程顺序
3. 结束节点 (type:"EndEvent")
4. 所有连接线 (type:"Link")
5. 所有变量 (type:"Variable")

# Component Types
- name: 流程命名
  {"type":"name","value":"xxx"}
- StartEvent: 开始节点
  {"type":"StartEvent","id":"start","name":"流程开始"}
- EndEvent: 结束节点
  {"type":"EndEvent","id":"end","name":"流程结束"}
- Activity: 活动节点（标准插件）
  {"type":"Activity","id":"n1","name":"节点名","code":"插件编码","data":{"key":"value"}}
- Activity: 活动节点（第三方插件）
  {"type":"Activity","id":"n1","name":"节点名","code":"remote_plugin","plugin_code":"插件标识码","plugin_version":"1.0.0","data":{"业务参数":"值"}}
- ParallelGateway: 并行网关
  {"type":"ParallelGateway","id":"pg1","name":"并行"}
- ExclusiveGateway: 排他网关
  {"type":"ExclusiveGateway","id":"eg1","name":"判断","conditions":[{"evaluate":"条件表达式","target":"目标节点ID"}]}
- ConvergeGateway: 汇聚网关
  {"type":"ConvergeGateway","id":"cg1","name":"汇聚"}
- Link: 连接线
  {"type":"Link","source":"源节点ID","target":"目标节点ID"}
- Variable: 变量
  {"type":"Variable","key":"${变量名}","name":"显示名","value":"默认值","source_type":"custom","custom_type":"input"}

# ID Rules
- 开始节点ID: start
- 结束节点ID: end
- 任务节点ID: n1, n2, n3...
- 并行网关ID: pg1, pg2...
- 排他网关ID: eg1, eg2...
- 汇聚网关ID: cg1, cg2...

# Data Format Rules
- data字段扁平化，直接为{"key":"value"}格式
- 引用变量使用${变量名}格式
- 仅填写用户指定的参数，其他参数由后端补全默认值
- 第三方插件（remote_plugin）：code固定为"remote_plugin"，需额外指定plugin_code和plugin_version；data中只填业务参数，框架字段（command/input/session_code/chat_history/context）由后端自动补全

# Constraints
- 每个流程必须有且仅有一个开始节点和一个结束节点
- 所有节点必须通过连接线连通
- 并行网关必须与汇聚网关配对使用
- 排他网关的条件分支必须覆盖所有可能情况
- 用户提到的可配置参数应定义为变量
```

---

## 5. 示例

### 示例 1：带默认分支的排他网关

**流程图**：

```
┌─ [approved] → 执行变更 ─┐
开始 → 等待审批 → 审批判断 ──┼─ [rejected] → 执行回滚 ─┼→ 汇聚 → 结束
                             └─ [default]  → 异常处理 ─┘
```

**JSONL 输出**：

```json
{"type":"name","value":"审批后执行变更流程"}
{"type":"StartEvent","id":"start","name":"流程开始"}
{"type":"Activity","id":"n1","name":"等待审批","code":"bk_pause"}
{"type":"ExclusiveGateway","id":"eg1","name":"审批结果判断","conditions":[{"evaluate":"${approval_result}=='approved'","target":"n2"},{"evaluate":"${approval_result}=='rejected'","target":"n3"}]}
{"type":"Activity","id":"n2","name":"执行变更脚本","code":"job_fast_execute_script"}
{"type":"Activity","id":"n3","name":"执行回滚脚本","code":"job_fast_execute_script"}
{"type":"Activity","id":"n4","name":"异常处理通知","code":"bk_notify"}
{"type":"ConvergeGateway","id":"cg1","name":"流程汇聚"}
{"type":"EndEvent","id":"end","name":"流程结束"}
{"type":"Link","source":"start","target":"n1"}
{"type":"Link","source":"n1","target":"eg1"}
{"type":"Link","source":"eg1","target":"n2"}
{"type":"Link","source":"eg1","target":"n3"}
{"type":"Link","source":"eg1","target":"n4","is_default":true}
{"type":"Link","source":"n2","target":"cg1"}
{"type":"Link","source":"n3","target":"cg1"}
{"type":"Link","source":"n4","target":"cg1"}
{"type":"Link","source":"cg1","target":"end"}
{"type":"Variable","key":"${approval_result}","name":"审批结果","value":"","source_type":"custom","custom_type":"input","description":"approved/rejected"}
{"type":"Variable","key":"${reject_reason}","name":"驳回原因","value":"","source_type":"custom","custom_type":"textarea","description":"审批驳回原因"}
{"type":"Variable","key":"${change_script}","name":"变更脚本内容","value":"","source_type":"custom","custom_type":"textarea","description":"需要执行的变更脚本"}
{"type":"Variable","key":"${ip}","name":"目标服务器IP","value":"","source_type":"custom","custom_type":"input","description":"执行脚本的目标服务器IP"}
{"type":"Variable","key":"${operator}","name":"操作人","value":"admin","source_type":"custom","custom_type":"input","description":"流程操作人"}
```

### 示例 2：第三方插件流程 (remote_plugin)

**流程图**：

```
开始 → [第三方插件name] → [第三方插件name] → 结束
```

**JSONL 输出**：

```jsonl
{"type":"name","value":"第三方插件测试流程"}
{"type":"StartEvent","id":"start","name":"流程开始"}
{"type":"Activity","id":"n1","name":"第三方插件name","code":"remote_plugin","plugin_code":"xxx","plugin_version":"1.0.0","data":{"zone":3,"is_pb":false,"pb_path":"","remark":""}}
{"type":"Activity","id":"n2","name":"第三方插件name","code":"remote_plugin","plugin_code":"xxx","plugin_version":"1.0.0","data":{}}
{"type":"EndEvent","id":"end","name":"流程结束"}
{"type":"Link","source":"start","target":"n1"}
{"type":"Link","source":"n1","target":"n2"}
{"type":"Link","source":"n2","target":"end"}
```

---

## 6. 注意事项

- 并行网关 (ParallelGateway) 的所有分支都会执行，汇聚时等待全部完成
- 条件网关 (ExclusiveGateway) 只会执行一个满足条件的分支
- 条件并行网关 (ExclusiveParallelGateway) 会执行所有满足条件的分支
- 每个分支网关必须有对应的汇聚网关 (ConvergeGateway)，且分支网关的所有分支第一个遇到的汇聚网关必须是同一个
- 条件网关建议设置 `is_default` 默认分支处理未匹配情况
- 第三方插件 `code` 固定为 `"remote_plugin"`，通过 `plugin_code` 指定具体插件标识
- 第三方插件的 `data` 中仅填写业务参数，框架字段由后端渲染器自动补全
- 后端渲染器会将 `plugin_code` 和 `plugin_version` 放入 `component.data` 内部

