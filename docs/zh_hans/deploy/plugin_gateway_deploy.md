# 插件网关部署指南

本文说明插件网关上线后，如何完成代码发布、数据库迁移、来源配置初始化，以及 API 网关侧的资源同步。

## 1. 能力概览

当前插件网关由以下代码共同承载：

- Django app：`gcloud.plugin_gateway`
- APIGW 视图：`gcloud.apigw.views.plugin_gateway`
- APIGW 路径前缀：`/apigw/plugin-gateway/`

当前版本提供的能力包括：

- 插件分类、列表、详情查询
- 插件执行登记
- 执行状态查询与详情查询
- 取消执行
- 执行结果回调桥接
- 来源级白名单与默认项目配置

当前版本的边界也需要明确：

- 目录接口可以直接对外使用
- 执行接口当前负责“登记执行 + 状态持久化 + 回调桥接”
- 当前版本不会自动把请求同步转发到真实标准插件运行时

## 2. 发布步骤

### 2.1 发布代码

将包含 `gcloud.plugin_gateway` 和 `gcloud.apigw.views.plugin_gateway` 变更的版本发布到部署环境。

### 2.2 安装依赖

如部署流程会重建 Python 运行环境，请按常规方式安装依赖：

```bash
pip install -r requirements.txt
```

### 2.3 执行数据库迁移

插件网关新增了以下模型：

- `PluginGatewaySourceConfig`
- `PluginGatewayRun`

部署后必须执行迁移：

```bash
python manage.py migrate
```

如需只迁移该 app，可执行：

```bash
python manage.py migrate plugin_gateway
```

### 2.4 重启服务

部署后应至少重启：

- Web 进程
- Celery Worker
- Beat / Periodic Task 进程（若你的环境单独部署）

当前版本没有新增独立的插件网关 worker，因此不需要单独拉起新的进程组。

## 3. 初始化来源配置

当前版本没有独立的来源配置页面，`PluginGatewaySourceConfig` 需要通过 Django shell、初始化脚本或数据迁移录入。

推荐在 Django shell 中初始化：

```bash
python manage.py shell
```

```python
from gcloud.plugin_gateway.models import PluginGatewaySourceConfig

PluginGatewaySourceConfig.objects.update_or_create(
    source_key="bkflow",
    defaults={
        "display_name": "BKFlow",
        "default_project_id": 2001,
        "callback_domain_allow_list": ["bkflow.example.com"],
        "plugin_allow_list": ["plugin_job_execute", "plugin_job_status"],
        "is_enabled": True,
    },
)
```

字段说明：

| 字段 | 说明 |
|------|------|
| `source_key` | 消费方调用时使用的来源标识 |
| `display_name` | 来源展示名 |
| `default_project_id` | 未传 `project_id` 时的默认回填值 |
| `callback_domain_allow_list` | 允许回调的域名白名单 |
| `plugin_allow_list` | 当前来源允许调用的插件 ID 白名单 |
| `is_enabled` | 来源总开关 |

配置约束：

- `callback_domain_allow_list` 为空时，所有回调地址都会被拒绝
- `plugin_allow_list` 为空时，所有插件都会被拒绝
- `callback_domain_allow_list` 只应配置受信任平台域名

## 4. API 网关资源与文档同步

插件网关接口已统一收敛到 APIGW 体系下，相关产物位于：

- 资源定义：`gcloud/apigw/management/commands/data/api-resources.yml`
- 网关定义：`gcloud/apigw/management/commands/data/api-definition.yml`
- 资源文档归档：`gcloud/apigw/docs/apigw-docs.tgz`

当前需要同步的资源如下：

| 方法 | 资源路径 | 说明 |
|------|----------|------|
| `GET` | `/apigw/plugin-gateway/categories/` | 查询分类 |
| `GET` | `/apigw/plugin-gateway/plugins/` | 查询插件列表 |
| `GET` | `/apigw/plugin-gateway/plugins/{plugin_id}/` | 查询插件详情 |
| `POST` | `/apigw/plugin-gateway/runs/` | 创建执行记录 |
| `GET` | `/apigw/plugin-gateway/runs/status/` | 轮询执行状态 |
| `GET` | `/apigw/plugin-gateway/runs/{run_id}/` | 查询执行详情 |
| `POST` | `/apigw/plugin-gateway/runs/{run_id}/cancel/` | 取消执行 |

同步建议：

1. 更新 `api-resources.yml`
2. 同步更新 `docs/{zh_hans,en}/apidoc/*.md`
3. 重新打包 `gcloud/apigw/docs/apigw-docs.tgz`
4. 再执行现有的 APIGW 同步命令

## 5. 部署后检查

### 5.1 检查来源配置

```bash
python manage.py shell -c "
from gcloud.plugin_gateway.models import PluginGatewaySourceConfig
print(list(PluginGatewaySourceConfig.objects.values('source_key', 'is_enabled')))
"
```

### 5.2 检查目录接口

```bash
curl -X GET 'https://{gateway-host}/apigw/plugin-gateway/plugins/' \
  -H 'X-Bkapi-Authorization: ...'
```

### 5.3 检查执行登记

```bash
curl -X POST 'https://{gateway-host}/apigw/plugin-gateway/runs/' \
  -H 'Content-Type: application/json' \
  -H 'X-Bkapi-Authorization: ...' \
  -d '{
    "source_key": "bkflow",
    "plugin_id": "plugin_job_execute",
    "plugin_version": "1.2.0",
    "client_request_id": "demo_task_1_node_1_attempt_1",
    "callback_url": "https://bkflow.example.com/api/callback",
    "callback_token": "callback-token",
    "inputs": {
      "target_ip": "127.0.0.1"
    }
  }'
```

若成功，记录会进入 `WAITING_CALLBACK`。

### 5.4 检查回调链路

当前版本会在单次回调内做有限重试：

- 最多重试 3 次
- 失败后记录日志并返回 `False`
- `callback_token` 会加密存储，回调时解密后写入 `X-Callback-Token`

建议在日志平台中关注包含 `[plugin_gateway] callback request failed` 的错误日志。

## 6. 当前版本的运维边界

上线后需要和接入方明确以下事实：

- 目录发现能力已经可用
- 执行登记、轮询、详情、取消和结果回调已经可用
- 当前版本尚未自动调度真实标准插件运行时

因此在真实插件调度适配完成前，应将本版本视为“开放网关层”，而不是“真实执行代理层”。
