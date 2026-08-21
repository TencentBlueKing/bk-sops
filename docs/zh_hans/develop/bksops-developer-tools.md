## 前言

在开发标准运维的插件的过程中，除了编写插件本身的逻辑之外，开发者需要频繁的进行项目`静态文件的收集`,`项目重启`，`celery worker重启`上，本标准运维开发者工具包通过给django，djcelery打补丁的方式，在不需要显式的修改项目源码的同时，实现 **自动静态文件收集，自动项目重启，插件代码修改worker自动重启**，使标准运维插件开发者可以将精力集中在插件本身的逻辑上，提高插件开发的效率。

## 安装

添加环境变量 `USE_AUTO_PATCH=True`

在`local_settings.py `中添加以下内容：

```python
from scripts.auto_reload_tools.auth_collectstatic_patch import patch_django_autoreload
from scripts.auto_reload_tools.auto_reload_worker import patch_worker_autoreload

# 静态文件 js 文件改变 项目自动收集静态文件+重启项目
patch_django_autoreload()
# 监听的插件目录文件发生改变，worker 将会自动完成重启
patch_worker_autoreload()
```

## 注意事项：

- 在使用`patch_django_autoreload`之前请确保您的插件静态文件开发的位置为：`pipeline_plugins//components//static`, 如果您直接在项目根目录下开发`js`, 最后将该`js`文件手动拷到`pipeline_plugins//components//static`, **请谨慎使用该功能**，否则的话可能会出现`pipeline_plugins//components//static`下面的文件覆盖您`static`下面`js`文件的情况。
- 目前的 `patch_worker_autoreload` 补丁监听到您**插件代码发生改变之后会立即重启worker**，这非常适合在本地开发插件的情况，**但是这并不意味着如果有正在运行的任务时，重启会延迟**(后面可能会增加这个配置项)，**目前的情况而言大多数情况该插件是适用的。**
- `猴子补丁对于项目而言是非常危险的事情，除非你非常清楚它干了什么。`本工具包只适用于提升本地插件开发的效率，请勿用到正式环境！

