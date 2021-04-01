<!-- TOC -->

- [Celery Worker 配置](#celery-worker-配置)
  - [Worker Pool 的选择](#worker-pool-的选择)
- [任务队列隔离](#任务队列隔离)

<!-- /TOC -->

## Celery Worker 配置

引擎中对不同类型的调度任务划分了不同的队列，建议按照如下的方式来启动 Celery Worker：

处理流程推进的 worker：

```shell
python manage.py celery worker -Q er_execute
```

处理轮询调度及回调请求的 worker：

```shell
python manage.py celery worker -Q er_schedule
```

### Worker Pool 的选择

Celery worker 默认使用 prefork 模式来启动，如果要提高系统的流程执行并发量，建议安装 gevent 并以 gevent 模式启动：

```python
$ pip install gevent
$ python manage.py celery worker -Q er_execute,er_schedule -P gevent -c 500
```

更多 celery worker pool 的介绍请参考 [celery workers](https://docs.celeryproject.org/en/stable/userguide/workers.html#concurrency)

## 任务队列隔离

有时候我们的使用场景中，我们不希望一些任务的执行被其他任务执行影响，这个时候我们可以通过添加自定义的队列来解决这个问题：

```python
from pipeline.eri.celery.queues import *
from celery import Celery

# 添加 API 队列
CELERY_QUEUES.extend(QueueResolver("api").queues())

app = Celery("proj")

app.config_from_object("django.conf:settings")
```

这样我们就能够在执行任务的时候选择我们创建的自定义队列：

```python
api.run_pipeline(runtime, pipeline, queue='api')
```

当然，为了实现队列隔离的效果，我们要为我们自定义的队列启动专用的 worker：

```shell
python manage.py celery worker -Q er_execute_api,er_schedule_api
```

如果你添加了多个自定义队列，就要为每个队列都启动一批 worker。
