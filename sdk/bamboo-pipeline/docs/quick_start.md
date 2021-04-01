## pipeline

pipeline 是标准运维 v3 内部使用的任务调度引擎，其主要职责是解析，执行，管理由用户创建的流程任务，并提供了如暂停，撤销，跳过和重试等灵活的控制能力和并行、子流程等进阶特性，并可通过水平扩展来进一步提升任务的并发处理能力。

## 起步

### 初始化

由于 pipeline 依赖 Django ORM，所以必须作为一个 Django APP 嵌入到 Django 项目中使用。

首先将 pipeline，django_signal_valve 项目拷贝到当前 Django 目录下，并在 Django 工程的 `INSTALLED_APPS` 中添加以下 APP:

```python
(
    ...
    'pipeline',
    'pipeline.log',
    'pipeline.engine',
    'pipeline.component_framework',
    'pipeline.django_signal_valve',
    'djcelery',
     ...
)
```

并在 Django 工程根目录下运行 `python manage.py migrate` 初始化数据库。

### 环境准备

在使用 pipeline 前，需要启动 celery-worker：

```shell
python manage.py celery worker
```

### 执行一个简单的流程

你只需要根据规范提供一个流程描述结构，并使用 `PipelineParser` 将其转换为 `Pipeline` 对象，当然，你也可以自己组装 `Pipeline` 对象，只不过这样会比较繁琐。下面的结构就描述了一个简单的流程，流程示意图如下：

![simple example](https://raw.githubusercontent.com/homholueng/md_pic/master/pipeline_doc/simple_example.png)

下面让我们创建出这个流程并让他跑起来：

```python
from pipeline import builder
from pipeline.builder import EmptyStartEvent, ServiceActivity, EmptyEndEvent
from pipeline.parser import PipelineParser
from pipeline.service import task_service

# 使用 builder 构造出流程描述结构
start = EmptyStartEvent()
act = ServiceActivity(component_code='example_component')
end = EmptyEndEvent()

start.extend(act).extend(end)

tree = builder.build_tree(start)

# 根据流程描述结构创建流程对象
parser = PipelineParser(pipeline_tree=tree)
pipeline = parser.parse()

# 执行流程对象
task_service.run_pipeline(pipeline)
```

流程开始执行后，可以通过 `task_service.get_state` 接口获取流程当前执行状态：

```bash
>>> task_service.get_state(pipeline.id)

{'children': {u'5740b0a1f8b03f9fb82c3690a41c6b10': {'finish_time': '2019-03-27 06:56:16',
   'id': u'5740b0a1f8b03f9fb82c3690a41c6b10',
   'loop': 1L,
   'retry': 0L,
   'skip': False,
   'start_time': '2019-03-27 06:56:16',
   'state': 'FINISHED'},
  u'6930365c0c73358dbefb9c2d25922e0f': {'finish_time': '2019-03-27 06:56:16',
   'id': u'6930365c0c73358dbefb9c2d25922e0f',
   'loop': 1L,
   'retry': 0L,
   'skip': False,
   'start_time': '2019-03-27 06:56:16',
   'state': 'FINISHED'},
  u'd29a8ef1ec7f367e9724415e03de22ab': {'finish_time': '2019-03-27 06:56:16',
   'id': u'd29a8ef1ec7f367e9724415e03de22ab',
   'loop': 1L,
   'retry': 0L,
   'skip': False,
   'start_time': '2019-03-27 06:56:16',
   'state': 'FINISHED'}},
 'finish_time': '2019-03-27 06:56:16',
 'id': u'3a07e1b279a83df2bf15f6b094901303',
 'loop': 1L,
 'retry': 0L,
 'skip': False,
 'start_time': '2019-03-27 06:56:16',
 'state': 'FINISHED'}
```

> Tips：如果在调用 `task_service.get_state` 时抛出了 InvalidOperationException: node does not exist, may have not by executed 异常，请确认 Celery Worker 是否成功启动并接收到了任务，以及检查传递给 `task_service.get_state` 的节点 ID 是否正确。

可以看到，整个流程很快就执行完了，恭喜你，你已经成功的把一个流程运行起来了！

### 接下来

- [基础概念](./user_guide_basic_concept.md)
- [流程编排](./user_guide_flow_orchestration.md)
- [流程构造器](./user_guide_flow_builder.md)
- [SPLICE 变量](./user_guide_splice_var.md)
- [流程管理](./user_guide_flow_management.md)
- [自定义组件](./user_guide_custom_component.md)
- [组件管理](./user_guide_component_management.md)
- [运行自定义组件](./user_guide_run_your_component.md)
- [组件单元测试](./user_guide_component_unit_test.md)
- [Worker 配置](./user_guide_workers.md)
- [自定义配置](./user_guide_config.md)
- [卡死任务检测](./user_guide_zombie_process.md)
- API Reference
  - [pipeline.service.task_service](./api_reference/pipeline.service.task_service.md)