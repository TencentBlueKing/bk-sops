<!-- TOC -->

- [基本概念](#基本概念)
- [流程对象](#流程对象)
  - [pipeline](#pipeline)
- [流程元素](#流程元素)
  - [event](#event)
  - [activity](#activity)
  - [gateway](#gateway)
  - [subprocess](#subprocess)
  - [sequence flow](#sequence-flow)
- [数据交换](#数据交换)
  - [数据对象](#数据对象)
  - [数据上下文](#数据上下文)
  - [变量（Var）](#变量var)
  - [子流程参数传递（DataInput & Param）](#子流程参数传递datainput--param)
- [DSL](#dsl)

<!-- /TOC -->
## 基本概念

在进行进一步的了解和使用之前，让我们先来了解一下这个流程引擎中的一些基础概念。

## 流程对象

### pipeline

在 pipeline 流程引擎中，单个流程被称为 pipeline，每个流程在引擎内部都会拥有一个与其对应的 `Pipeline` 对象，该对象存储了一个流程中的所有信息（流程结构，流程数据），同时，这个对象也是引擎中的核心对象，这个对象会作为流程执行的依据，`Pipeline` 对象对于流程引擎来说就好像 Python 字节码对于 Python 虚拟机一样。

## 流程元素

下面这些对象被称**流程元素，流程元素指的是一个流程对象的基本组成元素。**

### event

一个 `Pipeline` 对象至少会拥有两个事件，一个开始事件（`StartEvent`）和结束事件（`EndEvent`），开始事件的完成标志一个 `Pipeline` 对象的执行开始，而结束事件的完成则标志一个 `Pipeline` 的执行完成。

### activity

一个 `Activity` 对象代表了某项活动，比如发起网络请求，操作数据库，执行命令等等，`Activity` 的行为通常由用户来定义。

### gateway

gateway 在 `Pipeline` 对象中起到了引流的作用，网关会决定一个任务流程的执行走向和行为，如分支网关（`ExclusiveGateway`）决定了接下来需要引擎需要执行的路径，并行网关（`ParallelGateway`）会增加当前 `Pipeline` 对象的执行进程数，条件并行网关（`ConditionalParallelGateway`）会根据当前上下文的信息来判断当前 `Pipeline` 对象的增加的执行进程数，而汇聚网关（`ConvergeGateway`）则会减少当前 `Pipeline` 对象的执行进程数。

### subprocess

子流程（`SubProcess`）是 `Pipeline` 对象中一种特殊的节点，当一个 `Pipeline` 对象作为另一个 `Pipeline` 对象的某个节点出现在其结构中，我们就把这个前者称为后者的子流程，通过使用子流程，开发者能够对 `Pipeline` 对象重用，减少重复编码。

### sequence flow

每个节点之间的连线，pipeline 将其称为顺序流。

## 数据交换

### 数据对象

流程对象中每个节点都拥有一个数据对象，这个数据对象用于存储节点的输入和输出数据，每个节点之间的数据对象是相互隔离的，也就是说，节点1不能直接访问节点2的输出。

### 数据上下文

在整个流程执行的过程中，节点之前并不是完全孤立的，某些时候节点需要进行通信，例如，节点2需要获取节点1的执行结果，并根据该结果来决定接下来的行为，由于在一个流程中每个节点之间的数据是相互隔离的，无法在节点内实现对其他节点数据的直接访问，所以，每个流程会拥有一个用于进行节点通信和数据传递的数据上下文。

节点1能够将自己在执行过程中生成的某些数据写到数据上下文中，当其他节点需要使用的时候，只需要从数据上下文中获取这些数据即可。

数据对象与数据上下文之间的数据交换如下图所示：

![数据上下文](https://raw.githubusercontent.com/homholueng/md_pic/master/pipeline_doc/data_context.png)

> 为什么不能在节点中直接访问其他节点与上下文的数据？在节点中直接访问其他节点与上下文中的数据固然方便，但是这样可能会导致在实现组件时过度依赖当前上下文的结构与流程结构，从而破坏了组件的独立性与可复用性。pipeline 中的每种活动节点都是独立的个体，即：无论在什么结构下的流程中、在流程中的什么位置都能够正确的执行。

### 变量（Var）

在定义流程时，通过变量（Var）能够声明数据上下文和节点数据对象中的数据，以及变量之间的引用关系，目前框架中提供了以下三种类型的变量：

- PLAIN：常量类型的变量，其值在声明后就不会发生变化，这种变量的声明十分简单：`{'type': 'plain', 'value': 'var value'}`
- SPLICE：拼接类型的变量，这种变量的值能够引用其他变量并且根据需求进行一定程度的拼接和 python 操作，SPLICE 类型变量的详细使用说明可以参考 [SPLICE 变量使用](./user_guide_splice_var.md) 章节
- LAZY：延迟获取值类型的变量，这种变量在进行解析前可以执行一段自定义的代码来获取特定的值，更加详细的说明可以参考 [LAZY 变量](./user_guide_lazy_variable.md) 章节

### 子流程参数传递（DataInput & Param）

如果我们要将一个流程作为子流程在别的流程里面执行，一般来说都需要向外暴露一些参数让使用者在执行的时候进行修改，一个流程通过 DataInput 来标记该流程作为子流程时向外暴露的参数，下面展示的配置中，`global_1` 能够作为参数向外暴露，而 `constant` 则不会向外暴露，这意味着当该流程被作为子流程使用时，父流程只能够修改其 `global_1` 参数。

```python
'data': {
  'inputs': {
      'global_1': {
          'type': 'splice',
          'is_param': True,
          'value': 'default value'
      },
      'constant': {
          'type': 'plain',
          'is_param': False,
          'value': 'constant value'
      }
  }
}
```

当流程标记了向外暴露的参数后，其他流程在将其作为子流程使用时，就能够通过 Param 来设置这些向外暴露的参数值，下面的配置展示了父流程通过 Param 来设置子流程暴露的参数值的操作：

```python
{
  'activities': {
      '2': {
          'type': 'SubProcess',
          'pipeline': {
              'data': {
                  'inputs': {
                      'global_1': {
                          'type': 'splice',
                          'is_param': True,
                          'value': 'default value'
                      },
                      'constant': {
                          'type': 'plain',
                          'is_param': False,
                          'value': 'constant value'
                      }
                  }
              }
          },
          'param': {
              'global_1': {
                  'type': 'splice',
                  'value': 'key'
              }
          }
      }
  }
}
```

## DSL

在 pipeline 流程引擎中，使用 JSON 作为一个流程结构的 DSL，这样的好处是足够的简单和通用，在 Quick Start 中我们通过流程构造器构造出了一个流程对象，流程构造器的职责就是使用 JSON 为我们生成一个流程的描述结构，然后引擎再根据这个描述结构来生成 `Pipeline` 对象。我们可以将 Quick Start 中构造的流程描述结构打印出来看一看：

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
