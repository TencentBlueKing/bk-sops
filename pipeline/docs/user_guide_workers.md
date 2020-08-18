<!-- TOC -->

- [Celery Worker 配置](#celery-worker-配置)
- [任务队列隔离](#任务队列隔离)

<!-- /TOC -->

## Celery Worker 配置

引擎中对不同类型的调度任务划分了不同的队列，建议按照如下的方式来启动 Celery Worker：

处理流程推进的 worker：

```shell
python manage.py celery worker -Q pipeline,pipeline_priority
```

处理轮询调度及回调请求的 worker：

```shell
celery worker -A {celery app path} -P gevent -Q service_schedule,service_schedule_priority
```

处理其他事件的 worker：

```shell
python manage.py celery worker -Q pipeline_additional_task,pipeline_additional_task_priority
```

## 任务队列隔离

有时候我们的使用场景中，我们不希望一些任务的执行被其他任务执行影响，这个时候我们可以通过添加自定义的队列来解决这个问题：

```python
from pipeline.celery.queues import ScalableQueues

ScalableQueues.add(name='custom_queue_1')
ScalableQueues.add(name='custom_queue_2')

# 在完成队列添加操作后再进行 celery settings 的导入操作
from pipeline.celery.settings import *
```

这样我们就能够在执行任务的时候选择我们创建的自定义队列：

```python
task_service.run_pipeline(pipeline, queue='custom_queue_1')
```

当然，为了实现队列隔离的效果，我们要为我们自定义的队列启动专用的 worker：

```shell
python manage.py celery worker -Q {queue_name}_pipeline_priority,{queue_name}_service_schedule_priority,pipeline_additional_task_priority
```

其中 `{queue_name}` 需要替换为我们添加的自定义队列的名称；当然，如果你添加了多个自定义队列，就要为每个队列都启动一批 worker。以上面的例子来看，我们添加了两个自定义队列 `custom_queue_1` 和 `custom_queue_2`，那我们就要启动两个丢应的 worker：

```shell
python manage.py celery worker -Q custom_queue_1_pipeline_priority,custom_queue_1_service_schedule_priority

python manage.py celery worker -Q custom_queue_2_pipeline_priority,custom_queue_2_service_schedule_priority
```