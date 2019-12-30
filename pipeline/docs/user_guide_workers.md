## Celery Worker 配置

引擎中对不同类型的调度任务划分了不同的队列，建议按照如下的方式来启动 Celery Worker：

处理流程推进的 worker：

```shell
python manage.py celery worker -Q pipeline
```

处理轮询调度及回调请求的 worker：

```shell
celery worker -A {celery app path} -P gevent -Q service_schedule
```

处理其他事件的 worker：

```shell
python manage.py celery worker -Q pipeline_additional_task
```

