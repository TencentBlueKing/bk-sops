# _system 变量渲染失败问题分析

## 问题描述
第一个 pipeline_tree 在渲染 `_system.executor` 和 `_system.bk_biz_id` 时失败，但第二个能正常渲染。

## 关键差异

### 第一个 pipeline_tree
- 有 `${loop}` 常量，source_info 指向节点 `nbb5f3f2d6433bd4b3a45a3f966499d7` 的 `_loop` 输出
- Gateway 条件中使用 `${int(loop)} < ${int(data_len)}`
- `execute_kwargs.value` 是一个嵌套字典，包含 `${_system.bk_biz_id}` 和 `${_system.executor}`

### 第二个 pipeline_tree
- **没有** `${loop}` 常量
- Gateway 条件中也使用 `${int(loop)} < ${int(data_len)}`（但没有定义 `${loop}`）
- `execute_kwargs.value` 同样是一个嵌套字典，包含 `${_system.bk_biz_id}` 和 `${_system.executor}`

## 渲染流程分析

### 关键代码路径
1. `get_node_data_v2` (node.py:552-592)
   - 创建 `SystemObject` 并添加到 `root_pipeline_context`
   - 调用 `preview_node_inputs` 进行渲染

2. `preview_node_inputs` (constants.py:103-179)
   - 对于非 subprocess_plugin 节点，使用优化路径
   - 调用 `get_need_render_context_keys()` 获取需要渲染的上下文键
   - 只包含在 `need_render_context_keys` 中的变量会被添加到 `context_values`

3. `get_need_render_context_keys` (constants.py:112-119)
   - 使用 `get_references()` 检测变量引用
   - `get_references()` 使用 `ConstantPool` 来检测引用

4. `get_references` (constants.py:78-100)
   - 使用 `ConstantPool(inputs, lazy=True).get_reference_info(strict=False)`
   - **问题可能在这里**：`ConstantPool` 可能无法正确检测嵌套字典中的 `${_system.bk_biz_id}` 引用

## 可能的原因

### 假设 1: ConstantPool 无法递归检测嵌套字典中的变量引用
当 `execute_kwargs.value` 是一个字典时：
```python
{
    "caller_bk_biz_id": "${_system.bk_biz_id}",
    "caller_executor": "${_system.executor}"
}
```
`ConstantPool` 可能只检测顶层字符串，无法递归检测字典值中的变量引用。

### 假设 2: 第一个 pipeline_tree 中的 `${loop}` 常量影响了引用检测
第一个 pipeline_tree 有 `${loop}` 常量，可能在 `get_references` 的循环检测过程中，由于 `${loop}` 的引用链导致 `${_system}` 没有被正确识别。

### 假设 3: format_web_data_to_pipeline 处理差异
在 `format_web_data_to_pipeline` 中，`component.data` 被转换为 `component.inputs`。如果第一个 pipeline_tree 中的某些配置导致 `execute_kwargs` 没有被正确转换，可能导致渲染失败。

## 建议的解决方案

1. **确保 `get_references` 能递归检测嵌套字典中的变量引用**
   - 修改 `get_references` 函数，递归处理字典和列表中的值
   - 或者修改 `ConstantPool` 使其支持递归检测

2. **确保 `${_system}` 始终被包含在渲染上下文中**
   - 在 `preview_node_inputs` 中，无论 `get_references` 的结果如何，都确保 `${_system}` 被添加到 `context_values`

3. **检查 `format_web_data_to_pipeline` 对嵌套字典的处理**
   - 确保 `execute_kwargs.value` 这样的嵌套字典结构被正确转换为 `component.inputs`

## 验证方法

1. 检查第一个 pipeline_tree 在执行时，`get_references` 返回的引用集合是否包含 `${_system}`
2. 检查 `hydrated_context` 中是否包含 `_system` 对象
3. 检查 `Template.render()` 是否能访问 `_system.bk_biz_id` 和 `_system.executor`
