# 灰度升级设计：master → release_humming_bird 双版本并行部署

## 背景

需要在不修改代码的前提下，将标准运维从 master 分支灰度升级到 release_humming_bird (hb) 分支。两个版本共享同一份 DB 数据，用户可通过不同入口访问新旧版本，任务数据、流程配置等完全不受影响。

## 分支差异摘要

| 维度 | master | release_humming_bird |
|------|--------|---------------------|
| Django | 3.2.25 | 4.2.20 |
| Celery | 4.4.0 | 5.2.7 |
| bamboo-pipeline | 3.24.2 | 4.0.0 |
| Python | 3.6/3.7 | 3.11 |
| 前端 | 103 文件变更，无新状态码 | 新增 PENDING_APPROVAL / PENDING_CONFIRMATION / PENDING_PROCESSING |

### DB 差异

- master 独有字段：`ai_notify_type`、`ai_notify_group`（BaseTemplate 子类），对应 migration `common_template/0010`、`tasktmpl3/0020`
- hb 独有 migration：django-celery-beat 0016-0019（4个 AlterField）、django-celery-results 0009-0011（新建 GroupResult 表 + AddField + 索引调整）
- bamboo-pipeline 3.24.2 → 4.0.0：DB migration 完全一致，无新增

### API 兼容性

- hb 删除的 7 个 apigw view（create_template、get_node_job_executed_log 等）均为外部网关/内部服务接口，**前端不调用**
- hb 内部 status API 硬编码 `with_new_status=True`，会返回 master 前端不认识的状态码
- 影响范围仅限含暂停节点（pause_node）和审批节点（bk_approve）的任务

## 方案设计

### 架构

```
                    ┌─ 旧版入口 (old.sops.example.com) ─┐
                    │  master 后端 (Django 3.2, Py3.6)   │
                    │  仅 web 进程 (gunicorn)             │
                    │  ❌ 不启动 celery worker            │
用户 → Nginx ──────┤                                      ├──→ 共享 MySQL
                    │  新版入口 (new.sops.example.com)    │
                    │  hb 后端 (Django 4.2, Py3.11)      │
                    │  web 进程 + ✅ celery workers       │
                    └────────────────────────────────────┘
                                    ↕
                              共享 Redis (broker)
```

核心原则：
- 两套独立运行环境，各自的 Python 版本和依赖
- 共享同一个 MySQL 和 Redis
- **celery worker + celery beat 只在 hb 环境启动**
- master 部署仅提供 web 服务（gunicorn），不启动任何后台任务进程

---

## 操作 Checklist

### 阶段一：准备工作

- [ ] **1.1 备份当前生产数据库**
  ```bash
  mysqldump -h <host> -u <user> -p <dbname> \
    --single-transaction --routines --triggers \
    > backup_$(date +%Y%m%d_%H%M%S).sql
  ```

- [ ] **1.2 确认当前 DB migration 状态**
  ```bash
  # 在 master 环境中执行
  python manage.py showmigrations --plan | grep '\[ \]'
  # 输出应为空，表示所有 migration 都已 applied
  ```

- [ ] **1.3 记录当前进行中的任务数**
  ```sql
  SELECT COUNT(*) AS running_tasks
  FROM pipeline_pipelineinstance
  WHERE is_started=1 AND is_finished=0 AND is_revoked=0;
  ```
  建议在任务量低谷时段操作，等待进行中任务自然完成。

- [ ] **1.4 准备两套独立运行环境**

  | 环境 | Python | 代码分支 | 用途 |
  |------|--------|---------|------|
  | 环境 A | 3.6 或 3.7 | master | 仅 web |
  | 环境 B | 3.11 | release_humming_bird | web + celery |

  各自安装依赖：
  ```bash
  # 环境 A
  pip install -r requirements.txt

  # 环境 B
  pip install -r requirements.txt
  ```

- [ ] **1.5 构建前端**
  ```bash
  # 环境 A (master)
  cd frontend/desktop && npm install && npm run build
  # 产物在 frontend/desktop/static/

  # 环境 B (hb)
  cd frontend/desktop && npm install && npm run build
  ```

### 阶段二：DB 迁移

- [ ] **2.1 在 hb 环境中执行 migrate**
  ```bash
  # 环境 B (hb)
  python manage.py migrate
  ```
  预期行为：
  - 补跑 `django_celery_beat` 的 0016、0017、0018、0019
  - 补跑 `django_celery_results` 的 0009、0010、0011
  - master 的 `common_template/0010` 和 `tasktmpl3/0020` 在 DB 中标记为 applied 但 hb 代码中无对应文件 — **这是正常的**

- [ ] **2.2 验证 migration 状态一致性**
  ```bash
  # 环境 B (hb) — 确认第三方 migration 已 applied
  python manage.py showmigrations django_celery_beat django_celery_results
  # 应显示全部 [X]

  # 环境 A (master) — 确认不报错
  python manage.py check
  python manage.py showmigrations django_celery_beat django_celery_results
  # 0016-0019 和 0009-0011 会显示为 applied，master 代码中无对应文件
  # Django 不会因此报错，只是 showmigrations 显示异常
  ```

- [ ] **2.3 确认字段兼容性**
  ```sql
  -- master 的 ai_notify_type/ai_notify_group 列应仍然存在
  -- hb 不引用它们，但不会报错（Django 忽略 model 未定义的列）
  -- master 正常读写它们
  SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS
  WHERE TABLE_NAME = 'common_template_commontemplate'
    AND COLUMN_NAME IN ('ai_notify_type', 'ai_notify_group');
  -- 应返回 2 行

  -- hb 新增的 GroupResult 表应已创建
  SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES
  WHERE TABLE_NAME = 'django_celery_results_groupresult';
  -- 应返回 1

  -- celery_results 新增列应已存在
  SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS
  WHERE TABLE_NAME = 'django_celery_results_taskresult'
    AND COLUMN_NAME = 'periodic_task_name';
  -- 应返回 1 行
  ```

### 阶段三：部署 hb 实例（新版）

- [ ] **3.1 配置 hb 环境变量**
  ```bash
  # 必须与 master 指向相同的 MySQL 和 Redis
  export MYSQL_HOST=<共享MySQL地址>
  export MYSQL_PORT=<端口>
  export MYSQL_NAME=<数据库名>
  export MYSQL_USER=<用户>
  export MYSQL_PASSWORD=<密码>
  export BKAPP_SOPS_BROKER_URL=redis://<共享Redis地址>:<端口>/0

  # hb 特有配置（根据需要调整）
  # export BKAPP_TASK_STATUS_DISPLAY_VERSION=v2  # 默认 v2，启用新状态展示
  ```

- [ ] **3.2 部署 hb 前端静态资源**
  ```bash
  # 按标准流程部署前端
  rm -rf ./static/bk_sops
  cp -r ./frontend/desktop/static ./static/bk_sops
  mv ./static/bk_sops/index.html ./gcloud/core/templates/core/base_vue.html
  python manage.py collectstatic --noinput
  ```

- [ ] **3.3 启动 hb web 进程**
  ```bash
  gunicorn wsgi -w <workers> -b 0.0.0.0:8001
  ```

- [ ] **3.4 启动 hb celery workers（全局唯一的一套 worker）**
  ```bash
  celery -A blueapps.core.celery worker -l info -c <concurrency>
  celery -A blueapps.core.celery beat -l info
  ```

- [ ] **3.5 验证 hb 部署**
  - 访问 hb 前端，确认页面正常加载
  - 创建测试任务并执行，确认 celery 正常消费
  - 查看任务状态，确认新状态（等待审批等）正常展示

### 阶段四：切换 master 实例为 web-only

- [ ] **4.1 优雅停止 master 的 celery workers**
  ```bash
  # 发送 SIGTERM，等待当前任务完成后退出
  celery -A blueapps.core.celery control shutdown
  ```

- [ ] **4.2 等待进行中任务完成**
  ```sql
  -- 反复查询直到为 0，或确认剩余任务可以由 hb worker 接管
  SELECT COUNT(*) FROM pipeline_pipelineinstance
  WHERE is_started=1 AND is_finished=0 AND is_revoked=0;
  ```

- [ ] **4.3 停止 master 的 celery beat**
  ```bash
  # 确保 beat 已停止，避免重复调度
  kill <celery_beat_pid>
  ```

- [ ] **4.4 确认 master 环境变量指向相同的 MySQL 和 Redis**
  ```bash
  export MYSQL_HOST=<同一个MySQL地址>
  export BKAPP_SOPS_BROKER_URL=redis://<同一个Redis地址>:<端口>/0
  # ...其他配置与生产一致
  ```

- [ ] **4.5 master 仅启动 web 进程**
  ```bash
  gunicorn wsgi -w <workers> -b 0.0.0.0:8000
  # ❌ 不执行 celery worker
  # ❌ 不执行 celery beat
  ```

### 阶段五：Nginx 配置

- [ ] **5.1 配置双入口**
  ```nginx
  # 旧版入口
  server {
      listen 80;
      server_name old.sops.example.com;

      location /static/ {
          alias /path/to/master/staticfiles/;
      }

      location / {
          proxy_pass http://127.0.0.1:8000;
          proxy_set_header Host $host;
          proxy_set_header X-Real-IP $remote_addr;
          proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
          proxy_set_header X-Forwarded-Proto $scheme;
      }
  }

  # 新版入口
  server {
      listen 80;
      server_name new.sops.example.com;

      location /static/ {
          alias /path/to/hb/staticfiles/;
      }

      location / {
          proxy_pass http://127.0.0.1:8001;
          proxy_set_header Host $host;
          proxy_set_header X-Real-IP $remote_addr;
          proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
          proxy_set_header X-Forwarded-Proto $scheme;
      }
  }
  ```

- [ ] **5.2 Reload Nginx**
  ```bash
  nginx -t && nginx -s reload
  ```

- [ ] **5.3 验证双入口可访问**
  ```bash
  curl -I http://old.sops.example.com/
  curl -I http://new.sops.example.com/
  ```

### 阶段六：功能验证

- [ ] **6.1 旧版入口 (master 前端) 基础验证**
  - [ ] 流程模板列表正常加载
  - [ ] 查看已有任务详情正常
  - [ ] 新建任务并选择执行方案正常
  - [ ] 启动任务 → 任务正常执行（由 hb celery worker 消费）
  - [ ] 任务完成后状态显示正确
  - [ ] 周期任务正常触发

- [ ] **6.2 新版入口 (hb 前端) 基础验证**
  - [ ] 同上基础功能
  - [ ] 新增的状态展示（等待审批/等待确认/等待处理）正常
  - [ ] 独立子流程状态下钻正常
  - [ ] 用户收藏项目功能正常

- [ ] **6.3 交叉验证**
  - [ ] 在旧版创建的任务，在新版能正常查看和操作
  - [ ] 在新版创建的任务，在旧版能正常查看和操作
  - [ ] 确认旧版查看含暂停/审批节点任务时的表现（会显示原始状态码字符串，非功能性问题）

- [ ] **6.4 异常场景验证**
  - [ ] 在旧版创建含暂停节点的任务，执行后在两个入口分别查看状态
  - [ ] 强制失败一个节点，确认两个入口都能正确展示和操作
  - [ ] 测试任务重试、跳过等操作在两个入口的一致性

---

## 已知限制

### 1. master 前端状态码显示

hb 后端内部 status API 硬编码 `with_new_status=True`，对于含以下节点的任务，master 前端会显示原始状态码而非中文标签：

| hb 状态码 | 含义 | master 前端显示 |
|-----------|------|----------------|
| `PENDING_APPROVAL` | 等待审批 | 显示原始字符串 "PENDING_APPROVAL" |
| `PENDING_CONFIRMATION` | 等待确认 | 显示原始字符串 "PENDING_CONFIRMATION" |
| `PENDING_PROCESSING` | 等待处理 | 显示原始字符串 "PENDING_PROCESSING" |

**影响范围**：仅限使用了 `bk_approve`（审批）或 `pause_node`（暂停）插件的任务。普通任务的 RUNNING/FAILED/FINISHED/SUSPENDED 状态完全正常。

**若不可接受**：需在 hb 后端的 `gcloud/taskflow3/apis/django/api.py` 中 `status()` 和 `batch_status()` 函数做约 4 行修改，根据请求来源（Header/Cookie）决定传 `with_new_status=True` 还是 `False`。

### 2. django_migrations 表残留记录

两个环境的 `django_migrations` 表会有对方不认识的 migration 记录：
- master 环境：`django_celery_beat/0016-0019` 和 `django_celery_results/0009-0011` 标记为 applied 但无对应文件
- hb 环境：`common_template/0010` 和 `tasktmpl3/0020` 标记为 applied 但无对应文件

**影响**：`manage.py showmigrations` 显示异常，`manage.py check` 和正常运行不受影响。

### 3. Celery 消息兼容性

master 后端（celery 4.4.0）创建任务时发送的 celery 消息由 hb 的 celery 5.2.7 worker 消费。两者均使用 pickle 序列化。

- Celery 5 向后兼容 celery 4 的消息协议（protocol 2）
- Python 3.11 能反序列化 Python 3.6/3.7 的 pickle 数据
- bamboo-pipeline 两个版本使用相同的 DB schema

**建议**：上线前在测试环境做完整的端到端验证，覆盖各种节点类型（标准插件、子流程、并行网关等）。

### 4. 外部 API 网关客户端

hb 删除了 7 个 apigw view（`create_template`、`get_node_job_executed_log` 等）。如果有外部系统通过 API 网关调用这些接口，需要将其路由到 master 后端，或提前通知外部系统切换。

---

## 回滚方案

1. 停止 hb 所有进程（web + celery workers + beat）
2. 在 master 环境重新启动 celery workers 和 beat
3. Nginx 切回仅指向 master
4. DB 中 hb 补跑的 7 个第三方 migration 创建的表/列不影响 master 运行（Django 忽略 model 未定义的表和列）
5. 无需回滚 DB

---

## 最终下线旧版

当确认所有用户已迁移到新版后：

1. 停止 master web 进程
2. Nginx 移除旧版入口配置
3. （可选）清理 `django_migrations` 表中 master 独有的 migration 记录：
   ```sql
   DELETE FROM django_migrations
   WHERE app = 'template' AND name = '0010_auto_20260210_0022';
   DELETE FROM django_migrations
   WHERE app = 'tasktmpl3' AND name = '0020_auto_20260210_0022';
   ```
4. （可选）删除 DB 中残留的 `ai_notify_type` 和 `ai_notify_group` 列：
   ```sql
   ALTER TABLE common_template_commontemplate
     DROP COLUMN ai_notify_type,
     DROP COLUMN ai_notify_group;
   ALTER TABLE tasktmpl3_tasktemplate
     DROP COLUMN ai_notify_type,
     DROP COLUMN ai_notify_group;
   ```
