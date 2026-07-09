# 标准运维内置插件开发最佳实践

### 🎧   前言:

本篇文章的作用是，帮助那些已经在开发插件，或者摩拳擦掌准备开发插件的人一个简单的指引，标准运维的插件是什么，怎么编写一个插件，在插件的开发过程中，哪些操作是不建议做的🙅‍♂️，哪些是建议做的 🙆 。以及插件版本的概念，如何编写插件的单元测试等等。

### 标准插件是什么❓

**标准运维插件是标准运维的核心功能，是标准运维能满足运维同学多种多样的运维场景的根本**，我们可以把画布比作是做饭的工具，比如刀锅和铲子，把插件必做是原材料，只有原材料的样式足够多，才能通过各种排练组合做出各种各样美味的饭菜来，不然就妥妥的:**床底下练武-施展不开了** 。

### 标准运维插件组成结构

**每一个插件是一个独立的原子**, 类似于流水线不同阶段的工人，负责接收一组输入，经过处理后产生一个输出，这个输出允许作为下一个插件的输入，以此类推。

一个完整插件主要由以下这几部分组成:

- 表单: 表单定义了插件的输入，表单支持多种控件，下拉框，文件上传，表格，输入框，单选多选框等，以此来满足对于插件等输入的各种复杂的使用场景。
  
  表单的定义可以查看相关的文档:
  
  传送门🚪  > [Tag 使用和开发说明](https://github.com/TencentBlueKing/bk-sops/blob/master/docs/develop/tag_usage_dev.md)

- 插件的定义(Component):  Component 定义了插件的名称，form路径，执行逻辑对应的Service, code 以及版本信息。

- 插件的执行逻辑(Service) :  Service 定义了插件的输入输出描述，以及对应的执行逻辑函数，其中execute函数用于处理执行逻辑， schedule用于执行轮询逻辑，当不需要轮询时，可以设置`__need_schedule__`  关闭。

- 插件的测试

### 插件的代码结构

插件的完整开发教程请移步:

传送门🚪 > [标准插件开发](https://github.com/TencentBlueKing/bk-sops/blob/master/docs/develop/dev_plugins.md#%E6%A0%87%E5%87%86%E6%8F%92%E4%BB%B6%E5%BC%80%E5%8F%91)

正常情况下，一个插件的的代码结构如下:

```python
# -*- coding: utf-8 -*-

import logging
from pipeline.core.flow.activity import Service
from gcloud.conf import settings
logger = logging.getLogger('celery')

__group_name__ = _("配置平台(CMDB)")

class DemoService(Service):

     __need_schedule__ = True

    def inputs_format(self):
        return []

    def outputs_format(self):
        return []

    def execute(self, data, parent_data):
        return True

    def schedule(self, data, parent_data, callback_data=None):
        return True

    
class DemoComponent(Component):
    name = _("创建集群")
    code = 'plugin_code'
    version = "1.0.0" # 默认不填为legacy
    bound_service = DemoService
    form = '%scomponents/atoms/demo/plugin_code/legacy.js' % settings.STATIC_URL
    desc = "这是这个插件的默认描述"
```

接下来我们来看看Service的各个方法的作用都是什么:

**inputs_format**

- 返回输入参数的列表，该方法是对输入参数的说明，对插件的执行没有任何影响，返回空也没有关系，但是一般建议你写上作为参数的一个输入说明，方便其他的人去理解你的插件的输入。
  
  ```python
  def inputs_format(self):
          return [self.InputItem(name=_('业务 ID'),
                                 key='biz_cc_id',
                                 type='string',
                                 schema=StringItemSchema(description=_('当前操作所属的 CMDB 业务 ID')))]
  ```

**outputs_format**

- 返回输出参数的列表， 列表格式的每一项定义一个返回字段，是 `execute` 函数中的 `set_outputs` 输出的字段的子集；`key` 表示输出字段标识，`name` 表示输出 字段含义，`type` 表示输出字段类型（`str`、`int` 等 `python` 数据结构）。
  
  输出列表不会影响到插件的执行，但是会影响到插件在前端的运行结果的展示。

**execute**

- 可以是任何 python 代码，如果需要调用蓝鲸API网关接口，一般分为参数组装、API 调用、结果解析。
- data 是标准插件输入输出参数数据对象，输入参数对应于前端的表单，可以用 `data.inputs.xxx` 或者 `data.get_one_of_inputs('xxx')` 获取 某一个参数；执行完成可以使用 `data.set_outputs` 写入输出参数，异常信息请赋值给 `ex_data`。
- `parent_data` 是任务的公共参数，包括 executor（执行者），operator（操作员），biz_cc_id（所属业务 ID）等。详细信息请查看 `gcloud/taskflow3/utils.py`。
- 返回 `False` 表示执行失败，同步标准插件返回 `True` 表示标准插件执行成功，异步标准插件返回 `True` 会进入休眠，等待第一次异步轮询或者外部 回调，执行 `schedule` 函数。

**schedule 函数详解：**

-  `pipeline.core.flow.activity.StaticIntervalGenerator`（每隔 多少秒轮询一次）、`SquareIntervalGenerator`（每次轮询间隔时间是当前已调度次数的平方）。
- 使用 `self.finish_schedule` 结束轮询，返回 `True` 表示标准插件执行成功，`False` 表示执行失败。如果不执行`self.finish_schedule`又返回True, 则表示继续轮询。

### 场景解析:

说了那么多，可是我还是不会怎么开发插件。没关系，接下来我们将会选两种较为典型的场景分别对应的插件。看看下次你遇到类似场景的时候应该怎么学着写。

#### 第一种场景:

插件只会一次性的调用, 比如咱就拿`配置平台(CMDB)-更新主机属性`  这个插件举例子，修改个主机属性，调个接口，啪的一下就完事儿了，只需要一次，需要轮询吗，不需要。

所以这类的插件就只有一个`execute`而没有`schedule`。 因为在这种单次调用的场景下不需要。

#### 第二种场景:

这个插件要执行的逻辑是异步的，典型代表有job系列插件，比如执行脚本，执行作业。为什么这么说，因为`execute`只会执行一次，也就是说我们最多能做到在`execute`函数里面调用`job`接口创建一个任务，但是问题来了，job的任务执行是需要时间的，短的需要十几秒，大的需要数分钟，数十分钟都有可能。

这个时候有大聪明举手了，我有办法,  我只需要在**execute**里面 **sleep** 个几分钟, 那不就完事了，哈哈哈哈。

**万万不可**。

我们知道，pipeline底层是由celery驱动的，我们的execute最终其实是落在celery的一个进程or线程中执行的，取决于你使用的是进程池还是线程池，比如原来有5个进程在日夜不停的跑，来一个任务几毫秒或者一两秒内跑完了, **当我同时启动很多任务时，因为每个任务执行的都很快，所以新来的任务不用怎么等也可以分配到进程去执行。但是如果我加了一个sleep事件，让每个进程睡十分钟，假设有5个进程，我同时启动五个任务时，五个任务都正常跑起来了，但是当我执行第六个任务时，问题出现了，任务来了，但是所有的进程都在呼呼大睡，根本没有进程去执行这个任务。于是我第六个任务只能等到十分钟后才能得到执行.** 如果任务一多，就会造成任务阻塞。

正确的做法应该是 开启

```python
__need_schedule__ = True
```

然后在`schedule`中编写我们相关的轮询逻辑，执行的时间长，每次轮询的时间短一点，多轮询几次就好了。

## 一些最佳实践：

#### ⚠️ 不要在 execute 和 schedule 中增加执行时间较长的逻辑

一定不要在 `execute` 和 `schedule` 编写执行时间过长的逻辑，比如`time.sleep`或者其他类似的代码，**这样可能会造成任务阻塞。具体的表现是新的任务可能会阻塞住而不执行。**

#### ✈️   尽量编写足够多的异常处理，提高插件的稳定性

翻开大多数的标准运维插件，我们会发现大多数插件都不是直接执行那么简单，比如`更新主机属性` 这个插件。可以看到很多的这样的逻辑:

```python
        if ip_list["invalid_ip"]:
            data.outputs.ex_data = _("无法从配置平台(CMDB)查询到对应 IP，请确认输入的 IP 是否合法")
            data.outputs.invalid_ip = ",".join(ip_list["invalid_ip"])
            return False
```

提前校验好参数信息才会保证我们的插件成功率。

#### ✈️   当插件带来不兼容的改动时，起一个新版本更合理。

有时候我们需要对某个插件进行升级操作，例如为表单添加新的字段，为后台逻辑添加新的功能，那么这个时候就需要修改现有插件的逻辑；但是用户存量流程和任务使用到了这个插件，直接修改插件的代码可能会导致存量流程和任务不可用，所以正确的做法应该是为这个插件增加一个新的版本。

通过设置 Component 的 `version` 类属性，我们能够将 `code` 相同的插件设置成不同版本，以保证插件的功能升级不会影响用户的正常使用，用户只需要在合适的时候将旧的插件升级到新版本即可。

如果插件需要说明不同版本之间的差异，可以在插件Component的desc中说明。

**重要：对于没有声明 `version` 参数的插件，请不要擅自为其添加 `version` 字段，否则系统会将其视为新的插件，可能会导致现有模板和任务不可用。**

> version 字段的命名需要遵循规范，比如   `1.0.0`  

#### ✈️   当存在多个逻辑相似的插件版本时，将代码公共逻辑抽离出来更合适。

参考CC的一些插件, 发现继承了公共的**Service** ``BaseTransferHostToModuleService

```python
logger = logging.getLogger("celery")
__group_name__ = _("配置平台(CMDB)")


class CmdbTransferHostResourceModuleService(BaseTransferHostToModuleService):
    def execute(self, data, parent_data):
        return self.exec_transfer_host_module(data, parent_data, "transfer_host_to_resourcemodule")


class CmdbTransferHostResourceModuleComponent(Component):
    name = _("上交主机至资源池")
    code = "cmdb_transfer_host_resource"
    bound_service = CmdbTransferHostResourceModuleService
    form = "%scomponents/atoms/cc/cmdb_transfer_host_resource.js" % settings.STATIC_URL
```

在抽离的过程中，记得兼容之前的老插件。

#### ✈️   为插件编写单元测试

通过插件的单元测试，我们可以知道我们每对公共组件的改动是否有影响到其他版本的插件，从而提升我们插件的健壮性。

#### ✈️  合理使用并发

当插件中出现多次调用时，可以适当的使用并发来提高插件的效率。参考案例：`job分发文件` 等插件，相关代码可以搜索:

路径： [查看相关代码](https://github.com/TencentBlueKing/bk-sops/blob/master/pipeline_plugins/components/collections/sites/open/job/all_biz_fast_push_file/v1_0.py)

```python
job_result_list = batch_execute_func(client.jobv3.fast_transfer_file, params_list, interval_enabled=True)
```


