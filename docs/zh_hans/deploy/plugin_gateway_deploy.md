# 插件网关部署指南

本文说明插件网关上线后，如何完成代码发布、数据库迁移、来源配置初始化，以及 API 网关侧的资源同步。

## 1. 能力概览

当前插件网关由以下代码共同承载：

- Django app：`gcloud.plugin_gateway`
- APIGW 视图：`gcloud.apigw.views.plugin_gateway`
- APIGW 路径前缀：`/apigw/plugin-gateway/`

当前版本提供的能力包括：

- 内置插件与第三方插件的分类、列表、详情查询
- 插件执行登记
- 同步完成、轮询、回调三种执行模式
- 执行状态查询与详情查询，状态覆盖 `CREATED/RUNNING/WAITING_CALLBACK/SUCCEEDED/FAILED/CANCELLED`
- 取消执行
- 执行结果回调桥接
- 来源级白名单、黑名单、默认项目、空间项目映射与超时配置

当前版本的运行边界也需要明确：

- 插件执行采用组件运行壳，不创建标准运维引擎 `PipelineModel` 实例
- `context.operator` 会进入组件运行上下文，底层系统继续按真实操作人鉴权
- `context.scope_type/scope_value` 在标准运维侧解析为项目；解析失败时 run 会明确失败
- 运行壳上下文不完备的组件应配置到来源 `do_not_open_list`

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
- Celery Worker：至少包含 `open_plugin_dispatch`、`open_plugin_polling`、`open_plugin_callback` 三条队列
- Beat / Periodic Task 进程：用于周期性扫描超时 run

如环境按队列拆分 worker，可以参考：

```bash
python manage.py celery worker -l info -Q open_plugin_dispatch
python manage.py celery worker -l info -Q open_plugin_polling
python manage.py celery worker -l info -Q open_plugin_callback
```

`sweep_expired_plugin_gateway_runs` 由 beat 每 60 秒触发，建议确认 beat 配置已随代码发布生效。

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
        "scope_project_map": {
            "bkflow_space:space-1": 2001,
        },
        "do_not_open_list": ["builtin__unsafe_component"],
        "execution_timeout_seconds": 7200,
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
| `plugin_allow_list` | 遗留字段，不再参与执行准入；保留仅用于兼容已有配置 |
| `scope_project_map` | 当 `context.scope_type/scope_value` 无法按业务自动解析时的项目映射，键格式为 `<scope_type>:<scope_value>` |
| `do_not_open_list` | 来源级黑名单；命中后列表、详情、执行都会拦截 |
| `execution_timeout_seconds` | 单次执行的超时时间，超时后由周期任务置为失败 |
| `is_enabled` | 来源总开关 |

配置约束：

- `callback_domain_allow_list` 为空时，所有回调地址都会被拒绝
- 来源默认允许调用目录中的全部插件，无需维护 `plugin_allow_list`
- 不能通过运行壳安全执行的插件应加入 `do_not_open_list`
- `callback_domain_allow_list` 只应配置受信任平台域名
- 内置插件 ID 采用 `builtin__<component_code>`，第三方插件兼容裸 `code`

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
| `POST` | `/apigw/plugin-gateway/runs/{run_id}/internal-callback/` | 插件网关内部回调 |
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
    "plugin_id": "builtin__job_execute_task",
    "plugin_version": "legacy",
    "client_request_id": "demo_task_1_node_1_attempt_1",
    "callback_url": "https://bkflow.example.com/api/callback",
    "callback_token": "callback-token",
    "inputs": {
      "target_ip": "127.0.0.1"
    },
    "context": {
      "scope_type": "biz",
      "scope_value": "2",
      "operator": "bkflow-user",
      "space_id": "bkflow-space-1",
      "task_id": "demo_task_1",
      "node_id": "node_1"
    }
  }'
```

若成功，记录会先进入 `CREATED`，随后由 `open_plugin_dispatch` worker 推进到终态或异步等待态。

### 5.4 检查回调链路

当前版本包含两类回调链路：

- 回调型组件写回标准运维内部回调入口：`/apigw/plugin-gateway/runs/{run_id}/internal-callback/`
- 插件网关在 run 到达终态后回调消费方 `callback_url`

对消费方的终态回调会在单次回调内做有限重试：

- 最多重试 3 次
- 失败后记录日志并返回 `False`
- `callback_token` 会加密存储，回调时解密后写入 `X-Callback-Token`

建议在日志平台中关注包含 `[plugin_gateway] callback request failed` 的错误日志。

## 6. 当前版本的运维边界

上线后需要和接入方明确以下事实：

- 目录发现已覆盖内置插件和第三方插件
- 执行登记、同步完成、轮询、回调、详情、取消和终态回调已经可用
- BKFlow 只透传 `context`，项目解析在标准运维侧完成
- 插件执行不创建引擎实例，强依赖引擎节点态或全局变量解密的组件需要进入 `do_not_open_list`
- 第三方插件已从直连插件服务切到运行壳路径，上线前需要按接入来源做同步等价性回归
