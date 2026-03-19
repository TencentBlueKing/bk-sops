# 标准运维（BK-SOPS）技术文档

## 目录

- [项目概述](#项目概述)
- [项目架构](#项目架构)
- [功能说明](#功能说明)
- [代码结构](#代码结构)
- [数据库结构](#数据库结构)
- [功能模块](#功能模块)
- [技术栈](#技术栈)
- [部署架构](#部署架构)

---

## 项目概述

**标准运维（BK-SOPS）** 是腾讯蓝鲸产品体系中一款轻量级的调度编排类 SaaS 产品，通过可视化的图形界面进行任务流程编排和执行。

### 核心价值

- **流程编排服务**：基于蓝鲸 PaaS 平台的 API 网关服务，对接企业内部各个系统 API 的能力，将在多系统间切换的工作模式整合到一个流程中，实现一键自动化调度
- **自助化服务**：屏蔽底层系统之间的差异，让运维人员可以将业务日常的运维工作交给产品、开发、测试等人员执行，实现业务发布、变更等日常工作的自助化

### 版本信息

- **当前版本**：3.32.9
- **开发语言**：Python (Django)
- **前端框架**：Vue.js
- **底层引擎**：[bamboo-engine](https://github.com/TencentBlueKing/bamboo-engine)

---

## 项目架构

### 逻辑架构（四层架构）

```
┌─────────────────────────────────────────────────────────────┐
│                     接入层 (Access Layer)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  权限控制     │  │  API接口     │  │  数据统计     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   任务管理层 (Task Management Layer)         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  流程编排     │  │  任务控制     │  │  插件框架     │    │
│  │  - 模板管理   │  │  - 创建任务   │  │  - 标准插件   │    │
│  │  - 可视化编辑 │  │  - 暂停/继续 │  │  - 自定义插件 │    │
│  │               │  │  - 撤销任务   │  │  - 变量引擎   │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   流程引擎层 (Pipeline Engine Layer)         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  任务执行引擎 │  │  流程控制     │  │  上下文管理   │      │
│  │  - Bamboo    │  │  - 串行/并行  │  │  - 变量传递   │      │
│  │  - Engine    │  │  - 分支选择   │  │  - 状态管理   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   API 网关层 (API Gateway Layer)              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  蓝鲸API网关  │  │  第三方系统   │  │  插件服务     │      │
│  │  - CMDB      │  │  - 企业内部   │  │  - 远程插件   │      │
│  │  - Job       │  │  - 自定义系统  │  │  - 本地插件   │      │
│  │  - Monitor    │  │               │  │               │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### 技术架构

```
┌─────────────────────────────────────────────────────────────┐
│                        前端层 (Frontend)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  Desktop Web │  │  Mobile Web  │  │  静态资源     │    │
│  │  (Vue.js)    │  │  (Vue.js)     │  │  (Components)│    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            ↓ HTTP/WebSocket
┌─────────────────────────────────────────────────────────────┐
│                      Web服务层 (Web Services)                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  Web Server  │  │  Callback    │  │  API Gateway │    │
│  │  (Gunicorn)  │  │  Server      │  │  (DRF)        │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   业务逻辑层 (Business Logic)                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  TaskFlow    │  │  TaskTemplate│  │  Pipeline    │    │
│  │  Management  │  │  Management  │  │  Engine      │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   异步任务层 (Async Workers)                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  Celery      │  │  Pipeline    │  │  Schedule    │    │
│  │  Workers     │  │  Workers     │  │  Workers     │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                     数据存储层 (Data Storage)                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   MySQL      │  │   Redis       │  │   RabbitMQ   │    │
│  │  (主数据)     │  │  (缓存/锁)    │  │  (消息队列)   │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

---

## 功能说明

### 核心功能

#### 1. 流程编排
- **可视化流程设计**：通过拖拽方式组合标准插件节点到一个流程模板
- **多种流程模式**：
  - 串行执行：节点按顺序执行
  - 并行执行：多个节点同时执行
  - 子流程：支持流程嵌套
  - 条件分支：根据全局参数自动选择分支执行
  - 失败处理：节点失败处理机制可配置（重试、跳过、终止等）

#### 2. 任务执行
- **任务创建**：基于流程模板创建任务实例
- **任务控制**：
  - 启动任务
  - 暂停任务
  - 继续任务
  - 撤销任务
  - 节点重试
  - 节点跳过
- **实时监控**：任务执行状态实时展示，支持执行日志查看

#### 3. 标准插件
- **官方插件库**：对接蓝鲸通知、作业平台、配置平台等服务
- **自定义插件**：支持用户自定义接入企业内部系统，定制开发标准插件
- **插件类型**：
  - 标准插件（原子）：基础执行单元
  - 子流程插件：流程嵌套
  - 远程插件：通过插件服务远程加载

#### 4. 参数引擎
- **参数共享**：支持流程内参数共享
- **参数替换**：支持变量替换和表达式计算
- **全局变量**：支持全局变量定义和使用
- **参数校验**：任务创建时进行参数校验

#### 5. 周期任务
- **定时任务**：支持 Cron 表达式配置
- **计划任务**：支持一次性计划任务
- **任务历史**：记录周期任务执行历史

#### 6. 权限管理
- **项目权限**：基于项目的权限控制
- **模板权限**：流程模板的使用权限控制
- **IAM 集成**：与蓝鲸 IAM 权限中心集成
- **角色管理**：通过配置平台同步业务角色

#### 7. 轻应用（Mini App）
- **快速接入**：为业务提供快速接入能力
- **职能化**：降低非运维人员的操作成本
- **移动端支持**：支持移动端访问

#### 8. 数据统计
- **任务统计**：任务执行情况统计
- **模板统计**：流程模板使用情况统计
- **节点统计**：节点执行情况统计

### 扩展功能

- **审计中心**：操作记录审计
- **标签管理**：流程模板和任务标签管理
- **公共流程**：跨项目共享流程模板
- **外部插件**：支持外部插件源管理
- **项目常量**：项目级别的常量定义
- **资源筛选**：集群和主机资源筛选配置

---

## 代码结构

### 目录结构

```
bk-sops/
├── gcloud/                          # 标准运维业务层
│   ├── core/                       # 核心业务逻辑
│   │   ├── models.py              # 核心数据模型（Project, Business等）
│   │   ├── apis/                   # API接口
│   │   ├── urls.py                 # URL路由
│   │   └── utils/                  # 工具函数
│   ├── taskflow3/                  # 任务管理模块
│   │   ├── models.py              # 任务实例模型
│   │   ├── apis/                   # 任务API
│   │   ├── domains/                # 领域逻辑
│   │   │   ├── dispatchers/       # 任务调度器
│   │   │   └── context.py          # 任务上下文
│   │   ├── signals/               # 信号处理
│   │   └── celery/                 # Celery任务
│   ├── tasktmpl3/                  # 流程模板管理模块
│   │   ├── models.py              # 模板模型
│   │   ├── apis/                   # 模板API
│   │   └── domains/                # 领域逻辑
│   ├── common_template/           # 公共模板模块
│   ├── periodictask/              # 周期任务模块
│   ├── clocked_task/              # 计划任务模块
│   ├── apigw/                     # API网关模块
│   ├── iam_auth/                  # IAM权限认证
│   ├── analysis_statistics/      # 统计分析模块
│   ├── external_plugins/         # 外部插件管理
│   └── contrib/                   # 贡献模块
│       ├── cleaner/              # 数据清理
│       ├── notice/               # 通知服务
│       └── audit/                # 审计服务
├── pipeline/                      # 流程引擎核心（bamboo-engine）
│   ├── engine/                   # 执行引擎
│   ├── eri/                      # 执行运行时接口
│   └── models.py                 # 引擎数据模型
├── pipeline_web/                 # 流程引擎前端适配层
│   ├── core/                     # 核心抽象
│   ├── parser/                   # 数据解析
│   └── preview.py                # 预览功能
├── pipeline_plugins/             # 标准插件库
│   ├── components/              # 标准插件组件
│   │   ├── collections/        # 插件集合
│   │   │   ├── sites/          # 站点插件
│   │   │   │   ├── open/      # 开放平台插件
│   │   │   │   │   ├── job/   # 作业平台插件
│   │   │   │   │   ├── cc/    # 配置平台插件
│   │   │   │   │   └── ...
│   │   │   │   └── ...
│   │   │   └── common.py       # 通用插件基类
│   │   └── controller.py      # 插件控制器
│   └── variables/               # 变量插件
├── plugin_service/              # 插件服务
│   ├── api.py                  # 插件服务API
│   ├── plugin_client.py        # 插件客户端
│   └── client_decorators.py    # 客户端装饰器
├── frontend/                    # 前端代码
│   ├── desktop/                # 桌面端前端
│   │   └── src/               # Vue.js源码
│   └── mobile/                # 移动端前端
├── config/                      # 配置文件
│   ├── default.py             # 默认配置
│   ├── dev.py                 # 开发环境配置
│   └── prod.py                # 生产环境配置
├── api/                        # 蓝鲸API SDK
│   ├── collections/           # API集合
│   └── client.py             # API客户端
├── docs/                       # 文档
├── bin/                        # 脚本文件
│   ├── start_web.sh          # Web服务启动脚本
│   └── celery_auto_restart.sh # Celery自动重启脚本
└── app_desc.yaml              # 应用描述文件
```

### 核心模块说明

#### 1. gcloud/core - 核心模块
- **models.py**：核心数据模型
  - `Project`：项目模型
  - `Business`：业务模型
  - `ProjectConfig`：项目配置
  - `EngineConfig`：引擎配置
- **apis/**：核心API接口
- **utils/**：工具函数

#### 2. gcloud/taskflow3 - 任务管理模块
- **models.py**：任务实例模型
  - `TaskFlowInstance`：任务实例
  - `TaskConfig`：任务配置
  - `TimeoutNodeConfig`：节点超时配置
- **domains/**：领域逻辑
  - `dispatchers/`：任务和节点调度器
  - `context.py`：任务上下文管理
- **signals/**：Django信号处理
- **celery/**：异步任务

#### 3. gcloud/tasktmpl3 - 模板管理模块
- **models.py**：模板模型
  - `TaskTemplate`：任务模板
- **domains/**：模板领域逻辑
- **apis/**：模板API

#### 4. pipeline_plugins - 标准插件库
- **components/collections/**：插件集合
  - `common.py`：插件基类
  - `controller.py`：插件控制器
  - `sites/open/`：开放平台插件
- **variables/**：变量插件

#### 5. pipeline - 流程引擎
- **engine/**：执行引擎
- **eri/**：执行运行时接口
- **models.py**：引擎数据模型

---

## 数据库结构

### 核心数据表

#### 1. 项目相关表

**gcloud_core_project** - 项目表
```sql
- id: 主键
- name: 项目名称
- bk_biz_id: 业务ID（CMDB）
- time_zone: 时区
- creator: 创建人
- desc: 描述
- from_cmdb: 是否来自CMDB
- create_time: 创建时间
- update_time: 更新时间
```

**gcloud_core_business** - 业务表
```sql
- id: 主键
- cc_id: CMDB业务ID（唯一）
- cc_name: 业务名称
- cc_owner: 开发商账号
- cc_company: 开发商ID
- time_zone: 时区
- life_cycle: 生命周期
- executor: 任务执行者
- status: 业务状态
```

**gcloud_core_projectconfig** - 项目配置表
```sql
- id: 主键
- project_id: 项目ID
- custom_display_configs: 自定义显示配置（JSON）
- create_time: 创建时间
- update_time: 更新时间
```

#### 2. 模板相关表

**tasktmpl3_tasktemplate** - 任务模板表
```sql
- id: 主键
- project_id: 项目ID
- pipeline_template_id: 流程模板ID（关联pipeline_pipeline_template）
- name: 模板名称
- category: 模板分类
- creator: 创建人
- create_time: 创建时间
- edit_time: 编辑时间
- is_deleted: 是否删除
- template_source: 模板来源（项目/公共）
```

**pipeline_pipeline_template** - 流程模板表（引擎层）
```sql
- id: 主键
- instance_id: 实例ID
- name: 模板名称
- creator: 创建人
- create_time: 创建时间
- snapshot_id: 快照ID
- is_started: 是否已启动
- is_finished: 是否已完成
- is_revoked: 是否已撤销
```

#### 3. 任务相关表

**taskflow3_taskflowinstance** - 任务实例表
```sql
- id: 主键
- project_id: 项目ID
- template_id: 模板ID
- pipeline_instance_id: 流程实例ID（关联pipeline_pipeline_instance）
- name: 任务名称
- creator: 创建人
- create_time: 创建时间
- start_time: 开始时间
- finish_time: 完成时间
- category: 任务分类
- create_info: 创建信息（JSON）
- engine_ver: 引擎版本
```

**pipeline_pipeline_instance** - 流程实例表（引擎层）
```sql
- id: 主键
- instance_id: 实例ID
- name: 实例名称
- creator: 创建人
- start_time: 开始时间
- finish_time: 完成时间
- is_started: 是否已启动
- is_finished: 是否已完成
- is_revoked: 是否已撤销
- snapshot_id: 快照ID
- template_id: 模板ID
```

**pipeline_eri_state** - 节点状态表（引擎层）
```sql
- id: 主键
- node_id: 节点ID
- root_id: 根节点ID（流程实例ID）
- parent_id: 父节点ID
- name: 状态名称（RUNNING, SUCCESS, FAILED等）
- version: 版本
- loop: 循环次数
- inner_loop: 内部循环次数
- skip: 是否跳过
- retry: 重试次数
- start_time: 开始时间
- archive_time: 归档时间
```

**pipeline_eri_schedule** - 节点调度表（引擎层）
```sql
- id: 主键
- node_id: 节点ID
- root_id: 根节点ID
- schedule_id: 调度ID
- schedule_times: 调度次数
- wait_callback: 是否等待回调
- callback_data: 回调数据（JSON）
- expired_time: 过期时间
```

#### 4. 周期任务相关表

**periodictask_periodictask** - 周期任务表
```sql
- id: 主键
- project_id: 项目ID
- template_id: 模板ID
- name: 任务名称
- cron: Cron表达式
- enabled: 是否启用
- creator: 创建人
- create_time: 创建时间
- last_run_at: 最后运行时间
- total_run_count: 总运行次数
```

**periodictask_periodictaskhistory** - 周期任务历史表
```sql
- id: 主键
- periodic_task_id: 周期任务ID
- taskflow_id: 任务流ID
- exe_data: 执行数据（JSON）
- start_at: 开始时间
- start_success: 是否启动成功
```

#### 5. 插件相关表

**pipeline_componentmodel** - 组件模型表
```sql
- id: 主键
- code: 组件代码
- name: 组件名称
- status: 状态
- version: 版本
- group: 分组
```

**gcloud_external_plugins_packagesource** - 外部插件源表
```sql
- id: 主键
- name: 插件源名称
- base_url: 基础URL
- headers: 请求头（JSON）
- enabled: 是否启用
```

#### 6. 统计分析相关表

**analysis_statistics_taskflowstatistics** - 任务流统计表
```sql
- id: 主键
- instance_id: 实例ID
- atom_total: 原子节点总数
- subprocess_total: 子流程总数
- gateways_total: 网关总数
```

**analysis_statistics_templatestatistics** - 模板统计表
```sql
- id: 主键
- template_id: 模板ID
- atom_total: 原子节点总数
- subprocess_total: 子流程总数
- gateways_total: 网关总数
```

#### 7. 其他重要表

**gcloud_label_label** - 标签表
```sql
- id: 主键
- name: 标签名称
- project_id: 项目ID
```

**gcloud_projectconstants_projectconstant** - 项目常量表
```sql
- id: 主键
- project_id: 项目ID
- key: 常量键
- value: 常量值
- desc: 描述
```

**gcloud_contrib_operaterecord_taskoperaterecord** - 任务操作记录表
```sql
- id: 主键
- operator: 操作人
- operate_type: 操作类型
- operate_source: 操作来源
- instance_id: 实例ID
- project_id: 项目ID
- operate_date: 操作时间
```

### 数据库关系图

```
Project (项目)
  ├── TaskTemplate (模板) 1:N
  │     └── TaskFlowInstance (任务) 1:N
  │           └── PipelineInstance (流程实例) 1:1
  │                 └── State (节点状态) 1:N
  │                 └── Schedule (节点调度) 1:N
  ├── PeriodicTask (周期任务) 1:N
  ├── ProjectConfig (项目配置) 1:1
  └── ProjectConstant (项目常量) 1:N
```

---

## 功能模块

### 1. 流程编排模块 (tasktmpl3)

**功能**：
- 流程模板的创建、编辑、删除
- 可视化流程设计
- 模板版本管理
- 模板导入导出
- 模板权限管理

**核心类**：
- `TaskTemplate`：模板模型
- `TaskTemplateManager`：模板管理器
- `TaskTemplateViewSet`：模板视图集

**关键API**：
- `/api/v3/tasktmpl3/templates/` - 模板列表
- `/api/v3/tasktmpl3/templates/{id}/` - 模板详情
- `/api/v3/tasktmpl3/templates/{id}/create_task/` - 创建任务

### 2. 任务执行模块 (taskflow3)

**功能**：
- 任务创建和执行
- 任务控制（暂停、继续、撤销）
- 节点操作（重试、跳过）
- 任务状态查询
- 任务日志查看

**核心类**：
- `TaskFlowInstance`：任务实例模型
- `TaskCommandDispatcher`：任务命令调度器
- `NodeCommandDispatcher`：节点命令调度器
- `TaskContext`：任务上下文

**关键API**：
- `/api/v3/taskflow3/tasks/` - 任务列表
- `/api/v3/taskflow3/tasks/{id}/` - 任务详情
- `/api/v3/taskflow3/tasks/{id}/operate/` - 任务操作
- `/api/v3/taskflow3/tasks/{id}/nodes/{node_id}/operate/` - 节点操作

### 3. 周期任务模块 (periodictask)

**功能**：
- 周期任务创建和管理
- Cron表达式配置
- 任务启用/禁用
- 执行历史查询

**核心类**：
- `PeriodicTask`：周期任务模型
- `PeriodicTaskHistory`：周期任务历史

**关键API**：
- `/api/v3/periodictask/tasks/` - 周期任务列表
- `/api/v3/periodictask/tasks/{id}/` - 周期任务详情
- `/api/v3/periodictask/tasks/{id}/set_enabled/` - 启用/禁用

### 4. 计划任务模块 (clocked_task)

**功能**：
- 一次性计划任务创建
- 计划时间配置
- 任务通知配置

**核心类**：
- `ClockedTask`：计划任务模型

### 5. 公共模板模块 (common_template)

**功能**：
- 公共模板管理
- 模板共享
- 模板导入导出

**核心类**：
- `CommonTemplate`：公共模板模型

### 6. 插件管理模块 (external_plugins)

**功能**：
- 外部插件源管理
- 插件同步
- 插件版本管理

**核心类**：
- `PackageSource`：插件源模型
- `SyncTask`：同步任务模型

### 7. 统计分析模块 (analysis_statistics)

**功能**：
- 任务执行统计
- 模板使用统计
- 节点执行统计
- 项目维度统计

**核心类**：
- `TaskflowStatistics`：任务流统计
- `TemplateStatistics`：模板统计
- `TaskflowExecutedNodeStatistics`：节点统计

### 8. 权限认证模块 (iam_auth)

**功能**：
- IAM权限集成
- 资源权限管理
- 权限拦截

**核心类**：
- `IAMInterceptor`：IAM拦截器
- `ResourceHelper`：资源助手

### 9. API网关模块 (apigw)

**功能**：
- 对外API接口
- API文档生成
- API权限控制

**关键API**：
- `/api/v3/apigw/` - API网关入口

### 10. 数据清理模块 (contrib/cleaner)

**功能**：
- 过期数据清理
- 任务数据清理
- 引擎数据清理

**核心类**：
- `CleanExpiredV2TaskData`：清理过期任务数据

---

## 技术栈

### 后端技术

- **框架**：Django 3.x
- **API框架**：Django REST Framework (DRF)
- **异步任务**：Celery + RabbitMQ
- **数据库**：MySQL
- **缓存**：Redis
- **Web服务器**：Gunicorn (gthread模式)
- **流程引擎**：bamboo-engine (自研)

### 前端技术

- **框架**：Vue.js 2.x
- **构建工具**：Webpack
- **UI组件**：Element UI
- **图表**：ECharts

### 开发工具

- **版本控制**：Git
- **代码规范**：ESLint, Pylint
- **测试框架**：pytest, Django TestCase
- **文档生成**：Swagger/OpenAPI

---

## 部署架构

### 模块划分

根据 `app_desc.yaml` 配置，系统分为以下模块：

#### 1. default 模块（主服务）
- **Web服务**：5个副本，4C2G5R
- **Celery Beat**：1个副本，4C1G5R（定时任务调度）
- **Celery Worker**：5个副本，4C2G5R（异步任务处理）

#### 2. callback 模块（回调服务）
- **Web服务**：5个副本，4C5G5R（专门处理插件回调）

#### 3. pipeline 模块（流程引擎服务）
- **v1-engine**：2个副本，4C1G5R（V1引擎）
- **api-er-e**：4个副本，4C1G5R（API执行队列）
- **api-er-s**：4个副本，4C1G5R（API调度队列）
- **api-task**：2个副本，4C1G5R（API任务队列）
- **cworker**：2个副本，4C1G5R（通用工作队列）
- **er-e**：2个副本，4C2G5R（执行队列）
- **er-s**：2个副本，4C2G5R（调度队列）
- **peri-er-e**：2个副本，4C1G5R（周期任务执行）
- **peri-er-s**：2个副本，4C1G5R（周期任务调度）
- **stats-worker**：2个副本，4C1G5R（统计队列）
- **cleaner**：2个副本，4C1G5R（清理队列）
- **web**：1个副本，4C1G5R（Celery监控）
- **node-timeout**：1个副本，4C1G5R（节点超时处理）

#### 4. api 模块（API服务）
- **Web服务**：5个副本，4C2G5R

### 服务依赖

- **MySQL**：主数据库
- **RabbitMQ**：消息队列
- **Redis**：缓存和分布式锁
- **BKRepo**：文件存储
- **OTEL**：可观测性

### 队列说明

**Celery队列划分**：
- `default`：默认队列
- `pipeline`：流程执行队列
- `pipeline_priority`：流程优先级队列
- `er_execute`：执行队列
- `er_schedule`：调度队列
- `er_execute_api`：API执行队列
- `er_schedule_api`：API调度队列
- `task_prepare_api`：任务准备队列
- `task_callback`：任务回调队列
- `node_auto_retry`：节点自动重试队列
- `timeout_node_execute`：超时节点执行队列
- `task_data_clean`：数据清理队列

---

## 附录

### 相关文档

- [架构设计](overview/architecture.md)
- [代码目录](overview/code_structure.md)
- [使用场景](overview/usecase.md)
- [开发指南](develop/dev_plugins.md)
- [API文档](apidoc/)

### 相关链接

- [GitHub仓库](https://github.com/TencentBlueKing/bk-sops)
- [蓝鲸文档](https://bk.tencent.com/docs/)
- [bamboo-engine](https://github.com/TencentBlueKing/bamboo-engine)

---

**文档版本**：1.0
**最后更新**：2024年
**维护者**：BK-SOPS团队











