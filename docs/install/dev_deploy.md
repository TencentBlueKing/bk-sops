# 开发环境后台部署

## 准备本地 rabbitmq 资源  
在本地安装 rabbitmq，并启动 rabbitmq-server，服务监听的端口保持默认（5672）。


## 准备本地 redis 资源  
在本地安装 redis，并启动 redis-server，服务监听的端口保持默认（6379）。


## 准备本地 mysql  
在本地安装 mysql，并启动 mysql-server，服务监听的端口保持默认（3306）。


## 本地 python 包安装  
通过 git 拉取源代码到工程目录中，并进入目录下运行 
```bash
pip install -r requirements.txt
```


## 配置本地环境变量和数据库

1) 设置环境变量  
有两种方式设置本地开发需要的环境变量，一是手动设置，即执行如下命令

```bash
export APP_ID="bk_sops"
export APP_TOKEN="{APP_TOKEN}"
export BK_PAAS_HOST=""
export BK_CC_HOST=""
export BK_JOB_HOST=""
```
BK_PAAS_HOST、BK_CC_HOST、BK_JOB_HOST 分别改为你部署的蓝鲸社区版域名、配置平台域名、作业平台域名（需要加上 http 前缀；如果是 https 域名，请改为 https 前缀）。
APP_ID 设置为你的社区版标准运维应用ID，默认设置为 bk_sops。APP_TOKEN 设置为你的社区版标准运维应用 TOKEN，默认可以访问 http://{BK_PAAS_HOST}/admin/app/app/，找到名为"标准运维"的应用，查看详情获取 Token 字段值。

二是直接修改 scripts/develop/sites/community/env.sh，然后执行

```bash
source scripts/develop/sites/community/env.sh
```

2) 修改 config/dev.py，设置本地开发用的数据库信息，添加 Redis 本地信息

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',  # 默认用mysql
        'NAME': APP_ID,       # 数据库名 (默认与APP_ID相同)
        'USER': 'root',       # 你的数据库user
        'PASSWORD': '',       # 你的数据库password
        'HOST': 'localhost',  # 数据库HOST
        'PORT': '3306',       # 默认3306
    },
}

REDIS = {
    'host': 'localhost',
    'port': 6379,
}
```


## 创建并初始化数据库  

1) 在 mysql 中创建名为 bk_sops 的数据库
```sql
CREATE DATABASE `bk_sops` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
```

2) 在工程目录下执行以下命令初始化数据库
```bash
python manage.py migrate
python manage.py createcachetable django_cache
```


## 打包并收集前端静态资源

1）安装依赖包  
进入 pipeline/blueflow/，执行以下命令安装
```bash
npm install
```

2）本地打包
在 pipeline/blueflow/ 目录下，继续执行以下命令打包前端静态资源
```bash
npm run build -- --STATIC_ENV=dev
```

3）收集静态资源
回到项目根目录，执行以下命令收集前端静态资源到 static 目录下
```bash
python manage.py collectstatic --noinput
```

前端资源文件需要单独拷贝收集，执行如下命令
```bash
rm -rf static/dev static/images
mv pipeline/blueflow/static/dev static/
mv pipeline/blueflow/static/images static/
```


## 配置本地 hosts  
windows: 在 C:\Windows\System32\drivers\etc\host 文件中添加“127.0.0.1 dev.{BK_PAAS_HOST}”。  
mac: 执行 “sudo vim /etc/hosts”，添加“127.0.0.1 dev.{BK_PAAS_HOST}”。


## 启动进程
```bash
python manage.py celery worker -l info
python manage.py runserver 8000
```


## 访问页面  
使用浏览器开发 http://dev.{BK_PAAS_HOST}:8000/ 访问应用。
