<!-- TOC -->

- [如何从 bamboo-pipeline 升级至 bamboo-engine](#如何从-bamboo-pipeline-升级至-bamboo-engine)
  - [依赖升级](#依赖升级)
  - [修改项目配置](#修改项目配置)
  - [启动额外的 Worker 进程](#启动额外的-worker-进程)
  - [API 替换](#api-替换)
  - [* 可选项](#-可选项)

<!-- /TOC -->

## 如何从 bamboo-pipeline 升级至 bamboo-engine

`bamboo-engine` 和 `bamboo-pipeline` 不存在冲突，系统中可以同时启动和运行两套引擎

### 依赖升级

将 bamboo-pipeline 升级至 `3.1.0` 或以上版本

```
$ pip install bamboo-pipeline
```

### 修改项目配置

```python
from pipeline.celery.settings import *
from pipeline.eri.celery import queues
from celery import Celery

CELERY_QUEUES.extend(queues.CELERY_QUEUES)  # 向 broker 队列中添加 bamboo-engine 专用队列

app = Celery("proj")

app.config_from_object("django.conf:settings")

# 添加 INSTALLED_APPS
INSTALLED_APPS = [
    ...
    "pipeline.eri",
    ...
]
```

### 启动额外的 Worker 进程

```
$ python manage.py celery worker -Q er_execute,er_schedule -l info
```

### API 替换

按照如下映射进行 API 调用的替换：

- pipeline.service.task_service.run_pipeline: bamboo_engine.api.run_pipeline
- pipeline.service.task_service.pause_pipeline : bamboo_engine.api.pause_pipeline
- pipeline.service.task_service.revoke_pipeline : bamboo_engine.api.revoke_pipeline
- pipeline.service.task_service.resume_pipeline : bamboo_engine.api.resume_pipeline
- pipeline.service.task_service.pause_activity : bamboo_engine.api.pause_node_appoint
- pipeline.service.task_service.resume_activity : bamboo_engine.api.resume_node_appoint
- pipeline.service.task_service.retry_activity : bamboo_engine.api.retry_node
- pipeline.service.task_service.skip_activity : bamboo_engine.api.skip_node
- pipeline.service.task_service.skip_exclusive_gateway : bamboo_engine.api.skip_exclusive_gateway
- pipeline.service.task_service.forced_fail : bamboo_engine.api.forced_fail_activity
- pipeline.service.task_service.get_state : bamboo_engine.api.get_pipeline_states
- pipeline.service.task_service.get_topo_tree : 不再支持
- pipeline.service.task_service.get_inputs : bamboo_engine.api.get_execution_data_inputs
- pipeline.service.task_service.get_outputs : bamboo_engine.api.get_execution_data_outputs
- pipeline.service.task_service.get_activity_histories : bamboo_engine.api.get_node_histories
- pipeline.service.task_service.callback : bamboo_engine.api.callback
- pipeline.service.task_service.get_plain_log_for_node : pipeline.eri.runtime.BambooDjangoRuntime.get_plain_log_for_node


### * 可选项

- 将 pipeline.builder 包的所有引用切换至 bamboo_engine.builder 下
