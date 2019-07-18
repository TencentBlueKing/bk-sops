# 正式环境源码部署

## Fork 源代码到自己的仓库  
通过 Fork 源代码到自己的仓库，可以进行二次开发和定制。建议公共特性开发和 bug 修复通过 Pull requests 及时提交到官方仓库。如果不需要进行二次开发，请直接在 releases 中获取打包好的版本，上传部署升级官方标准运维 SaaS。


## 打包并收集前端静态资源
1）安装依赖包  
进入 frontend/desktop/，执行以下命令安装
```bash
npm install
```

2）打包前端资源
在 frontend/desktop/ 目录下，继续执行以下命令打包前端静态资源
```bash
npm run build -- --SITE_URL="/o/bk_sops" --STATIC_ENV="open/prod"
```

3）收集静态资源
回到项目根目录，执行以下命令收集前端静态资源到 static 目录下
```bash
python manage.py collectstatic --noinput
rm -rf static/open static/images
mv frontend/desktop/static/open static/
mv frontend/desktop/static/images static/
```


## 创建应用  
前往你部署的蓝鲸PaaS平台，在"开发者中心"点击"应用创建"，填写需要的参数，注意代码仓库填写你的 Github 仓库地址，账号和密码。注意，由于官方已经存在一个名为"标准运维"的应用，你只能填写不一样的应用名称和应用 ID，如"标准运维定制版"、bk-sops-ce。
后续文档中bk-sops-ce都代表你创建的应用的应用ID，如和文档示例不一致，请以你的应用ID为准。


## 修改配置  
前往你部署的蓝鲸PaaS平台，在"开发者中心"点击"新手指南"，按照文档指引进行操作，主要是数据库配置修改和设置APP_ID, APP_TOKEN, BK_PAAS_HOST 等变量。


## 开通 API 白名单
手动在你部署的蓝鲸社区版的中控机执行如下命令，开通标准运维访问蓝鲸PaaS平台API网关的白名单，以便标准插件可以正常调用 API。
```bash
source /data/install/utils.fc
add_app_token bk-sops-ce "$(_app_token bk-sops-ce)" "标准运维定制版"
```
注意把"标准运维定制版" 和 bk-sops-ce 改为你创建的应用名称和应用 ID。


# 准备 redis 资源
在你部署的蓝鲸社区版的运行环境找一台机器，新建一个 redis 服务账号和密码。也可以公用部署蓝鲸社区版时已经有的 redis 服务。


## 部署应用  
前往你部署的蓝鲸PaaS平台，在"开发者中心"点击"我的应用"，找到你刚才创建的应用，点击"应用部署"，请勾选"启用celery"和"启用周期性任务"。这样你就可以在测试环境访问你新建的"标准运维定制版"应用了。


## 修改标准运维环境变量配置
在浏览器输入网址 http://{BK_PAAS_HOST}/o/bk-sops-ce/admin/，打开标准运维管理后台页面。

![](../resource/img/admin_home.png)

找到“环境变量 EnvironmentVariables”表并单击进入编辑页面。将第二步中准备好的 redis 信息填写到环境变量配置中，即增加3条数据 BKAPP_REDIS_HOST、BKAPP_REDIS_PORT、BKAPP_REDIS_PASSWORD。
如果直接复用蓝鲸已经部署好的 redis 服务，环境变量可以分别配置为：
- BKAPP_REDIS_HOST=在中控机执行 `source /data/install/utils.fc && echo $REDIS_IP` 获取
- BKAPP_REDIS_PASSWORD=在中控机执行 `source /data/install/utils.fc && echo $REDIS_PASS` 获取
- BKAPP_REDIS_PORT=6379

![](../resource/img/admin_envs.png)


## 重新部署应用
由于环境变量只有在项目启动时才会加载，所以修改后必须重新部署才会生效，请进入开发者中心，找到你创建的应用，点击"应用部署"，请勾选"启用celery"和"启用周期性任务"。


## 替换官方标准运维 SaaS  
按照前面的步骤操作后，你已经在蓝鲸社区版 PaaS 上创建了一个标准运维的定制版本，如果功能测试正常（请主要测试流程模板创建、任务执行、任务操作等核心功能），那么你可以选择下架官方标准运维应用，并用定制版本替换。  

1) 如果需要保留官方标准运维应用的所有数据，你需要修改数据库配置  
获取你部署的蓝鲸官方标准运维应用的数据库名、数据库账号密码，默认测试环境是 bk_sops_bkt，正式环境是 bk_sops。修改代码的 config/stag.py 和 config/prod.py，分别修改为官方标准运维应用的数据库信息。
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',  # 默认用mysql
        'NAME': 'bk_sops',                     # 数据库名 (测试环境写 bk_sops_bkt)
        'USER': '',                            # 官方标准运维应用数据库user
        'PASSWORD': '',                        # 官方标准运维应用数据库password
        'HOST': '',                   		   # 官方标准运维应用数据库HOST
        'PORT': '',                            # 官方标准运维应用数据库PORT
    },
}

```

2) 由于标准运维接入了蓝鲸PaaS平台API网关，你需要修改标准运维网关配置
请参考[API网关替换方式](https://docs.bk.tencent.com/bk_osed/guide.html#SaaS)文档，把标准运维 API 转发到你的定制版本的接口。
