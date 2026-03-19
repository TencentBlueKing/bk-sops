# 流程分析数据依赖关系图

## 一、概述

本文档使用Mermaid图表展示流程分析的数据流向、数据表关系和分析维度依赖关系，帮助理解整个分析系统的架构和数据流转过程。

---

## 二、数据表关系图

### 2.1 核心数据表关系

```mermaid
erDiagram
    TaskTemplate ||--o{ PipelineTemplate : "关联"
    CommonTemplate ||--o{ PipelineTemplate : "关联"
    PipelineTemplate ||--o{ TemplateStatistics : "统计"
    TaskTemplate ||--o{ TaskFlowInstance : "创建"
    CommonTemplate ||--o{ TaskFlowInstance : "创建"
    TaskFlowInstance ||--o{ TaskflowStatistics : "统计"
    TaskFlowInstance ||--o{ TaskflowExecutedNodeStatistics : "节点执行"
    TaskTemplate ||--o{ TemplateNodeStatistics : "节点引用"
    CommonTemplate ||--o{ TemplateNodeStatistics : "节点引用"

    TaskTemplate {
        bigint id PK
        int project_id FK
        bigint pipeline_template_id FK
        string category
        boolean is_deleted
    }

    CommonTemplate {
        bigint id PK
        bigint pipeline_template_id FK
        string category
        boolean is_deleted
    }

    PipelineTemplate {
        bigint template_id PK
        json data "pipeline_tree"
        string creator
        datetime create_time
        datetime edit_time
    }

    TemplateStatistics {
        bigint id PK
        bigint template_id FK
        bigint task_template_id FK
        int atom_total
        int subprocess_total
        int gateways_total
        int input_count
        int output_count
        string category
        datetime template_create_time
    }

    TaskFlowInstance {
        bigint id PK
        bigint pipeline_instance_id FK
        bigint template_id FK
        string status
        string current_flow
        datetime create_time
        datetime start_time
        datetime finish_time
    }

    TaskflowStatistics {
        bigint id PK
        bigint instance_id FK
        bigint task_instance_id FK
        bigint template_id FK
        bigint task_template_id FK
        int atom_total
        int subprocess_total
        int gateways_total
        string category
        datetime create_time
        datetime start_time
        datetime finish_time
        int elapsed_time
    }

    TaskflowExecutedNodeStatistics {
        bigint id PK
        bigint instance_id FK
        bigint task_instance_id FK
        string template_node_id
        string node_id
        string component_code
        datetime started_time
        datetime archived_time
        int elapsed_time
        boolean status
        boolean is_skip
        boolean is_retry
    }

    TemplateNodeStatistics {
        bigint id PK
        bigint template_id FK
        bigint task_template_id FK
        string component_code
        string node_id
        string category
        boolean is_sub
    }
```

---

## 三、数据流向图

### 3.1 流程结构分析数据流

```mermaid
flowchart TD
    A[TaskTemplate/CommonTemplate] -->|pipeline_template| B[PipelineTemplate]
    B -->|data字段| C[pipeline_tree JSON]
    C -->|解析| D[流程结构分析引擎]

    E[TemplateStatistics] -->|统计信息| D

    D -->|输出| F[流程结构分析结果]
    F -->|包含| F1[节点数量指标]
    F -->|包含| F2[复杂度指标]
    F -->|包含| F3[模式指标]
    F -->|包含| F4[变量使用指标]

    style A fill:#e1f5ff
    style B fill:#e1f5ff
    style C fill:#fff4e1
    style D fill:#e8f5e9
    style F fill:#f3e5f5
```

### 3.2 流程执行分析数据流

```mermaid
flowchart TD
    A[TaskFlowInstance] -->|创建任务| B[TaskflowStatistics]
    B -->|执行记录| C[流程执行分析引擎]

    D[TaskflowExecutedNodeStatistics] -->|节点执行详情| C

    C -->|输出| E[流程执行分析结果]
    E -->|包含| E1[执行频率指标]
    E -->|包含| E2[成功率指标]
    E -->|包含| E3[耗时指标]
    E -->|包含| E4[执行趋势指标]

    style A fill:#e1f5ff
    style B fill:#e1f5ff
    style D fill:#e1f5ff
    style C fill:#e8f5e9
    style E fill:#f3e5f5
```

### 3.3 节点使用分析数据流

```mermaid
flowchart TD
    A[TemplateNodeStatistics] -->|节点引用统计| B[节点使用分析引擎]
    C[TaskflowExecutedNodeStatistics] -->|节点执行统计| B
    D[pipeline_tree] -->|节点组合关系| B

    B -->|输出| E[节点使用分析结果]
    E -->|包含| E1[使用频率指标]
    E -->|包含| E2[成功率指标]
    E -->|包含| E3[耗时指标]
    E -->|包含| E4[组合指标]

    style A fill:#e1f5ff
    style C fill:#e1f5ff
    style D fill:#fff4e1
    style B fill:#e8f5e9
    style E fill:#f3e5f5
```

### 3.4 业务场景分析数据流

```mermaid
flowchart TD
    A[TaskTemplate.category] -->|分类信息| B[业务场景分析引擎]
    C[TaskflowStatistics.category] -->|执行分类| B

    B -->|输出| D[业务场景分析结果]
    D -->|包含| D1[场景分布指标]
    D -->|包含| D2[使用频率指标]
    D -->|包含| D3[成功率指标]
    D -->|包含| D4[耗时指标]
    D -->|包含| D5[效果指标]

    style A fill:#e1f5ff
    style C fill:#e1f5ff
    style B fill:#e8f5e9
    style D fill:#f3e5f5
```

### 3.5 质量分析数据流

```mermaid
flowchart TD
    A[流程结构分析结果] -->|结构指标| B[质量分析引擎]
    C[流程执行分析结果] -->|执行指标| B
    D[节点使用分析结果] -->|节点指标| B
    E[业务场景分析结果] -->|场景指标| B

    F[知识库] -.->|最佳实践知识| B

    B -->|输出| G[质量分析结果]
    G -->|包含| G1[质量评分]
    G -->|包含| G2[异常识别]
    G -->|包含| G3[优化建议]

    style A fill:#f3e5f5
    style C fill:#f3e5f5
    style D fill:#f3e5f5
    style E fill:#f3e5f5
    style F fill:#fff9c4
    style B fill:#e8f5e9
    style G fill:#f3e5f5
```

---

## 四、分析维度依赖关系图

### 4.1 基础分析依赖关系

```mermaid
flowchart TD
    subgraph 数据源层["数据源层（现成数据）"]
        A1[TaskTemplate/CommonTemplate]
        A2[PipelineTemplate]
        A3[TemplateStatistics]
        A4[TaskflowStatistics]
        A5[TaskflowExecutedNodeStatistics]
        A6[TemplateNodeStatistics]
    end

    subgraph 分析引擎层["分析引擎层（基础）"]
        B1[流程结构分析引擎]
        B2[流程执行分析引擎]
        B3[节点使用分析引擎]
        B4[业务场景分析引擎]
        B5[质量分析引擎基础部分]
    end

    subgraph 结果层["分析结果层"]
        C1[流程结构分析结果]
        C2[流程执行分析结果]
        C3[节点使用分析结果]
        C4[业务场景分析结果]
        C5[质量分析结果基础部分]
    end

    A1 -->|pipeline_tree| B1
    A2 -->|data| B1
    A3 -->|统计信息| B1

    A4 -->|执行记录| B2
    A5 -->|节点执行| B2

    A6 -->|节点引用| B3
    A5 -->|节点执行| B3
    A1 -->|pipeline_tree| B3

    A1 -->|category| B4
    A4 -->|category| B4

    C1 -->|结构指标| B5
    C2 -->|执行指标| B5
    C3 -->|节点指标| B5
    C4 -->|场景指标| B5

    B1 --> C1
    B2 --> C2
    B3 --> C3
    B4 --> C4
    B5 --> C5

    style A1 fill:#e1f5ff
    style A2 fill:#e1f5ff
    style A3 fill:#e1f5ff
    style A4 fill:#e1f5ff
    style A5 fill:#e1f5ff
    style A6 fill:#e1f5ff
    style B1 fill:#e8f5e9
    style B2 fill:#e8f5e9
    style B3 fill:#e8f5e9
    style B4 fill:#e8f5e9
    style B5 fill:#e8f5e9
    style C1 fill:#f3e5f5
    style C2 fill:#f3e5f5
    style C3 fill:#f3e5f5
    style C4 fill:#f3e5f5
    style C5 fill:#f3e5f5
```

### 4.2 高级分析依赖关系

```mermaid
flowchart TD
    subgraph 基础结果层["基础分析结果层"]
        A1[流程结构分析结果]
        A2[节点使用分析结果]
        A3[质量分析结果基础部分]
    end

    subgraph 知识库层["知识库层"]
        B1[流程模式知识]
        B2[节点组合模式知识]
        B3[最佳实践知识]
        B4[异常模式知识]
    end

    subgraph 高级分析引擎层["高级分析引擎层"]
        C1[流程模式匹配引擎]
        C2[节点组合模式识别引擎]
        C3[基于最佳实践的质量分析引擎]
    end

    subgraph 高级结果层["高级分析结果层"]
        D1[流程模式识别结果]
        D2[节点组合模式识别结果]
        D3[质量分析结果高级部分]
    end

    A1 -->|流程结构| C1
    B1 -->|模式知识| C1

    A2 -->|节点组合| C2
    B2 -->|组合模式知识| C2

    A3 -->|基础质量指标| C3
    A1 -->|结构指标| C3
    A2 -->|节点指标| C3
    B3 -->|最佳实践知识| C3
    B4 -->|异常模式知识| C3

    C1 --> D1
    C2 --> D2
    C3 --> D3

    style A1 fill:#f3e5f5
    style A2 fill:#f3e5f5
    style A3 fill:#f3e5f5
    style B1 fill:#fff9c4
    style B2 fill:#fff9c4
    style B3 fill:#fff9c4
    style B4 fill:#fff9c4
    style C1 fill:#e8f5e9
    style C2 fill:#e8f5e9
    style C3 fill:#e8f5e9
    style D1 fill:#f3e5f5
    style D2 fill:#f3e5f5
    style D3 fill:#f3e5f5
```

---

## 五、完整数据流架构图

### 5.1 整体架构

```mermaid
flowchart TB
    subgraph 数据采集层["数据采集层"]
        A1[流程模板数据]
        A2[任务执行数据]
        A3[节点执行数据]
    end

    subgraph 数据存储层["数据存储层"]
        B1[(MySQL数据库)]
        B2[(知识库)]
    end

    subgraph 分析处理层["分析处理层"]
        C1[流程结构分析]
        C2[流程执行分析]
        C3[节点使用分析]
        C4[业务场景分析]
        C5[质量分析基础]
        C6[质量分析高级]
    end

    subgraph 结果输出层["结果输出层"]
        D1[分析报告]
        D2[优化建议]
        D3[可视化图表]
    end

    A1 --> B1
    A2 --> B1
    A3 --> B1

    B1 --> C1
    B1 --> C2
    B1 --> C3
    B1 --> C4
    B1 --> C5

    B2 -.->|知识支持| C6
    C1 --> C5
    C2 --> C5
    C3 --> C5
    C4 --> C5

    C1 --> C6
    C3 --> C6
    C5 --> C6

    C1 --> D1
    C2 --> D1
    C3 --> D1
    C4 --> D1
    C5 --> D1
    C6 --> D1

    C5 --> D2
    C6 --> D2

    D1 --> D3

    style A1 fill:#e1f5ff
    style A2 fill:#e1f5ff
    style A3 fill:#e1f5ff
    style B1 fill:#fff4e1
    style B2 fill:#fff9c4
    style C1 fill:#e8f5e9
    style C2 fill:#e8f5e9
    style C3 fill:#e8f5e9
    style C4 fill:#e8f5e9
    style C5 fill:#e8f5e9
    style C6 fill:#c8e6c9
    style D1 fill:#f3e5f5
    style D2 fill:#f3e5f5
    style D3 fill:#f3e5f5
```

---

## 六、实施阶段依赖关系图

### 6.1 分阶段实施依赖

```mermaid
gantt
    title 流程分析实施阶段依赖关系
    dateFormat YYYY-MM-DD
    section 阶段五基础部分
    流程结构分析基础     :done, struct1, 2024-01-01, 3d
    流程执行分析        :done, exec1, 2024-01-01, 3d
    节点使用分析基础     :done, node1, 2024-01-01, 3d
    业务场景分析        :done, scene1, 2024-01-01, 2d
    质量分析基础        :active, quality1, 2024-01-04, 2d

    section 知识库构建
    知识库构建          :crit, kb1, 2024-01-01, 10d

    section 阶段五高级部分
    流程模式识别        :kb2, after kb1, 2d
    节点组合模式识别    :kb3, after kb1, 2d
    质量分析高级        :kb4, after kb1, 2d
```

### 6.2 依赖关系说明

```mermaid
flowchart LR
    A[阶段五基础部分] -->|可立即实施| B[基础分析结果]
    C[知识库构建] -->|完成后| D[高级分析能力]
    B -->|作为输入| E[质量分析基础]
    D -->|增强| F[质量分析高级]
    E -->|结合| F

    style A fill:#e8f5e9
    style C fill:#fff9c4
    style B fill:#f3e5f5
    style D fill:#fff9c4
    style E fill:#f3e5f5
    style F fill:#c8e6c9
```

---

## 七、数据表字段映射关系

### 7.1 流程结构分析字段映射

| 分析指标 | 数据表 | 字段 | 说明 |
|---------|--------|------|------|
| 总节点数 | TemplateStatistics | atom_total + subprocess_total | 直接计算 |
| 流程深度 | pipeline_tree | flows | 通过图算法计算 |
| 分支数 | pipeline_tree | gateways | 统计排他网关数 |
| 并行分支数 | pipeline_tree | gateways | 统计并行网关分支数 |
| 输入变量数 | TemplateStatistics | input_count | 直接获取 |
| 输出变量数 | TemplateStatistics | output_count | 直接获取 |

### 7.2 流程执行分析字段映射

| 分析指标 | 数据表 | 字段 | 说明 |
|---------|--------|------|------|
| 总执行次数 | TaskflowStatistics | COUNT(*) | 按template_id分组统计 |
| 成功率 | TaskFlowInstance | status | 统计FINISHED状态占比 |
| 平均耗时 | TaskflowStatistics | elapsed_time | AVG函数计算 |
| P90耗时 | TaskflowStatistics | elapsed_time | PERCENTILE函数计算 |
| 执行趋势 | TaskflowStatistics | create_time | 按时间维度分组统计 |

### 7.3 节点使用分析字段映射

| 分析指标 | 数据表 | 字段 | 说明 |
|---------|--------|------|------|
| 节点使用次数 | TemplateNodeStatistics | COUNT(*) | 按component_code分组统计 |
| 节点使用率 | TemplateNodeStatistics | COUNT(DISTINCT template_id) | 计算模板占比 |
| 节点成功率 | TaskflowExecutedNodeStatistics | status | 统计True占比 |
| 节点平均耗时 | TaskflowExecutedNodeStatistics | elapsed_time | AVG函数计算 |
| 节点组合 | pipeline_tree | flows | 分析source和target关系 |

---

## 八、关键依赖关系总结

### 8.1 数据依赖关系

1. **流程结构分析**：
   - 主要依赖：`pipeline_tree`（从PipelineTemplate.data获取）
   - 辅助依赖：`TemplateStatistics`（获取统计信息）

2. **流程执行分析**：
   - 主要依赖：`TaskflowStatistics`（执行记录）
   - 辅助依赖：`TaskFlowInstance`（任务状态）、`TaskflowExecutedNodeStatistics`（节点执行详情）

3. **节点使用分析**：
   - 主要依赖：`TemplateNodeStatistics`（节点引用）、`TaskflowExecutedNodeStatistics`（节点执行）
   - 辅助依赖：`pipeline_tree`（节点组合关系）

4. **业务场景分析**：
   - 主要依赖：`category`字段（从TaskTemplate和TaskflowStatistics）

5. **质量分析**：
   - 依赖：综合上述所有分析结果
   - 高级部分：还需要知识库支持

### 8.2 实施依赖关系

1. **基础分析**（阶段五基础部分）：
   - ✅ 可立即实施，无需等待知识库
   - 依赖：现有数据库表

2. **高级分析**（阶段五高级部分）：
   - ⚠️ 需要知识库构建完成后实施
   - 依赖：知识库中的模式知识和最佳实践知识

### 8.3 算法依赖关系

1. **独立算法**：
   - 流程结构分析算法
   - 流程执行分析算法
   - 业务场景分析算法

2. **依赖其他算法的算法**：
   - 质量分析算法（依赖上述所有算法的结果）

3. **依赖知识库的算法**：
   - 流程模式匹配算法
   - 节点组合模式识别算法
   - 基于最佳实践的质量分析算法

---

## 九、总结

本文档通过Mermaid图表清晰展示了：

1. **数据表关系**：核心数据表之间的关联关系
2. **数据流向**：从数据源到分析结果的完整数据流
3. **分析维度依赖**：各分析维度之间的依赖关系
4. **实施阶段依赖**：基础分析和高级分析的依赖关系
5. **字段映射关系**：分析指标与数据表字段的对应关系

这些图表为理解和实施流程分析系统提供了清晰的指导。

---

**文档版本**：v1.0
**创建时间**：2024-01-XX
**最后更新**：2024-01-XX
**文档状态**：已完成
