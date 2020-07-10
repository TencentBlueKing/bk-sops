<!-- TOC -->

- [流程构造器](#流程构造器)
- [构造元素](#构造元素)
  - [event](#event)
    - [EmptyStartEvent](#emptystartevent)
    - [EmptyEndEvent](#emptyendevent)
    - [ExecutableEndEvent](#executableendevent)
  - [activity](#activity)
    - [ServiceActivity](#serviceactivity)
    - [SubProcess](#subprocess)
  - [gateway](#gateway)
    - [ParallelGateway](#parallelgateway)
    - [ExclusiveGateway](#exclusivegateway)
    - [ConditionalParallelGateway](#conditionalparallelgateway)
    - [ConvergeGateway](#convergegateway)
  - [data](#data)
    - [Data](#data-1)
    - [Var](#var)
    - [NodeOutput](#nodeoutput)
    - [RewritableNodeOutput](#rewritablenodeoutput)
    - [Params](#params)
    - [DataInput](#datainput)
- [连接构造元素](#连接构造元素)
  - [extend](#extend)
  - [connect](#connect)
  - [converge](#converge)
  - [to](#to)
- [生成流程描述结构](#生成流程描述结构)

<!-- /TOC -->
## 流程构造器

回到 Quick Start 中的例子，可以看到，流程对象的生成分为两个步骤：

1. 构造流程描述结构
2. 根据流程描述结构生成 `Pipeline` 对象


```python
from pipeline import builder
from pipeline.builder import EmptyStartEvent, ServiceActivity, EmptyEndEvent
from pipeline.parser import PipelineParser

# 1. 构造流程描述结构
start = EmptyStartEvent()
act = ServiceActivity(component_code='example_component')
end = EmptyEndEvent()

start.extend(act).extend(end)

tree = builder.build_tree(start)

# 2. 根据流程描述结构生成流程对象
parser = PipelineParser(pipeline_tree=tree)
pipeline = parser.parse()

# 执行流程对象
task_service.run_pipeline(pipeline)
```

流程构造器的职责是降低我们构造流程描述结构的成本，可以看到上面的例子中构造的流程只有三个节点，但是通过这三个节点生成的描述结构却十分的复杂：

```bash
>>> tree = builder.build_tree(start)
>>> tree
{'activities': {'d29a8ef1ec7f367e9724415e03de22ab': {'component': {'code': 'example_component',
    'inputs': {}},
   'error_ignorable': False,
   'id': 'd29a8ef1ec7f367e9724415e03de22ab',
   'incoming': ['ee7124a9bcf337308aff8fcc0a674782'],
   'name': None,
   'optional': False,
   'outgoing': 'c43b3a60c86b36ac91e177b02abe7800',
   'type': 'ServiceActivity'}},
 'data': {'inputs': {}, 'outputs': {}},
 'end_event': {'id': '6930365c0c73358dbefb9c2d25922e0f',
  'incoming': ['c43b3a60c86b36ac91e177b02abe7800'],
  'name': None,
  'outgoing': '',
  'type': 'EmptyEndEvent'},
 'flows': {'c43b3a60c86b36ac91e177b02abe7800': {'id': 'c43b3a60c86b36ac91e177b02abe7800',
   'is_default': False,
   'source': 'd29a8ef1ec7f367e9724415e03de22ab',
   'target': '6930365c0c73358dbefb9c2d25922e0f'},
  'ee7124a9bcf337308aff8fcc0a674782': {'id': 'ee7124a9bcf337308aff8fcc0a674782',
   'is_default': False,
   'source': '5740b0a1f8b03f9fb82c3690a41c6b10',
   'target': 'd29a8ef1ec7f367e9724415e03de22ab'}},
 'gateways': {},
 'id': '3a07e1b279a83df2bf15f6b094901303',
 'start_event': {'id': '5740b0a1f8b03f9fb82c3690a41c6b10',
  'incoming': '',
  'name': None,
  'outgoing': 'ee7124a9bcf337308aff8fcc0a674782',
  'type': 'EmptyStartEvent'}}
```

如果要手动去拼接这样的一个结构，这简直就是一个灾难，所以，使用流程构造器能够大大的降低我们构造复杂流程的成本。

## 构造元素

要使用流程构造器，首先我们需要创建构造流程时要使用到的构造元素，**构造元素指的是*流程元素*的替代对象**，每个构造元素都拥有一个到流程元素的唯一映射，且构造元素拥有与其所对应的流程元素相同的类名。下面所展示的代码片段中创建除了三个流程元素：`start`，`act` 及 `end`。

```python
from pipeline import builder
from pipeline.builder import EmptyStartEvent, ServiceActivity, EmptyEndEvent
from pipeline.parser import PipelineParser

start = EmptyStartEvent()
act = ServiceActivity(component_code='example_component')
end = EmptyEndEvent()
```

目前可用的构造元素（等同于可用的流程元素）如下所示：

- event 类型
  - `EmptyStartEvent`：空开始事件。
  - `EmptyEndEvent`：空结束事件。
  - `ExecutableEndEvent`：可执行结束事件。
- activity 类型
  - `ServiceActivity`：服务活动。
  - `SubProcess`：子流程。
- gateway 类型
  - `ParallelGateway`：并行网关。
  - `ExclusiveGateway`：分支网关。
  - `ConditionalParallelGateway`：条件并行网关。
  - `ConvergeGateway`：汇聚网关。
- data 类型
  - `Data`：Data 所对应的构造对象
  - `Params`：声明子流程中全局变量对父流程中中全局变量引用的参数对象
  - `Var`：代表流程中变量的构造对象
  - `DataInput`：用于声明子流程 Data 中对外暴露参数的构造对象
  - `NodeOutput`：用于声明对其他节点输出的结果引用的构造对象
  - `RewritableNodeOutput`：用于声明对多个节点输出的结果引用的构造对象，每次其引用的节点执行后，该变量的值会刷新为该节点中对应的输出值

### event

#### EmptyStartEvent

空开始事件

```python
EmptyStartEvent(id=None, name=None, outgoing=None)
```

- id：节点 ID，可为空，为空时框架自动生成
- name：节点名，可为空，为空时框架自动生成
- outgoing：输出节点数组，可为空

#### EmptyEndEvent

空结束事件

```python
EmptyEndEvent(id=None, name=None, outgoing=None)
```

- id：节点 ID，可为空，为空时框架自动生成
- name：节点名，可为空，为空时框架自动生成
- outgoing：输出节点数组，可为空

#### ExecutableEndEvent

可自定义执行逻辑的结束事件

```python
ExecutableEndEvent(type, id=None, name=None, outgoing=None)
```
- type：自定义业务逻辑结束节点的名称（在 `FlowNodeClsFactory` 中注册的 name）
- id：节点 ID，可为空，为空时框架自动生成
- name：节点名，可为空，为空时框架自动生成
- outgoing：输出节点数组，可为空

### activity

#### ServiceActivity

服务节点，可绑定特定的组件执行特定的逻辑

```python
ServiceActivity(id=None, 
                name=None,
                outgoing=None,
                component_code=None,
                failure_handler=None,
                error_ignorable=False,
                timeout=None,
                skippable=True,
                retryable=True)
```

- id：节点 ID，可为空，为空时框架自动生成
- name：节点名，可为空，为空时框架自动生成
- outgoing：输出节点数组，可为空
- component_code：服务节点绑定的 [component](./user_guide_custom_component.md) code
- failure_handler：节点执行失败时调用的自定义 handler 函数，签名应为 `failure_handler(data, parent_data)`
- error_ignorable：是否忽略执行中的错误或执行失败
- timeout：执行超时时间，单位为秒
- skippable：在执行出错或失败后是否能够手动跳过
- retryable：在执行出错或失败后是否能够手动重试

#### SubProcess

子流程节点，可关联特定的流程

```python
SubProcess(id=None, 
          name=None,
          outgoing=None,
          start=None,
          data=None,
          params=None,
          replace_id=False,
          template_id=None)
```

- id：节点 ID，可为空，为空时框架自动生成
- name：节点名，可为空，为空时框架自动生成
- outgoing：输出节点数组，可为空
- start：子流程引用流程的 `EmptyStartEvent` builder 对象，start 与 template_id 参数不能同时为空，当两者都不为空时优先使用 template_id
- data：子流程的 `Data` 对象
- params：子流程的传入参数，可以是 `dict` 或是 `pipeline.builder.flow.data.Params` 类型
- replace_id：是否需要在 `build_tree` 时替换该子流程节点所引用的所有 builder 对象的 ID，该选项只有在使用 start 关键字关联流程时生效
- template_id：该子流程节点所关联的 `pipeline.models.PipelineTemplate` 的 template_id，start 与 template_id 参数不能同时为空，当两者都不为空时优先使用 template_id，PipelineTemplate 相关的使用方式可参考[流程管理](./user_guide_flow_management.md)

### gateway

#### ParallelGateway

并行网关

```python
ParallelGateway(id=None, name=None, outgoing=None)
```

- id：节点 ID，可为空，为空时框架自动生成
- name：节点名，可为空，为空时框架自动生成
- outgoing：输出节点数组，可为空


#### ExclusiveGateway

分支网关

```python
ExclusiveGateway(id=None, name=None, outgoing=None, condition=None)
```

- id：节点 ID，可为空，为空时框架自动生成
- name：节点名，可为空，为空时框架自动生成
- outgoing：输出节点数组，可为空
- condition：分支网关中每个输出节点对应的条件映射，应为 `{node_index: "condition", ...}` 形式的字典，其中 node_index 为输出节点在 ExclusiveGateway outgoing 字段中的下标，condition 为节点执行需要满足的分支条件

#### ConditionalParallelGateway

条件并行网关

```python
ConditionalParallelGateway(id=None, name=None, outgoing=None, condition=None)
```

- id：节点 ID，可为空，为空时框架自动生成
- name：节点名，可为空，为空时框架自动生成
- outgoing：输出节点数组，可为空
- condition：条件并行网关中每个输出节点对应的条件映射，应为 `{node_index: "condition", ...}` 形式的字典，其中 node_index 为输出节点在 ConditionalParallelGateway outgoing 字段中的下标，condition 为节点执行需要满足的分支条件

#### ConvergeGateway

汇聚网关

```python
ConvergeGateway(id=None, name=None, outgoing=None)
```

- id：节点 ID，可为空，为空时框架自动生成
- name：节点名，可为空，为空时框架自动生成
- outgoing：输出节点数组，可为空


### data

#### Data

Data 所对应的构造对象

```python
Data(inputs=None, outputs=None)
```

- inputs：Data 对象的 inputs 字典，默认为 `{}`
- outputs：Data 对象的 outputs 字典，默认为 `{}`

#### Var

代表流程中变量的构造对象

```python
Var(type, value, custom_type=None)
```

- type：变量的类型，其取值范围为 `{Var.PLAIN, Var.SPLICE, Var.LAZY}`
- value：变量的值
- custom_type type 为 `Var.LAZY` 时，该变量对应的 [LazyVariable](./user_guide_lazy_variable.md) 的 code

#### NodeOutput

用于声明对其他节点输出的结果引用的构造对象

```python
NodeOutput(type, source_act, source_key)
```

- type：变量的类型，其取值范围为 `{Var.PLAIN, Var.SPLICE, Var.LAZY}`，该字段的取值目前不会影响 NodeOutput 的行为
- source_act：要引用的变量所属的输出节点 ID
- source_key：要引用的变量在其节点被输出后的 key

#### RewritableNodeOutput

用于声明对多个节点输出的结果引用的构造对象，每次其引用的节点执行后，该变量的值会刷新为该节点中对应的输出值

```python
RewritableNodeOutput(type, source_act)
```

- type：变量的类型，其取值范围为 `{Var.PLAIN, Var.SPLICE, Var.LAZY}`，该字段的取值目前不会影响 RewritableNodeOutput 的行为
- source_act：要引用的输出节点与其变量的映射数组，其形式应为 `[{'source_act': act_id, 'source_key': key}, ...]`，其中 source_act 为要引用的变量所属的输出节点 ID，source_key 为要引用的变量在其节点被输出后的 key

#### Params

声明子流程中全局变量对父流程中中全局变量引用的参数对象

```python
Params(params=None)
```

- params：记录子流程全局变量对父流程变量引用的 `dict`，其形式应为 `{key: Var(...)}`，其中 key 为子流程中变量的 key，Var 为 `Var` 构造对象实例，相关概念可以参考[子流程参数传递](./user_guide_basic_concept.md#子流程参数传递（Param）)

#### DataInput

用于声明子流程 Data 中对外暴露参数的构造对象，相关概念可以参考[子流程参数传递](./user_guide_basic_concept.md#子流程参数传递（Param）)

```python
Var(type, value, source_tag=None)
```

- type：变量的类型，其取值范围为 `{Var.PLAIN, Var.SPLICE, Var.LAZY}`
- value：变量的值
- source_tag：当 type 为 `Var.LAZY` 时，该变量对应的 [LazyVariable](./user_guide_lazy_variable.md) 的 code

## 连接构造元素

当我们创建好了构造元素之后，我们还需要将这些构造元素根据我们的需要连接起来，构造元素提供了若干方法来帮助我们应对各种场景下的元素连接操作。

### extend

`extend()` 方法会创建一条从调用者到传入元素的连接，并返回作为参数传入的构造元素：


```bash
>>> from pipeline.builder import ServiceActivity
>>> act_1 = ServiceActivity(name='act_1')
>>> act_2 = ServiceActivity(name='act_2')

>>> act_1.extend(act_2)
<ServiceActivity act_2:ba3dea8b2c6f32c09cf0f62feed9ec09>
```

通过使用 `extend()` 链式调用能够快速构造出一个简单的串行流程：

```bash
>>> from pipeline.builder import EmptyStartEvent, ServiceActivity, EmptyEndEvent
>>> start = EmptyStartEvent(name='start')
>>> act_1 = ServiceActivity(name='act_1')
>>> act_2 = ServiceActivity(name='act_2')
>>> act_3 = ServiceActivity(name='act_3')
>>> end = EmptyEndEvent(name='end')

>>> start.extend(act_1).extend(act_2).extend(act_3).extend(end)
<EmptyEndEvent end:aaca723bebf332fc8d6588ae0c109f47>

```

### connect

`connect()` 方法能够接收多个构造元素作为参数，并为每一个传入的构造元素构建一条由调用者到该元素的连接，并返回当前调用对象。当我们要构造的流程中含有分支或是并行结构时，这个方法能够帮助我们快速构造出这样的结构：

```bash
>>> from pipeline.builder import ServiceActivity, ParallelGateway
>>> parallel_gateway = ParallelGateway(name='parallel_gateway')
>>> act_1 = ServiceActivity(name='act_1')
>>> act_2 = ServiceActivity(name='act_2')
>>> act_3 = ServiceActivity(name='act_3')

>>> parallel_gateway.connect(act_1, act_2, act_3)
<ParallelGateway parallel_gateway:a91287c4a5b93640b428add7e6ee993d>

>>> parallel_gateway.outgoing
[<ServiceActivity act_1:66f1c7adae6138199d888a37a7903201>,
 <ServiceActivity act_2:4540e66a52a2301da687e7be0e3f392c>,
 <ServiceActivity act_3:0129e1a5071e3440a8c144ae43a9476f>]
```

### converge

`converge()` 方法会将所有从调用者出发的连接汇聚到传入的节点上，并返回该节点，使用 `converge()` 能够快速的实现从网关发散出去的连接的汇聚操作：

```bash
>>> from pipeline.builder import ServiceActivity, ParallelGateway, ConvergeGateway
>>> parallel_gateway = ParallelGateway(name='parallel_gateway')
>>> act_1 = ServiceActivity(name='act_1')
>>> act_2 = ServiceActivity(name='act_2')
>>> act_3 = ServiceActivity(name='act_3')
>>> act_4 = ServiceActivity(name='act_4')
>>> converge_gateway = ConvergeGateway(name='converge_gateway')

>>> act_3.extend(act_4)
<ServiceActivity act_4:37714d8e173f3794b98620c93b500abd>

>>> parallel_gateway.connect(act_1, act_2, act_3)
<ParallelGateway parallel_gateway:4456b3b6448e3fb3a2671d849af58f60>

>>> parallel_gateway.converge(converge_gateway)
<ConvergeGateway converge_gateway:b71e936f133734d0a9deeb8b6e2bc4e9>

>>> for act in [act_1, act_2, act_4]:
        print(act.outgoing)
[<ConvergeGateway converge_gateway:b71e936f133734d0a9deeb8b6e2bc4e9>]
[<ConvergeGateway converge_gateway:b71e936f133734d0a9deeb8b6e2bc4e9>]
[<ConvergeGateway converge_gateway:b71e936f133734d0a9deeb8b6e2bc4e9>]
```

### to

`to()` 方法是一个辅助方法，其内部什么都不做，只会原封不动的返回传入的构造元素。使用 `to()` 方法能够让我们在链式调用的过程中改变方法的调用者：

```bash
>>> from pipeline.builder import ServiceActivity, ParallelGateway, ConvergeGateway
>>> parallel_gateway = ParallelGateway(name='parallel_gateway')
>>> act_1 = ServiceActivity(name='act_1')
>>> act_2 = ServiceActivity(name='act_2')
>>> act_3 = ServiceActivity(name='act_3')
>>> act_4 = ServiceActivity(name='act_4')

>>> parallel_gateway.connect(act_1, act_2) \
                    .to(act_1).extend(act_3) \
                    .to(act_2).extend(act_4)
<ServiceActivity act_4:ebdbf2c493b737d3bbb066a1a4df4088>

>>> parallel_gateway.outgoing
[<ServiceActivity act_1:becf135175543be190304063b57b69a3>,
 <ServiceActivity act_2:3f9e1cba9e703645b65a4d046a71c242>]

>>> act_1.outgoing
[<ServiceActivity act_3:fb8a9311c48334a38eab9703b4bd7f10>]

>>> act_2.outgoing
[<ServiceActivity act_4:ebdbf2c493b737d3bbb066a1a4df4088>]
```

## 生成流程描述结构

当完成了构造元素的连接后，我们就能够通过构造元素来生成描述结构了，使用 `build_tree()` 函数，传入开始事件节点，流程构造器就会返回由这些构造元素连接成的流程描述结构：

```bash
>>> from pipeline.builder import EmptyStartEvent, ServiceActivity, EmptyEndEvent, build_tree
>>> start = EmptyStartEvent(name='start')
>>> act_1 = ServiceActivity(name='act_1')
>>> act_2 = ServiceActivity(name='act_2')
>>> act_3 = ServiceActivity(name='act_3')
>>> end = EmptyEndEvent(name='end')

>>> start.extend(act_1).extend(act_2).extend(act_3).extend(end)
<EmptyEndEvent end:aaca723bebf332fc8d6588ae0c109f47>

>>> build_tree(start_elem=start)
{'activities': {'15b9a9ffcd7d3d289cb99886c4b66aa0': {'component': {'code': None,
    'inputs': {}},
   'error_ignorable': False,
   'id': '15b9a9ffcd7d3d289cb99886c4b66aa0',
   'incoming': ['df79daafd73c36f3965a2f8b36058aa5'],
   'name': 'act_1',
   'optional': False,
   'outgoing': 'd67e43325e3b389cba471562bd7e2a73',
   'type': 'ServiceActivity'},
  '7c3cfddb114c35ecbe18b88f5a519c58': {'component': {'code': None,
    'inputs': {}},
   'error_ignorable': False,
   'id': '7c3cfddb114c35ecbe18b88f5a519c58',
   'incoming': ['d67e43325e3b389cba471562bd7e2a73'],
   'name': 'act_2',
   'optional': False,
   'outgoing': 'abf3d80c6e363156bc4076c7dd0324c4',
   'type': 'ServiceActivity'},
  'ffe2edb847e335c5861d35c747d6d5f9': {'component': {'code': None,
    'inputs': {}},
   'error_ignorable': False,
   'id': 'ffe2edb847e335c5861d35c747d6d5f9',
   'incoming': ['abf3d80c6e363156bc4076c7dd0324c4'],
   'name': 'act_3',
   'optional': False,
   'outgoing': 'c12f7f231c353d3ab5762fe6a18f7efb',
   'type': 'ServiceActivity'}},
 'data': {'inputs': {}, 'outputs': {}},
 'end_event': {'id': '05c932bb9d8735729c6aaf1aba52ee53',
  'incoming': ['c12f7f231c353d3ab5762fe6a18f7efb'],
  'name': 'end',
  'outgoing': '',
  'type': 'EmptyEndEvent'},
 'flows': {'abf3d80c6e363156bc4076c7dd0324c4': {'id': 'abf3d80c6e363156bc4076c7dd0324c4',
   'is_default': False,
   'source': '7c3cfddb114c35ecbe18b88f5a519c58',
   'target': 'ffe2edb847e335c5861d35c747d6d5f9'},
  'c12f7f231c353d3ab5762fe6a18f7efb': {'id': 'c12f7f231c353d3ab5762fe6a18f7efb',
   'is_default': False,
   'source': 'ffe2edb847e335c5861d35c747d6d5f9',
   'target': '05c932bb9d8735729c6aaf1aba52ee53'},
  'd67e43325e3b389cba471562bd7e2a73': {'id': 'd67e43325e3b389cba471562bd7e2a73',
   'is_default': False,
   'source': '15b9a9ffcd7d3d289cb99886c4b66aa0',
   'target': '7c3cfddb114c35ecbe18b88f5a519c58'},
  'df79daafd73c36f3965a2f8b36058aa5': {'id': 'df79daafd73c36f3965a2f8b36058aa5',
   'is_default': False,
   'source': 'c582a8976e673ac39db8519a75f8baaa',
   'target': '15b9a9ffcd7d3d289cb99886c4b66aa0'}},
 'gateways': {},
 'id': '3149bd721e94377e8baee990e9fc4622',
 'start_event': {'id': 'c582a8976e673ac39db8519a75f8baaa',
  'incoming': '',
  'name': 'start',
  'outgoing': 'df79daafd73c36f3965a2f8b36058aa5',
  'type': 'EmptyStartEvent'}}
```
