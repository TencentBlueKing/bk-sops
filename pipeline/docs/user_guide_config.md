

## 配置项

### PIPELINE_DATA_BACKEND

引擎在执行过程中用户数据交换的主要后端，默认值为 `pipeline.engine.core.data.mysql_backend.MySQLDataBackend`。

可选值为：
- `pipeline.engine.core.data.mysql_backend.MySQLDataBackend`：使用 MySQL 作为数据交换后端。
- `pipeline.engine.core.data.redis_backend.RedisDataBackend`：使用 Redis 作为数据交换后端。

注意，在使用 Redis 作为数据交换后端时，需要在 `settings.py` 中配置 Redis 的连接信息：

```python
redis = {
    'host': 'xxxxx',
    'port': '6379',
    # 以下为可选配置
    'mode': 'single', # 默认为单实例模式，可选值为: replication(使用了 redis sentinel 的集群), cluster(集群模式), single(单实例)
    'password': 'xxx', # 没有密码则不需要配置
    'service_name': 'mymaster', # replication 模式下的 service name
    'db': 0 # single 模式下使用的 db
}
```

### PIPELINE_DATA_CANDIDATE_BACKEND

引擎在执行过程中用户数据交换的备用后端，当引擎操作主要后端 `PIPELINE_DATA_BACKEND` 失败时，会转而去请求备用后端

可选值为：
- `pipeline.engine.core.data.mysql_backend.MySQLDataBackend`：使用 MySQL 作为数据交换后端。
- `pipeline.engine.core.data.redis_backend.RedisDataBackend`：使用 Redis 作为数据交换后端。

建议将 DB 作为引擎的备用后端使用

### PIPELINE_DATA_BACKEND_AUTO_EXPIRE

引擎数据交换主要后端中的数据是否设置自动过期，默认为 `False`，当值为 `True` 时，`PIPELINE_DATA_BACKEND` 与 `PIPELINE_DATA_CANDIDATE_BACKEND` 两者都不能为空。

### PIPELINE_DATA_BACKEND_AUTO_EXPIRE_SECONDS

引擎数据交换主要后端中的数据自动过期的时间，单位为秒，默认为 1 天。

### PIPELINE_WORKER_STATUS_CACHE_EXPIRES

对 celery worker 状态的缓存时间，单位为秒，默认值为 `30`。

### PIPELINE_RERUN_MAX_TIMES

节点允许循环执行的最大次数，为 `0` 则不限制，默认值为 `0`。

### COMPONENT_PATH

需要额外在每个 `INSTALLED_APP` 下扫描自定义插件的路径列表，如：

```python
COMPONENT_PATH = [
    'mycomponents.collections',
]
```

### VARIABLE_PATH

需要额外在每个 `INSTALLED_APP` 下扫描自定义变量的路径列表，如：

```python
VARIABLE_PATH = [
    'myvariables.collections',
]
```

### ENABLE_EXAMPLE_COMPONENTS

是否要加载示例插件，默认为 `True`。

### UUID_DIGIT_STARTS_SENSITIVE

是否对引擎自动生成的 UUID 首位字符敏感，默认为 `False`，若将该值设置为 `True`，则生成的 UUID 一定会以英文字符开头。

### EXTERNAL_PLUGINS_SOURCE_PROXY

远程插件源加载时的代理配置，配置示例：

```python
proxies = {
  "http": "http://host:3128",
  "https": "http://host:1080",
}
```

### EXTERNAL_PLUGINS_SOURCE_SECURE_RESTRICT

是否强制远程插件源使用安全协议，默认为 `True`。

### ENGINE_ZOMBIE_PROCESS_DOCTORS

处理僵尸进程的 doctor 配置，可参考 [僵尸进程](./user_guide_zombie_process.md)

### ENGINE_ZOMBIE_PROCESS_HEAL_CRON

处理僵尸进程的周期任务调度规则配置，可参考 [僵尸进程](./user_guide_zombie_process.md)
