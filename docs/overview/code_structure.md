# 代码目录

![](../resource/img/code_structure.png)

代码主要可以分为蓝鲸开发框架层 framework、流程引擎服务层 pipeline、标准运维业务层 gcloud 以及前端展示层 web。

- framework

  蓝鲸基于 django 框架的二次封装架构，主要提供 saas 运营在蓝鲸 paas 上的基础配置和服务。

  conf：工程各部署环境配置，如本地环境、测试环境、正式环境。

  common：主要是一些公共函数。

  blueapps：也是一些公共函数，单独作为一个模块主要是为了向后兼容新版开发框架。

  bk_api：蓝鲸 paas 提供的 API。

  blueking：蓝鲸 API Gateway SDK，包括配置平台、作业平台等提供的API。

  account：蓝鲸统一登录和鉴权。

- pipeline

  自研的流程引擎框架，主要包含任务流程编排页面和任务流程执行服务。

  conf：默认配置。

  core：参考 BPMN2.0 规范，定义了一些核心元素如 Activity、网关、事件和数据对象 Data，以及 pipeline 的整体结构。

  models：存储结构定义和相关的方法。

  engine：runtime 执行逻辑和任务状态管理。

  log：日志持久化存储和管理。

  parser：前端数据结构解析。

  validators：数据校验，如环状结构检测和数据合法性校验。

  components：原子框架和原子定义。

  variables：全局变量定义。

  contrib：扩展功能，如数据统计和前端 API。

- gcloud

  基于流程引擎框架封装的业务适配层，包含业务权限控制、流程模板管理、任务管理、业务配置、API 等功能。

  conf：配置动态适配层。

  core：业务核心逻辑，权限控制，业务首页。

  utils：公共函数和模块。

  tasktmpl3：流程模板管理。

  taskflow3：任务管理。

  webservice3：数据资源 API 管理。

  config：业务配置。

  apigw：对外 API 模块。

- web

  前端资源，包括 webpack 配置和静态资源。

  pipeline.blueflow：主要包括流程编排 pipeline/blueflow 模块，该模块是基于 vue 实现的。

  static：原子 components 和变量 variables 的前端定义文件，都放在各自模块的 static 目录下。

  templates：包含首页和 django admin 需要的页面。

  locale：国际化翻译文件。
