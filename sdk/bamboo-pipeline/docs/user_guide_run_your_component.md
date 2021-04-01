<!-- TOC -->

- [执行你的组件](#执行你的组件)
  - [Component Runner](#component-runner)
  - [示例](#示例)

<!-- /TOC -->

## 执行你的组件

当我们编写好我们的组件后，我们可能需要运行起来看看执行的效果，但是如果为了执行一个组件而特定的编排流程来测试，未免过于麻烦。这时候可以使用框架提供的 component runner 来模拟组件的运行时，直接在命令行中执行组件。

### Component Runner

要在命令行执行组件很简单，秩序执行如下命令：

```shel
python manage.py run_component your_component_code
```

该命令的可选选项如下：

- `-d`：data 字段，会传递给插件 `execute` 方法的 `data` 参数，格式为 JSON 字符串
- `-p`：parent_data 字段，会传递给插件 `execute` 方法的 `parent_data` 参数，格式为 JSON 字符串
- `-c`：parent_data 字段，会传递给插件 `execute` 方法的 `parent_data` 参数，格式为 JSON 字符串

> 注意：component runner 不会进行任何的 mock 操作，插件中的代码会被真正执行，对第三方系统接口的调用也会生效。

组件中调用 `self.logger` 打印的日志会被输出到当前命令行会话中。

### 示例

下面展示了在命令行中执行 code 为 `schedule_node` 的组件，并且传递相应的参数的示范：

```shell
python manage.py run_component -d '{"k": "v"}' -p '{"1": "2"}' -c '{"3": "4"}' schedule_node
2019-11-06 06:46:48,946 - INFO - Start to run component [schedule_node] with data: <inputs: {'k': 'v'} | outputs: {}>, parent_data: <inputs: {'1': '2'} | outputs: {}>
2019-11-06 06:46:48,947 - INFO - Schedule 1 with data: <inputs: {'k': 'v'} | outputs: {'k': 'v'}>, parent_data: <inputs: {'1': '2'} | outputs: {}>
2019-11-06 06:46:48,947 - INFO - Schedule return [True], wait for next schedule in 2s
2019-11-06 06:46:50,951 - INFO - Schedule 2 with data: <inputs: {'k': 'v'} | outputs: {'k': 'v', 'count': 1}>, parent_data: <inputs: {'1': '2'} | outputs: {}>
2019-11-06 06:46:50,952 - INFO - Schedule return [True], wait for next schedule in 2s
2019-11-06 06:46:52,954 - INFO - Schedule 3 with data: <inputs: {'k': 'v'} | outputs: {'k': 'v', 'count': 2}>, parent_data: <inputs: {'1': '2'} | outputs: {}>
2019-11-06 06:46:52,955 - INFO - Schedule return [True], wait for next schedule in 2s
2019-11-06 06:46:54,956 - INFO - Schedule 4 with data: <inputs: {'k': 'v'} | outputs: {'k': 'v', 'count': 3}>, parent_data: <inputs: {'1': '2'} | outputs: {}>
2019-11-06 06:46:54,956 - INFO - Schedule return [True], wait for next schedule in 2s
2019-11-06 06:46:56,958 - INFO - Schedule 5 with data: <inputs: {'k': 'v'} | outputs: {'k': 'v', 'count': 4}>, parent_data: <inputs: {'1': '2'} | outputs: {}>
2019-11-06 06:46:56,959 - INFO - Schedule return [True], wait for next schedule in 2s
2019-11-06 06:46:58,959 - INFO - Schedule 6 with data: <inputs: {'k': 'v'} | outputs: {'k': 'v', 'count': 5}>, parent_data: <inputs: {'1': '2'} | outputs: {}>
2019-11-06 06:46:58,960 - INFO - Schedule return [True], wait for next schedule in 2s
2019-11-06 06:47:00,962 - INFO - Schedule finished
```