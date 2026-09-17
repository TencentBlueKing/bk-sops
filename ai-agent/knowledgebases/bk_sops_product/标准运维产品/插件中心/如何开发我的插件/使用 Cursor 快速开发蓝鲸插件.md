> 插件开发分3步：`准备插件开发环境` -> `编写需求文档` -> `让 Cursor 开发`

## 前言

智能IDE是助手，`用好`智能助手看起来是`顺应`智能时代要学会的新技能。

本文以 智能IDE `Cursor` （公司有 `CodeBuddy`） `开发蓝鲸插件`( 将需求/Bug移入指定TAPD迭代) 为例，来介绍与智能工具协同工作的方法。

<video controls src="插件开发.mov" title="Title"></video>

> 开发某一个插件时录制的视频

## 前置项

### 安装 Cursor

 下载并安装 [Cursor](https://www.cursor.com/cn) 客户端。

### 准备本地开发环境

该章节具体详见 [https://iwiki.woa.com/p/4013100445](https://iwiki.woa.com/p/4013100445)。

- [创建插件](https://v3.open.woa.com/plugin-center)
- 拉取代码到本地
- 打开 Cursor，选择代码目录
- 在 Cursor 中创建虚拟环境  
  Python版本选择 `Python3.10`
- 安装依赖包

```bash
pip install pip==24.0
pip install -r requirements.txt -i https://mirrors.tencent.com/tencent_pypi/simple/
```

- 设置环境变量

```bash
export BKPAAS_APP_ID="xxx" ## 在开发者中心的插件控制台可以找到
export BKPAAS_APP_SECRET="xxx" ## 同上
export BK_APP_CONFIG_PATH="bk_plugin_runtime.config"
export BKPAAS_ENGINE_REGION="ieod"
export BKPAAS_LOGIN_URL="http://login.o.oa.com"
export BK_PLUGIN_RUNTIME_BROKER_URL="amqp://guest:guest@localhost:5672//"

export TAPD_IDC_API_IP="9.146.161.37" ## 可选，插件所在的IDC环境可访问 TAPD API
export TAPD_IDC_HOSTNAME="apiv2.tapd.oa.com" ## 可选，同上
```

- migration

```bash
python bin/manage.py migrate
```

- 运行插件本地环境

```bash
python bin/manage.py rundebugserver 127.0.0.1:8044
```

### 定义开发规范

输入命令 `/Generate Cursor Rules` ，内容如下

遵循Python代码规范，并包含以下规则

- 单行不超过120个字符
- 丰富的代码注释，以便对 Python 新手友好
- 使用 loggin.info 打印插件执行的关键日志，请勿打印 Token 等敏感信息
- 本条 Rule Type 设置为 `Always`

![alt text](image-20.png)

 

>  如果没有自动设置  Rule Type，在左侧手动设置。

## 1. 编写需求文档

 重点在定义需求，和 Cursor 交互的推荐方式是`写需求文档`，减少`多轮对话`。

首先我们需要梳理实现 `将需求/Bug移入指定TAPD迭代` 该需求，我们需要调用 TAPD的  [更新需求 API](https://o.tapd.woa.com/document/api-doc/API%E6%96%87%E6%A1%A3/api_reference/story/update_story.html)   和 [更新迭代 API](https://o.tapd.woa.com/document/api-doc/API%E6%96%87%E6%A1%A3/api_reference/bug/update_bug.html)，将指定需求或Bug的`迭代ID`设置为目标迭代ID。

基于上述 TAPD API 文档，整理`需求文档`如下，保存在`.cursor/rules` 目录下，文件名为 `storySpec.mdc` 。

```markdown
## 将需求/Bug移入指定TAPD迭代 蓝鲸标准插件 需求说明
将需求或迭代移动到指定迭代。

## 插件架构
- 插件框架详见 @https://context7.com/tencentblueking/bk-plugin-framework-python
- form.js 定义插件输入的表单
- bk_plugin/versions/v1_0_0.py 定义插件的执行入口
- 具体的执行函数在单独的文件中定义

## 1. 实现逻辑
通过调用 TAPD 的 `更新需求` 和 `更新Bug` API ，将需求或Bug的 `迭代` (iteration_id) 设置为预期的迭代ID。

>  $TAPD_IDC_API_IP（API地址中的HOST部分）、$TAPD_IDC_HOSTNAME（设置请求的主机头 HOST） 从操作系统环境变量中获取。

鉴权方式：Basic Auth 鉴权

### 1.1 更新需求 API
POST http://$TAPD_IDC_API_IP/stories

#### 输入参数
字段名	必选	类型及范围	说明
id	是	integer	ID
workspace_id	是	integer	项目ID
iteration_id	否	string	迭代ID

#### 输出参数

```json
{
    "status": 1,
    "data": {
        "Story": {
            "id": "1010158231500625827",
            "workspace_id": "10158231",
            "status": "planning",
            "iteration_id": "0"
        }
    },
    "info": "success"
}
```

### 1.2 更新Bug API
POST http://$TAPD_IDC_API_IP/bugs

#### 输入参数
字段名	必选	类型及范围	说明
id	是	integer	ID
workspace_id	是	integer	项目ID
iteration_id	否	string	迭代ID

#### 输出参数

```json
{
    "status": 1,
    "data": {
        "Bug": {
            "id": "1010158231500628817",
            "title": "【示例】新官网Chrome浏览器兼容性bug",
            "iteration_id": "0",
            "workspace_id": "10158231"
        }
    },
    "info": "success"
}
```

## 2. 插件输入参数
- TAPD应用ID: tapd_app_id，输入框（以密码模式显示 "showPassword": true）
- TAPD应用密钥: tapd_token，输入框（以密码模式显示 "showPassword": true）
- TAPD项目ID: tapd_project_id，输入框，正则校验规则为数字
- 迭代ID: iteration_id
- 需求列表: tapd_story_list
    - 列表，示例 ["12222", "22322"]
    - 多个以换行分割
- 缺陷列表: tapd_bug_list
    - 列表，示例 ["12222", "22322"]
    - 多个以换行分割

## 3. 插件输出变量	
- tapd_move_iteration_result

数据示例

```json
{
  "tapd_story_move_iteration_succ": 12,
  "tapd_bug_move_iteration_succ": 12,
  "tapd_story_move_iteration_total": 12,
  "tapd_bug_move_iteration_total": 12,
  "tapd_story_move_iteration_succ_list": [],
  "tapd_bug_move_iteration_succ_list": [], 
  "tapd_story_move_iteration_fail_list": [],
  "tapd_bug_move_iteration_fail_list": []
}
```
				
## 4. 插件运行结果              
满足以下任一条件，插件返回失败
- tapd_story_move_iteration_suc !=  tapd_story_move_iteration_total  
- tapd_bug_move_iteration_total != tapd_bug_move_iteration_succ   
```


![alt text](image-21.png)

 


## 2. 开发

```
@storySpec.mdc 请根据需求文档完成插件开发
```

![alt text](image-22.png)

 

![alt text](image-23.png)

 

![alt text](image-24.png)

 

![alt text](image-25.png)

 

![alt text](image-26.png)

 


## 3. 调试

打开 本地开发环境 127.0.0.1:8044 调试插件

```shell
python bin/manage.py rundebugserver 127.0.0.1:8044
```

> 如果之前打开过，需要重新启动，因为插件表单需要重新渲染。

![alt text](image-27.png)

 

![alt text](image-28.png)

 


## 4. 编写README

编写插件 `README.md`

![alt text](image-29.png)

 


详见 [工蜂Git代码仓库](https://git.woa.com/blueking-plugins/saas/tapd-move-itera)

![alt text](image-30.png)

 

![alt text](image-31.png)

 


## 5. 发布插件

在开发者中心的插件控制台发布插件，并使用。


## 感受

- 能让代码能力薄弱的同学快速开发插件，满足业务需求，在开发和使用插件的过程中提升开发能力。
- 耗时主要分为3部分：写需求文档、开发插件、调试，最长是 `写需求文档`

## 附录

### Cursor 最佳实践

Cursor 主设计写的协作规范。

![alt text](image-32.png)

 


### 通过 context7 让模型理解目标开发框架

context7 可以理解为是 智能IDE的 `知识库`  （爬取开发框架仓库的文档入库），让 智能IDE 快速理解开发框架（比如蓝鲸插件的开发框架）

[https://context7.com/tencentblueking/bk-plugin-framework-python/llms.txt?topic=showPassword&tokens=5640](https://context7.com/tencentblueking/bk-plugin-framework-python/llms.txt?topic=showPassword&tokens=5640)

![alt text](image-33.png)

 

这对开发框架的文档有要求，文档越完善、Content7 清洗更合理，将让智能IDE更高效的理解开发框架。

### 安全性

- 把敏感信息放在系统环境变量中，比如 `export TAPD_IDC_API_IP="9.146.161.37"`
- 需求文档中对输入/输出示例进行脱敏

### 如何生成产品需求文档

生成一个存量插件项目的需求文档，以便后续维护

你可以本文第一段 `编写需求文档`  的内容作为模板，让 Cursor 生成已有代码仓库的需求文档。

记得 @ 特定文件，比如  `@form.js`  `@v1_0_0.py` 以及 `对应库`

以下是基于上述 `需求模板` 生成一个存量插件项目的需求文档，以便后续维护。

```markdown
参照 /Users/spark/Downloads/storySpec.mdc  的格式生成 `读取企业微信智能表格的数据`的产品需求文档
```


![alt text](image-34.png)

 

![alt text](image-35.png)

 

![alt text](image-36.png)

 

