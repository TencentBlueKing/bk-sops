## 概述

标准插件在前端页面通过加载配置文件，渲染生成对应的表单组合项。配置文件可自定义表单类型、默认值、校验规则等属性，另外还可以给表单添加注册或监听事件函数属性，使表单项之间具有事件交互的能力。

## 如何使用

## Tag组件属性、方法

formMixins 函数定义了一些 Tag 组件公共的属性和方法，在添加 Tag 组件调用该方法来混入，可以避免编写重复的声明。

公共属性分为继承属性和非继承属性，继承属性在 Tag 组件里会被定义为 props 属性，目前只有 value 属性，非继承属性会被转换为 data 属性，它的值不会动态更新。属性的值，优先取标准插件配置文件里定义的值，若配置项没有对应属性的默认值。

Tag 组件的私有属性在添加组件时定义，属性的取值和公共属性一致，优先取标准插件配置文件里的值，若配置项没有对应属性则取默认值。

**配置文件里定义的表单项属性，只有在 Tag 组件里声明过，才能够被组件正确的拿到。**

### 公共属性列表

- `tagCode`，每个表单项的 id，每个标准插件配置文件里需唯一
- `name`，表单项名称，在页面上控制 label 的显示
- `hookable`，是否可勾选为全局变量
- `validation`，表单项的校验规则
- `default`，表单项的默认值
- `hidden`，是否隐藏
- `formEdit`，是否可编辑
- `formMode`，是否为表单模式
- `parentValue`，父组件的值
- `value`，表单组件的值，需要在 Tag 里手动定义，并作为调用 `getFormMixins` 函数的参数传入



### 公共方法列表

- `updateForm`，触发`change`事件更新表单值，并调用校验函数，参数为 `value`
- `validate`，校验函数
- `show`，表单隐藏
- `hide`，表单显示
- `get_form_instance`，获取表单实例，FormItem
- `get_parent`，获取 combine 实例或根元素实例
- `_get_value`，获取表单值
- `_set_value`，设置表单值


### 当前Tag组件支持的私有属性(value 除外)

|组件|属性|
|--------|--------|
|tagCheckbox|items|
|tagDatatable|columns、editable、value、add_btn、empty_text、remote_url、remote_data_init|
|tagDatetime|placeholder|
|tagInput|placeholder|
|tagInt|placeholder|
|TagPassword|--|
|TagRadio|items|
|TagSelect|items、multiple、multiple_limit、remote、remote_url、remote_data_init、placeholder、empty_text|
|tagText|--|
|TagTree|placeholder|
|tagCheckbox|items、expanded_keys、show_checkbox、default_expand_all、remote、remote_url、remote_data_init|
|TagTree|url、multiple、headers、auto_upload、limit、placeholder、text|


## 如何添加Tag组件

## 标准插件渲染逻辑

标准插件表单项的渲染由 RenderForm 组件分发，RenderForm 基于 Vue 封装，利用了数据双向绑定的提供的便利，实现了表单项取值与根组件的自定义 v-model，调用组件时只需传入对应的配置项 props，就可以实现父组件与 RenderForm 内部组件的数据自动同步。

配置文件里每一个表单项配置在前端组件渲染底层对应一个 FormItem 组件，一般情况下(非勾选状态) FormItem 组件下都包含一个 Tag* 子组件， Tag 的类型由配置项的 type 字段定义，目前支持的类型包括: input、textarea、checkbox、radio、select、table、upload、tree、password等，所有 Tag 组件都定义了一些公共的属性或者方法，若某种 Tag 类型需要支持的特定事件或者功能，则在对应的 Tag 子组件里定义。另外对于较复杂的使用场景，也可根据需求自定义扩展 Tag 类型。

RenderForm 组件的结构：

![图片描述](../resource/img/renderform_arch.png)


标准插件表单的渲染流程：


![图片描述](../resource/img/renderform_flow.png)

## 添加Tag组件步骤

添加 Tag 组件只需要在前端项目的`src/components/tags/`目录里增加一个单文件的 vue 组件，文件名称格式为`Tagxxx`，`xxx`为 Tag 组件的名称，命名遵循驼峰规则且保证在项目所有`Tag`里是唯一的。webpack 在打包是会查找该目录下的文件，自动引入并注册到 `FormItem` 组件里。模版最外层元素建议增加一个 `tag-xxx`的 `class` 名称，`xxx` 表示 Tag 的名称。

组件的编写需要注意一下几点：

- 是否展示模式、是否为编辑态
  
  RenderForm 组件为通用组件，标准运维所有页面的标准插件表单渲染都通过使用该组件来实现，页面不同地方可能会区分编辑态、禁用态，表单模式、查看模式，所以在编写组件模版是需要针对不同的场景写不同的模版，编辑、禁用通过`formEdit`属性区分、是否表单模式通过`formMode`属性区分。

- 定义私有属性，混入公共属性、方法

  编写组件时必须引入公共属性和方法，并且定义好私有属性后调用公共 mixins 函数的参数传入，其中私有属性必须包含 value 属性，属性申明遵循 props 校验规则格式。mixins 函数由前端项目目录`src/components/common/RenderForm/formMixins.js`文件定义。 

- 表单值绑定

  Tag 组件的值必须实现双向绑定，创建一个计算属性来处理绑定逻辑，计算属性的 `get` 由 props 里的 `value` 的值(需要注意引用类型值的深拷贝)，`set`需要调用`updateForm`方法传入修改后的value到组件，触发change事件和校验逻辑。
