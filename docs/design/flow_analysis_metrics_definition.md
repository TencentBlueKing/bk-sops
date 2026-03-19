# 流程分析指标定义文档

## 一、概述

本文档详细定义了流程分析中使用的所有指标，包括指标名称、类型、计算公式、数据来源、单位格式和示例值。指标分为基础指标和高级指标两类，基础指标可直接基于现成数据计算，高级指标需要知识库支持。

### 指标分类体系

```
流程分析指标
├── 流程结构分析指标
│   ├── 节点数量指标（基础）
│   ├── 流程复杂度指标（基础）
│   ├── 流程模式指标（基础）
│   ├── 变量使用指标（基础）
│   └── 流程模式识别指标（高级）
├── 流程执行分析指标
│   ├── 执行频率指标（基础）
│   ├── 成功率指标（基础）
│   ├── 耗时指标（基础）
│   └── 执行趋势指标（基础）
├── 节点使用分析指标
│   ├── 节点使用频率指标（基础）
│   ├── 节点成功率指标（基础）
│   ├── 节点耗时指标（基础）
│   ├── 节点组合指标（基础）
│   └── 节点组合模式指标（高级）
├── 业务场景分析指标
│   ├── 场景分布指标（基础）
│   ├── 场景使用频率指标（基础）
│   ├── 场景成功率指标（基础）
│   ├── 场景耗时指标（基础）
│   └── 场景效果指标（基础）
└── 质量分析指标
    ├── 质量评分指标（基础）
    ├── 质量维度评分指标（基础）
    ├── 基础异常识别指标（基础）
    ├── 基础优化建议指标（基础）
    └── 高级质量指标（高级）
```

---

## 二、流程结构分析指标

### 2.1 节点数量指标（基础）

#### 2.1.1 总节点数

- **指标名称**：`total_nodes`
- **指标类型**：基础指标
- **计算公式**：`total_nodes = atom_total + subprocess_total`
- **数据来源**：
  - `TemplateStatistics.atom_total`
  - `TemplateStatistics.subprocess_total`
- **单位/格式**：整数
- **示例值**：15
- **说明**：流程中所有任务节点的总数

#### 2.1.2 标准插件节点数

- **指标名称**：`atom_nodes_count`
- **指标类型**：基础指标
- **计算公式**：`atom_nodes_count = TemplateStatistics.atom_total`
- **数据来源**：`TemplateStatistics.atom_total`
- **单位/格式**：整数
- **示例值**：12
- **说明**：流程中标准插件节点的数量

#### 2.1.3 子流程节点数

- **指标名称**：`subprocess_nodes_count`
- **指标类型**：基础指标
- **计算公式**：`subprocess_nodes_count = TemplateStatistics.subprocess_total`
- **数据来源**：`TemplateStatistics.subprocess_total`
- **单位/格式**：整数
- **示例值**：3
- **说明**：流程中子流程节点的数量

#### 2.1.4 网关节点数

- **指标名称**：`gateways_count`
- **指标类型**：基础指标
- **计算公式**：`gateways_count = TemplateStatistics.gateways_total`
- **数据来源**：`TemplateStatistics.gateways_total`
- **单位/格式**：整数
- **示例值**：4
- **说明**：流程中网关节点的数量

#### 2.1.5 并行网关数

- **指标名称**：`parallel_gateways_count`
- **指标类型**：基础指标
- **计算公式**：统计`pipeline_tree.gateways`中`type == "ParallelGateway"`的节点数
- **数据来源**：`pipeline_tree.gateways`
- **单位/格式**：整数
- **示例值**：2
- **说明**：流程中并行网关的数量

#### 2.1.6 排他网关数

- **指标名称**：`exclusive_gateways_count`
- **指标类型**：基础指标
- **计算公式**：统计`pipeline_tree.gateways`中`type == "ExclusiveGateway"`的节点数
- **数据来源**：`pipeline_tree.gateways`
- **单位/格式**：整数
- **示例值**：1
- **说明**：流程中排他网关的数量

#### 2.1.7 汇聚网关数

- **指标名称**：`converge_gateways_count`
- **指标类型**：基础指标
- **计算公式**：统计`pipeline_tree.gateways`中`type == "ConvergeGateway"`的节点数
- **数据来源**：`pipeline_tree.gateways`
- **单位/格式**：整数
- **示例值**：1
- **说明**：流程中汇聚网关的数量

### 2.2 流程复杂度指标（基础）

#### 2.2.1 流程深度

- **指标名称**：`flow_depth`
- **指标类型**：基础指标
- **计算公式**：从`start_event`到`end_event`的最长路径长度（节点数）
- **数据来源**：`pipeline_tree`（通过`flows`构建有向图，计算最长路径）
- **单位/格式**：整数
- **示例值**：8
- **说明**：流程的最大执行路径长度，反映流程的纵向复杂度

#### 2.2.2 分支数

- **指标名称**：`branch_count`
- **指标类型**：基础指标
- **计算公式**：统计排他网关的数量（每个排他网关代表一个分支点）
- **数据来源**：`pipeline_tree.gateways`（`type == "ExclusiveGateway"`）
- **单位/格式**：整数
- **示例值**：3
- **说明**：流程中条件分支的数量

#### 2.2.3 并行分支数

- **指标名称**：`parallel_branch_count`
- **指标类型**：基础指标
- **计算公式**：统计并行网关的分支数量总和（每个并行网关的`outgoing`数组长度）
- **数据来源**：`pipeline_tree.gateways`（`type == "ParallelGateway"`）
- **单位/格式**：整数
- **示例值**：6
- **说明**：流程中并行分支的总数

#### 2.2.4 最大并行度

- **指标名称**：`max_parallelism`
- **指标类型**：基础指标
- **计算公式**：`max_parallelism = max(parallel_gateway.outgoing.length)`（所有并行网关的最大分支数）
- **数据来源**：`pipeline_tree.gateways`（`type == "ParallelGateway"`）
- **单位/格式**：整数
- **示例值**：4
- **说明**：流程中同时执行的最大分支数

#### 2.2.5 循环结构数

- **指标名称**：`loop_count`
- **指标类型**：基础指标
- **计算公式**：检测`pipeline_tree`中是否存在循环结构（通过DFS检测有向图中的环）
- **数据来源**：`pipeline_tree`（通过`flows`构建有向图）
- **单位/格式**：整数
- **示例值**：0
- **说明**：流程中循环结构的数量

### 2.3 流程模式指标（基础）

#### 2.3.1 串行节点比例

- **指标名称**：`serial_nodes_ratio`
- **指标类型**：基础指标
- **计算公式**：`serial_nodes_ratio = serial_nodes_count / total_nodes`
  - `serial_nodes_count`：只有一个`incoming`和一个`outgoing`的节点数
- **数据来源**：`pipeline_tree.activities`
- **单位/格式**：浮点数（0-1）
- **示例值**：0.6
- **说明**：串行执行的节点占比

#### 2.3.2 并行节点比例

- **指标名称**：`parallel_nodes_ratio`
- **指标类型**：基础指标
- **计算公式**：`parallel_nodes_ratio = parallel_nodes_count / total_nodes`
  - `parallel_nodes_count`：位于并行网关分支中的节点数
- **数据来源**：`pipeline_tree.activities`和`pipeline_tree.gateways`
- **单位/格式**：浮点数（0-1）
- **示例值**：0.3
- **说明**：并行执行的节点占比

#### 2.3.3 网关使用率

- **指标名称**：`gateway_usage_ratio`
- **指标类型**：基础指标
- **计算公式**：`gateway_usage_ratio = (gateways_count > 0 ? 1 : 0)`
- **数据来源**：`TemplateStatistics.gateways_total`
- **单位/格式**：浮点数（0或1）
- **示例值**：1
- **说明**：是否使用网关（1表示使用，0表示未使用）

### 2.4 变量使用指标（基础）

#### 2.4.1 输入变量数

- **指标名称**：`input_variables_count`
- **指标类型**：基础指标
- **计算公式**：`input_variables_count = TemplateStatistics.input_count`
- **数据来源**：`TemplateStatistics.input_count`
- **单位/格式**：整数
- **示例值**：5
- **说明**：流程中定义的输入变量数量

#### 2.4.2 输出变量数

- **指标名称**：`output_variables_count`
- **指标类型**：基础指标
- **计算公式**：`output_variables_count = TemplateStatistics.output_count`
- **数据来源**：`TemplateStatistics.output_count`
- **单位/格式**：整数
- **示例值**：3
- **说明**：流程中定义的输出变量数量

#### 2.4.3 变量引用率

- **指标名称**：`variable_reference_ratio`
- **指标类型**：基础指标
- **计算公式**：`variable_reference_ratio = referenced_variables_count / total_variables_count`
  - `referenced_variables_count`：在节点参数中被引用的变量数
  - `total_variables_count`：总变量数（`input_count + output_count`）
- **数据来源**：
  - `pipeline_tree.constants`（变量定义）
  - `pipeline_tree.activities`（节点参数中的变量引用）
- **单位/格式**：浮点数（0-1）
- **示例值**：0.75
- **说明**：被节点引用的变量占比

### 2.5 流程模式识别指标（高级）

#### 2.5.1 流程模式类型

- **指标名称**：`flow_pattern_type`
- **指标类型**：高级指标
- **计算公式**：通过知识库匹配流程模式（如：部署流程、监控流程、故障处理流程等）
- **数据来源**：知识库中的流程模式知识
- **单位/格式**：字符串（枚举值）
- **示例值**：`"deployment_flow"`
- **说明**：流程所属的模式类型

#### 2.5.2 模式匹配度

- **指标名称**：`pattern_match_score`
- **指标类型**：高级指标
- **计算公式**：`pattern_match_score = similarity(current_flow, pattern_template)`（向量相似度或结构相似度）
- **数据来源**：知识库中的流程模式知识
- **单位/格式**：浮点数（0-1）
- **示例值**：0.85
- **说明**：当前流程与标准模式的匹配度

---

## 三、流程执行分析指标

### 3.1 执行频率指标（基础）

#### 3.1.1 总执行次数

- **指标名称**：`total_executions`
- **指标类型**：基础指标
- **计算公式**：`total_executions = COUNT(TaskflowStatistics WHERE template_id = ?)`
- **数据来源**：`TaskflowStatistics`
- **单位/格式**：整数
- **示例值**：1250
- **说明**：流程模板的总执行次数

#### 3.1.2 日均执行次数

- **指标名称**：`daily_avg_executions`
- **指标类型**：基础指标
- **计算公式**：`daily_avg_executions = total_executions / days_count`
  - `days_count`：从首次执行到当前的天数
- **数据来源**：`TaskflowStatistics.create_time`
- **单位/格式**：浮点数
- **示例值**：12.5
- **说明**：平均每天的执行次数

#### 3.1.3 周均执行次数

- **指标名称**：`weekly_avg_executions`
- **指标类型**：基础指标
- **计算公式**：`weekly_avg_executions = total_executions / weeks_count`
- **数据来源**：`TaskflowStatistics.create_time`
- **单位/格式**：浮点数
- **示例值**：87.5
- **说明**：平均每周的执行次数

#### 3.1.4 月均执行次数

- **指标名称**：`monthly_avg_executions`
- **指标类型**：基础指标
- **计算公式**：`monthly_avg_executions = total_executions / months_count`
- **数据来源**：`TaskflowStatistics.create_time`
- **单位/格式**：浮点数
- **示例值**：375.0
- **说明**：平均每月的执行次数

### 3.2 成功率指标（基础）

#### 3.2.1 成功率

- **指标名称**：`success_rate`
- **指标类型**：基础指标
- **计算公式**：`success_rate = successful_executions / total_executions`
  - `successful_executions`：状态为FINISHED且所有节点都成功的执行次数
- **数据来源**：`TaskFlowInstance.status`（需要关联查询）
- **单位/格式**：浮点数（0-1）
- **示例值**：0.95
- **说明**：流程执行的成功率

#### 3.2.2 失败率

- **指标名称**：`failure_rate`
- **指标类型**：基础指标
- **计算公式**：`failure_rate = failed_executions / total_executions`
  - `failed_executions`：状态为FAILED的执行次数
- **数据来源**：`TaskFlowInstance.status`
- **单位/格式**：浮点数（0-1）
- **示例值**：0.04
- **说明**：流程执行的失败率

#### 3.2.3 跳过率

- **指标名称**：`skip_rate`
- **指标类型**：基础指标
- **计算公式**：`skip_rate = skipped_executions / total_executions`
  - `skipped_executions`：包含跳过节点的执行次数
- **数据来源**：`TaskflowExecutedNodeStatistics.is_skip`
- **单位/格式**：浮点数（0-1）
- **示例值**：0.01
- **说明**：流程执行的跳过率

### 3.3 耗时指标（基础）

#### 3.3.1 平均耗时

- **指标名称**：`avg_elapsed_time`
- **指标类型**：基础指标
- **计算公式**：`avg_elapsed_time = AVG(TaskflowStatistics.elapsed_time WHERE template_id = ?)`
- **数据来源**：`TaskflowStatistics.elapsed_time`
- **单位/格式**：整数（秒）
- **示例值**：180
- **说明**：流程执行的平均耗时（秒）

#### 3.3.2 中位数耗时

- **指标名称**：`median_elapsed_time`
- **指标类型**：基础指标
- **计算公式**：`median_elapsed_time = MEDIAN(TaskflowStatistics.elapsed_time WHERE template_id = ?)`
- **数据来源**：`TaskflowStatistics.elapsed_time`
- **单位/格式**：整数（秒）
- **示例值**：165
- **说明**：流程执行的中位数耗时

#### 3.3.3 P90耗时

- **指标名称**：`p90_elapsed_time`
- **指标类型**：基础指标
- **计算公式**：`p90_elapsed_time = PERCENTILE(TaskflowStatistics.elapsed_time, 90)`
- **数据来源**：`TaskflowStatistics.elapsed_time`
- **单位/格式**：整数（秒）
- **示例值**：250
- **说明**：90%的执行耗时都在此值以下

#### 3.3.4 P95耗时

- **指标名称**：`p95_elapsed_time`
- **指标类型**：基础指标
- **计算公式**：`p95_elapsed_time = PERCENTILE(TaskflowStatistics.elapsed_time, 95)`
- **数据来源**：`TaskflowStatistics.elapsed_time`
- **单位/格式**：整数（秒）
- **示例值**：300
- **说明**：95%的执行耗时都在此值以下

#### 3.3.5 P99耗时

- **指标名称**：`p99_elapsed_time`
- **指标类型**：基础指标
- **计算公式**：`p99_elapsed_time = PERCENTILE(TaskflowStatistics.elapsed_time, 99)`
- **数据来源**：`TaskflowStatistics.elapsed_time`
- **单位/格式**：整数（秒）
- **示例值**：450
- **说明**：99%的执行耗时都在此值以下

### 3.4 执行趋势指标（基础）

#### 3.4.1 执行次数趋势（日）

- **指标名称**：`daily_execution_trend`
- **指标类型**：基础指标
- **计算公式**：按`create_time`分组，统计每天的执行次数
- **数据来源**：`TaskflowStatistics.create_time`
- **单位/格式**：时间序列数据（日期 -> 执行次数）
- **示例值**：`{"2024-01-01": 10, "2024-01-02": 15, ...}`
- **说明**：按日统计的执行次数趋势

#### 3.4.2 成功率趋势（周）

- **指标名称**：`weekly_success_rate_trend`
- **指标类型**：基础指标
- **计算公式**：按周分组，计算每周的成功率
- **数据来源**：`TaskflowStatistics.create_time`和`TaskFlowInstance.status`
- **单位/格式**：时间序列数据（周 -> 成功率）
- **示例值**：`{"2024-W01": 0.95, "2024-W02": 0.96, ...}`
- **说明**：按周统计的成功率趋势

---

## 四、节点使用分析指标

### 4.1 节点使用频率指标（基础）

#### 4.1.1 节点使用次数

- **指标名称**：`node_usage_count`
- **指标类型**：基础指标
- **计算公式**：`node_usage_count = COUNT(TemplateNodeStatistics WHERE component_code = ?)`
- **数据来源**：`TemplateNodeStatistics`
- **单位/格式**：整数
- **示例值**：450
- **说明**：某个组件在所有模板中被使用的总次数

#### 4.1.2 节点使用率

- **指标名称**：`node_usage_ratio`
- **指标类型**：基础指标
- **计算公式**：`node_usage_ratio = templates_with_node / total_templates`
  - `templates_with_node`：使用该节点的模板数
  - `total_templates`：总模板数
- **数据来源**：`TemplateNodeStatistics`
- **单位/格式**：浮点数（0-1）
- **示例值**：0.35
- **说明**：使用该节点的模板占比

### 4.2 节点成功率指标（基础）

#### 4.2.1 节点成功率

- **指标名称**：`node_success_rate`
- **指标类型**：基础指标
- **计算公式**：`node_success_rate = successful_executions / total_executions`
  - `successful_executions`：`status = True`的执行次数
  - `total_executions`：总执行次数
- **数据来源**：`TaskflowExecutedNodeStatistics.status`
- **单位/格式**：浮点数（0-1）
- **示例值**：0.98
- **说明**：节点执行的成功率

#### 4.2.2 节点失败率

- **指标名称**：`node_failure_rate`
- **指标类型**：基础指标
- **计算公式**：`node_failure_rate = failed_executions / total_executions`
  - `failed_executions`：`status = False`的执行次数
- **数据来源**：`TaskflowExecutedNodeStatistics.status`
- **单位/格式**：浮点数（0-1）
- **示例值**：0.02
- **说明**：节点执行的失败率

#### 4.2.3 节点重试率

- **指标名称**：`node_retry_rate`
- **指标类型**：基础指标
- **计算公式**：`node_retry_rate = retry_executions / total_executions`
  - `retry_executions`：`is_retry = True`的执行次数
- **数据来源**：`TaskflowExecutedNodeStatistics.is_retry`
- **单位/格式**：浮点数（0-1）
- **示例值**：0.05
- **说明**：节点执行的重试率

### 4.3 节点耗时指标（基础）

#### 4.3.1 节点平均耗时

- **指标名称**：`node_avg_elapsed_time`
- **指标类型**：基础指标
- **计算公式**：`node_avg_elapsed_time = AVG(TaskflowExecutedNodeStatistics.elapsed_time WHERE component_code = ?)`
- **数据来源**：`TaskflowExecutedNodeStatistics.elapsed_time`
- **单位/格式**：整数（秒）
- **示例值**：25
- **说明**：节点执行的平均耗时

#### 4.3.2 节点耗时占比

- **指标名称**：`node_time_ratio`
- **指标类型**：基础指标
- **计算公式**：`node_time_ratio = node_avg_elapsed_time / flow_avg_elapsed_time`
- **数据来源**：
  - `TaskflowExecutedNodeStatistics.elapsed_time`
  - `TaskflowStatistics.elapsed_time`
- **单位/格式**：浮点数（0-1）
- **示例值**：0.15
- **说明**：节点耗时占流程总耗时的比例

### 4.4 节点组合指标（基础）

#### 4.4.1 常见节点序列

- **指标名称**：`common_node_sequences`
- **指标类型**：基础指标
- **计算公式**：分析`pipeline_tree.flows`，统计常见的节点执行序列（如：A->B->C）
- **数据来源**：`pipeline_tree.flows`
- **单位/格式**：列表（序列 -> 出现次数）
- **示例值**：`[("job_fast_execute_script", "sleep_timer"): 120]`
- **说明**：流程中常见的节点执行序列及其出现频率

#### 4.4.2 节点前置节点统计

- **指标名称**：`node_predecessors`
- **指标类型**：基础指标
- **计算公式**：统计每个节点的前置节点（通过`flows`查找`target = node_id`的`source`）
- **数据来源**：`pipeline_tree.flows`
- **单位/格式**：字典（节点ID -> 前置节点列表）
- **示例值**：`{"node123": ["node111", "node112"]}`
- **说明**：每个节点的前置节点列表

---

## 五、业务场景分析指标

### 5.1 场景分布指标（基础）

#### 5.1.1 场景模板数量

- **指标名称**：`category_template_count`
- **指标类型**：基础指标
- **计算公式**：`category_template_count = COUNT(TaskTemplate WHERE category = ?)`
- **数据来源**：`TaskTemplate.category`
- **单位/格式**：整数
- **示例值**：150
- **说明**：某个分类下的模板数量

#### 5.1.2 场景模板占比

- **指标名称**：`category_template_ratio`
- **指标类型**：基础指标
- **计算公式**：`category_template_ratio = category_template_count / total_templates`
- **数据来源**：`TaskTemplate.category`
- **单位/格式**：浮点数（0-1）
- **示例值**：0.25
- **说明**：某个分类的模板占比

#### 5.1.3 场景执行次数

- **指标名称**：`category_execution_count`
- **指标类型**：基础指标
- **计算公式**：`category_execution_count = COUNT(TaskflowStatistics WHERE category = ?)`
- **数据来源**：`TaskflowStatistics.category`
- **单位/格式**：整数
- **示例值**：5000
- **说明**：某个分类的执行次数

### 5.2 场景成功率指标（基础）

#### 5.2.1 场景成功率

- **指标名称**：`category_success_rate`
- **指标类型**：基础指标
- **计算公式**：`category_success_rate = successful_executions / total_executions`（按category分组）
- **数据来源**：`TaskflowStatistics.category`和`TaskFlowInstance.status`
- **单位/格式**：浮点数（0-1）
- **示例值**：0.92
- **说明**：某个分类的执行成功率

### 5.3 场景耗时指标（基础）

#### 5.3.1 场景平均耗时

- **指标名称**：`category_avg_elapsed_time`
- **指标类型**：基础指标
- **计算公式**：`category_avg_elapsed_time = AVG(TaskflowStatistics.elapsed_time WHERE category = ?)`
- **数据来源**：`TaskflowStatistics.elapsed_time`和`category`
- **单位/格式**：整数（秒）
- **示例值**：200
- **说明**：某个分类的平均执行耗时

---

## 六、质量分析指标

### 6.1 质量评分指标（基础）

#### 6.1.1 综合质量评分

- **指标名称**：`comprehensive_quality_score`
- **指标类型**：基础指标
- **计算公式**：
  ```
  comprehensive_quality_score =
    success_rate_weight * success_rate +
    efficiency_weight * (1 - normalized_elapsed_time) +
    complexity_weight * (1 - normalized_complexity)
  ```
  - `success_rate_weight = 0.5`
  - `efficiency_weight = 0.3`
  - `complexity_weight = 0.2`
  - `normalized_elapsed_time`：归一化的耗时（0-1）
  - `normalized_complexity`：归一化的复杂度（0-1）
- **数据来源**：综合多个维度的指标
- **单位/格式**：浮点数（0-1）
- **示例值**：0.85
- **说明**：流程的综合质量评分

#### 6.1.2 执行质量评分

- **指标名称**：`execution_quality_score`
- **指标类型**：基础指标
- **计算公式**：`execution_quality_score = success_rate * 0.6 + (1 - normalized_elapsed_time) * 0.4`
- **数据来源**：
  - `success_rate`（流程执行分析指标）
  - `avg_elapsed_time`（流程执行分析指标）
- **单位/格式**：浮点数（0-1）
- **示例值**：0.88
- **说明**：基于执行情况的质量评分

#### 6.1.3 结构质量评分

- **指标名称**：`structure_quality_score`
- **指标类型**：基础指标
- **计算公式**：`structure_quality_score = (1 - normalized_complexity) * 0.7 + normalized_reusability * 0.3`
  - `normalized_complexity`：归一化的复杂度（基于节点数、深度等）
  - `normalized_reusability`：归一化的复用性（基于子流程使用率）
- **数据来源**：流程结构分析指标
- **单位/格式**：浮点数（0-1）
- **示例值**：0.75
- **说明**：基于结构特征的质量评分

### 6.2 基础异常识别指标（基础）

#### 6.2.1 成功率异常标识

- **指标名称**：`success_rate_anomaly`
- **指标类型**：基础指标
- **计算公式**：`success_rate_anomaly = (success_rate < threshold) ? 1 : 0`
  - `threshold = 0.8`（可配置）
- **数据来源**：`success_rate`（流程执行分析指标）
- **单位/格式**：整数（0或1）
- **示例值**：0
- **说明**：标识成功率是否异常低（1表示异常，0表示正常）

#### 6.2.2 耗时异常标识

- **指标名称**：`elapsed_time_anomaly`
- **指标类型**：基础指标
- **计算公式**：`elapsed_time_anomaly = (avg_elapsed_time > threshold) ? 1 : 0`
  - `threshold`：基于历史数据的P95值或固定阈值
- **数据来源**：`avg_elapsed_time`（流程执行分析指标）
- **单位/格式**：整数（0或1）
- **示例值**：1
- **说明**：标识耗时是否异常长（1表示异常，0表示正常）

---

## 七、指标汇总表

### 7.1 基础指标汇总

| 指标分类 | 指标数量 | 实施优先级 |
|---------|---------|-----------|
| 流程结构分析指标 | 15 | P0 |
| 流程执行分析指标 | 12 | P0 |
| 节点使用分析指标 | 10 | P0 |
| 业务场景分析指标 | 8 | P0 |
| 质量分析指标 | 8 | P1 |
| **总计** | **53** | - |

### 7.2 高级指标汇总

| 指标分类 | 指标数量 | 实施优先级 |
|---------|---------|-----------|
| 流程结构分析指标 | 2 | P2 |
| 节点使用分析指标 | 3 | P2 |
| 质量分析指标 | 4 | P2 |
| **总计** | **9** | - |

---

## 八、总结

本文档定义了62个分析指标，其中53个为基础指标（可直接实施），9个为高级指标（需要知识库支持）。所有指标都明确了计算公式、数据来源和示例值，为后续的算法实现提供了详细的规范。

**关键要点**：
1. 基础指标占85%，可以立即实施
2. 高级指标占15%，需要在知识库构建完成后实施
3. 所有指标都有明确的数学定义，便于实现
4. 指标设计考虑了实际业务需求和技术可行性

---

**文档版本**：v1.0
**创建时间**：2024-01-XX
**最后更新**：2024-01-XX
**文档状态**：已完成
