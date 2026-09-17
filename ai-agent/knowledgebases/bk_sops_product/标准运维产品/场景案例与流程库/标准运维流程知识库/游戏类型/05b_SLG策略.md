# SLG 策略

> SLG 策略为传统 SLG 策略手游。运维流程特点是 GCS 工单+CDN 资源上传双轨发布、合服停服为核心场景、Spider 分布式数据库操作、GSE Kit 进程管理密度高。
>
> **216** 条流程 | **1** 个业务 | 平均节点数 7.9 | 中位节点数 4

---

## 流程特征

### 1. 组件使用特点

| 组件 | 使用次数 | SLG 策略特点 |
|------|---------|--------|
| job_fast_execute_script | 396 | 脚本执行 |
| job_execute_task | 322 | JOB 作业 |
| gsekit_job_exec | **222** | **GSE Kit 密度 1.03/流程 — 极高** |
| pause_node | 134 | 人工确认 |
| bk_notify | 100 | 通知 |
| job_fast_push_file | **98** | **文件分发密度 0.45/流程（CDN 资源包）** |
| sleep_timer | 92 | 定时 |
| remote_plugin | 86 | 远程插件 |
| gcs_bill_execute | **40** | **GCS 工单执行** |
| cc_batch_transfer_host_module | **26** | **CC 批量转移主机模块** |
| gsekit_flush_process | **23** | **GSE 刷新进程（进程热载入）** |
| gcs_spider_alter_bill | **10** | **GCS Spider 变更工单** |
| monitor_alarm_shield | 9 | 蓝鲸监控告警屏蔽 |

**核心差异化组件**：
- `gsekit_job_exec`（222 次，1.03/流程）：GSE Kit 进程管理使用极高，体现GCloud 对进程级操作（reload/hotfix/restart）的高频需求
- `gsekit_flush_process`（23 次）：GSE 进程热载入，不停服热更的关键组件
- `gcs_bill_execute`（40 次）+ `gcs_spider_alter_bill`（10 次）：GCS 工单+Spider 变更，合服/DB 操作
- `cc_batch_transfer_host_module`（26 次）：主机批量转移，合服/缩容场景
- `job_fast_push_file`（98 次，0.45/流程）：高频文件分发，客户端资源包+安卓/iOS 资源上传到 CDN

**高频远程插件**：

| 插件 | 次数 | 用途 |
|------|------|------|
| bkdbm-confirm | **22** | DBM 确认单据 |
| tcompose-exec | 11 | TCompose 执行 |
| facadesopsplugin | **7** | **Facade 插件（业务定制）** |
| bkchat-sops-send | 7 | BKChat 发送 |
| bot-approval | 6 | 机器人审批 |
| bkdbm-sqlexecute | 6 | DBM SQL 执行 |
| bkdbm-clearfiles | **5** | **DBM 文件清理** |
| tcompose-lbcopy | **3** | **TCompose 负载均衡复制** |
| bkdbm-spiderbu | **2** | **DBM Spider 备份** |

### 2. 流程结构特点

**网关使用**：

| 网关类型 | 次数 | 特点 |
|---------|------|------|
| ConvergeGateway | 48 | 汇聚 |
| ParallelGateway | 32 | 并行率 17.1% |
| ConditionalParallelGateway | **12** | 条件并行 2.8% |
| ExclusiveGateway | 10 | 排他率仅 4.2% |

**节点数分布**：
- p25=2, 中位=4, **p75=12**, max=53
- p75=12 较高，复杂流程（停服更新/合服）达 15-18 步

### 3. 场景分布

| 场景关键词 | 流程数 | 占比 | 特点 |
|-----------|--------|------|------|
| 更新 | 55 | **25.5%** | 最高频 |
| 停服 | 46 | **21.3%** | 停服占比极高 |
| 合服 | 33 | **15.3%** | **合服占比全类型最高** |
| 发布 | 19 | 8.8% | — |
| 灰度 | 11 | 5.1% | — |
| CDN | 10 | **4.6%** | CDN 资源上传 |
| DB | 8 | 3.7% | — |
| 开服 | 7 | 3.2% | — |
| 预发布 | 6 | 2.8% | — |
| 开区 | 5 | 2.3% | — |

---

## 关键检查点（Review 要点）

1. **停服更新+CDN 上传联动**：该类游戏的停服更新（21.3%）通常伴随客户端资源包上传 CDN，需确认 server 包+client 包+CDN 的一致性
2. **合服 Spider 操作安全性**：合服（15.3%）涉及 GCS Spider 变更+数据迁移，需确认备份和回滚策略
3. **GSE Kit 进程操作顺序**：GSE Kit（1.03/流程）高频使用，需确认 reload/hotfix/restart 的操作顺序和前后依赖
4. **多资源包上传一致性**：安卓+iOS 资源包分别上传 CDN，需确认两端资源版本一致
5. **热更不停服安全性**：gsekit_flush_process 用于不停服热更，需确认热更后的进程健康检查
6. **主机转移后资源回收**：cc_batch_transfer_host_module（26 次），合服/缩容后的主机需确认资源回收

---

## 代表性流程

**流程 1**：QA 客户端上传+停机更新（15 节点）
```
安卓资源包拉取到中转机 → iOS资源包拉取 → 安卓上传静态CDN×2 → FTP分发服务端文件 → 分发server包 → 更新server包 → gm进程停止 → 分发客户端文件 → 启动game进程 → 启动gm进程 → auth执行xmlreload
```
> 特点：客户端+服务端双轨更新，CDN 上传+进程管理联动

**流程 2**：不停服热更 Server 包（11 节点）
```
分发server包 → 更新server包 → 修改auth_version版本号 → auth执行xmlreload → game执行reload → game执行hotfix → game执行sysop → gm执行reload → gm执行hotfix → auth执行reload
```
> 特点：不停服热更的标准流程 — 多进程逐一 reload/hotfix

**流程 3**：推荐轮换（17 节点）
```
定时 → 计算平台数据查询 → python代码段 → 定时 → 1下推荐 → 1上推荐 → python代码段 → 2下推荐 → 计算平台查询 → bkchat通知
```
> 特点：数据驱动的运营操作，定时+数据查询+推荐轮换