# 标准运维单元测试编写指南

## 前言：

当你看这篇指南的时候，意味着你已经准备好开始编写标准运维单元测试框架了，标准运维插件单元测试的编写尽管和我们通常的单元测试框架略有不同，但是也同样理解和上手，接下来我们将以一个简单的插件入手，编写一个标准的标准运维单元测试样例。

## 前期准备：

首先，在你看这部分内容之前，请确保你已经编写并调试好了一个插件，这样你就可以跟着这份指南开始一步一步的编写一个属于你自己可用的单元测试，这样的话效果会好很多。

首先，我们需要在项目`pipeline_plugins\tests\components\collections\sites`下对应的目录，这通常和你的插件保持一致，新建一个 `test_{your_plugin_code} `格式的文件，例如你的插件code为 `my_plugin`, 那么你的文件名应该为`test_my_plugin` 这不是约定俗成的，但是你应该这样做。

## 快速上手

之后我们需要定义一个我们自己的单元测试类,假设你现在已经编写好了一个插件，名字叫`Demo`

```python
import json

from django.test import TestCase

from pipeline.component_framework.test import (
    ComponentTestMixin, ComponentTestCase, ExecuteAssertion, ScheduleAssertion, Patcher, MultiPatcher,
    ModulePatcher,
)
from pipeline_plugins.components.collections.sites.ieod.demo.test import DemoComponent


class DemoComponentTest(TestCase, ComponentTestMixin):
    def cases(self):
        return [
            EXECUTE_SUCCESS,
        ]

    def component_cls(self):
        return DemoComponent
```

同样的，类名也是约定俗成的，类似于`DemoComponentTest`， 想必你也已经发现了其中的规律。

### 标准的插件单元测试样例

之后，我们需要编写`EXECUTE_SUCCESS` 中的内容，在知道`EXECUTE_SUCCESS`是什么之前，我们还有一件重要的事情要做 - **列出我们需要Mock的方法，并准备好返回值。**

类似于这样：

```python
# mock path
ADD_TASK = "pipeline_plugins.components.utils.add_task"

ADD_TASK_SUCCESS = {
    "code": 0,
    "result": True,
    "data": [],
    "message": "已成功创建任务",
}
```

在这里，我们`mock`掉了`add_task`方法，同时并定义了一个`ADD_TASK_SUCCESS`，用来表示我们任务添加成功的返回结果。

当然，也许现在它们还未派上用场，但是马上就可以。

接下来，我们需要定义一个我们的测试样例，它规定了我们插件的输入输出等信息，大概长这个样子：

```python
COMBINE_ZONE_SUCCESS = ComponentTestCase(
    name="add task success",
    inputs={
        "param1": "",
        "param2": "",
    },
    parent_data={"executor": "admin", "biz_cc_id": "123"},
    execute_assertion=ExecuteAssertion(success=True, outputs={'task_id': '111'}),
    schedule_assertion=ScheduleAssertion(
        success=True, schedule_finished=True, outputs={},
    ),
    # add patch
    patchers=[
        Patcher(target=ADD_TASK, return_value=ADD_TASK_SUCCESS)
    ],
)
```

非常短小精悍，现在让我们来逐一拆解各个参数的作用：

- `name`: 我们测试样例的名称，可以更快的帮助我们定位到某个测试`ComponentTestCase`实例, 就像这样：

  ```bash
  [√] <MidasCombineZoneComponent> - [add task success]
  ```

- `inputs`: 插件的输入参数，对应插件`execute(self, data, parent_data)` 中的 `data` 参数。

- `parent_data`: 插件的输入参数，对应插件`execute(self, data, parent_data)` 中的 `parent_data` 参数。

- `execute_assertion`:  插件 `execute`函数的断言，其中`success=True` 表示 `execute`方法最终返回结果是True，同样的`success=False` `execute`方法最终返回结果是False 。`outputs` 表示在执行过程中插件所产生的值，对应的语句为：

  ```python
  data.set_outputs("task_id", "111")
  ```

- `schedule_assertion`: 和`execute_assertion`同理，不过针对的方法为`schedule`
- `patchers`: `patchers`定义了一组 Patcher，他帮助我们`mock`掉了一些外置的`api`，通常写单元测试的时候我们需要这样做，并且定义了相应的返回值。

以上就是一个非常简单的标准运维单元测试样例，它已经可以帮助你胜任百分之90的标准运维单元测试场景了，如果你的插件并不复杂，那么通常这意味着已经足够用了，你剩下的工作也仅仅是编写更多的情况。

类似于这样：

```python
class DemoComponentTest(TestCase, ComponentTestMixin):
    def cases(self):
        return [
            EXECUTE_SUCCESS, # 成功
            EXECUTE_FAILED # 失败
        ]

    def component_cls(self):
        return DemoComponent
```

如果是失败情况，记得修改相关的`success=Fasle`哦。

##  再进一步：

如果你曾经看过标准运维其他插件的单元测试，你就会发现标准运维单元测试远不止如此，当遇到一些更加复杂的情况的时候，你可能需要这样做：

### 如何根据不同的参数返回不同的返回值？

设想这样的场景，在多线程中，你重复调用了同样一个函数，但是它的入参并不一样，这个时候如果单纯的指定 `return_value`, 就会导致函数每一次的返回值都是相同的，这并不是我们需要的结果，这个时候`return_value`已经不能满足我们的要求了，我们需要使用`side_effect`

就像这样：

```python
 def add_task(params):
    if params:
        return ADD_TASK_SUCCESS
    else:
        return ""

    # add patch
    patchers=[
        Patcher(target=ADD_TASK, side_effect=add_task)
    ],
```

这样就可以达到根据不同的参数返回不同的结果这样的效果了。

### 如何让函数每次调用返回结果不一样？

当我们的应用涉及到某些循环调用时。类似于某些批量操作时：

```python
for p in params:
	result = add_task(p)
```

单纯的`return_value`同样也是无法满足我们的需求的，`side_effect`倒是可以，但是会增加非常多的`if else`并不推荐， 这个时候如果我们给 `side_effect`传入一个迭代器，而非函数的话，有趣的事情发生了。

```python
    patchers=[
        Patcher(target=ADD_TASK, side_effect=[1,2,3,4,5])
    ],
```

之后你每次调用的结果都将从迭代器的第一项开始，依次往后。

### 如何给指定的方法填入指定参数

```python
execute_call_assertion=[
    CallAssertion(
        func=CC_GET_IPS_INFO_BY_STR,
        calls=[Call(username='executor',
                    biz_cc_id=1,
                    ip_str='127.0.0.1',
                    use_cache=False)]),
]
```

这样就可以测试指定的函数了。
