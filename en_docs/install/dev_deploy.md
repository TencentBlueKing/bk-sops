# Development environment backend deployment

## Deploy Blueking Community Edition
The login authentication of SOPS SaaS depends on Blueking PaaS platform. Business information is retrieved via interface provided by Blueking CMDB. Therefore, you should deploy Blueking PaaS platform and Blueking CMDB as integration test environment.

1) If you only need to customize SOPS, and don't want to modify the source code of Blueking PaaS and Blueking CMDB, we suggest that you download the full Community Edition package from our official Blueking website.
- [Download URL] (https://bk.tencent.com/download/)
- [Deployment Guide] (https://docs.bk.tencent.com/bkce_install_guide/)
- [Product Forum] (https://bk.tencent.com/s-mart/community)
- QQ Group: 495299374

2) If you wish to use all open source Blueking products for custom development, you can deploy the open source Blueking PaaS platform and Blueking CMDB.
- [Blueking PaaS Platform] (https://github.com/Tencent/bk-PaaS)  
- [Blueking CMDB] (https://github.com/Tencent/bk-cmdb)  

Please refer to relevant documents of each open-source product to see the deployment instructions. After the Blueking PaaS platform is deployed, you also need to upload and deploy SOPS SaaS, and enable app authentication session whitelist.
You can [click here] (https://github.com/Tencent/bk-sops/releases) to download the Release version of SOPS, and then go to "Developer Center" -> "S-mart App" on Blueking PaaS platform to upload and deploy the new app.
You may refer to "User Authentication" in "Developer Center"->"API Gateway"->"Usage Guide"->"About API Calling". Add default SOPS APP_ID, which is bk_sops to app authentication session whitelist.


## Prepare local rabbitmq resource  
Install rabbitmq locally and launch rabbitmq-server. Keep the default service monitor port (5672).


## Prepare local redis resource  
Install redis locally and launch redis-server. Keep the default service monitor port (6379).


## Prepare local mysql  
Install mysql locally and launch mysql-server. Keep the default service monitor port (3306).


## Install python and dependent libraries
Install python 3.6.7 and pip locally. Pull the source code to the project directory via git, then execute the pip command to install the python packages.
```bash
pip install -r requirements.txt
```


## Environment configuration and database preparation

1)

When executing django `manage.py` command, you need to make sure that the following environment variables are present:

```
export APP_ID = "bk_sops"
export APP_TOKEN = "{Your SOPS App TOKEN}"
export BK_PAAS_HOST = "{Development Environment PAAS Domain}"
export RUN_VER = "open"
export DB_NAME = "{Your DB Name}"
export BKAPP_PYINSTRUMENT_ENABLE = "1"
export BKAPP_BK_IAM_SYSTEM_ID="bk_sops"
export BKAPP_API_JWT_EXEMPT="1"
export BK_IAM_SKIP="True"
export BKAPP_IAM_SKIP="True"
```


2) Add local configuration local_settings.py to the project root directory

```python
# -*- coding: utf-8 -*-
import os

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME'),
        'USER': '',  # Local database account
        'PASSWORD': '',  # Local database password
        'HOST': 'localhost',
        'PORT': '3306',
        'TEST_CHARSET': "utf8",
        'TEST_COLLATION': "utf8_general_ci",
        'TEST': {
            'CHARSET': 'utf8',
            'COLLATION': 'utf8_general_ci',
        }
    },
}

REDIS = {
    'host': 'localhost',
    'port': 6379,
    'db': 0
}

EXTERNAL_PLUGINS_SOURCE_SECURE_RESTRICT = False
BK_IAM_SYNC_TEMPLATES = False

STATIC_ROOT = 'staticfiles'
```


## Create and initialize database  

1) Create bk_sops database in mysql
```sql
CREATE DATABASE `bk_sops` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
```

2) Execute the following commands in project directory to initialize the database
```bash
python manage.py migrate
python manage.py createcachetable django_cache
```


## Package and collect frontend static resources

1) Install dependencies  
Go to frontend/desktop/ and execute the following command to install
```bash
npm install
```

2) Local packaging
Go to frontend/desktop/ and execute the following command to package the frontend static resources
```bash
npm run build -- --STATIC_ENV=dev
```

3) Collect static resources
Go back to the project root directory and execute the following command to collect the frontend static resources and put them into the static directory
```bash
python manage.py collectstatic --noinput
```

The frontend resource files need to be copied and collected separately, execute the following command
```bash
rm -rf static/dev static/images
mv frontend/desktop/static/dev static/
mv frontend/desktop/static/images static/
```


## Configure local hosts  
windows: add "127.0.0.1 dev.{BK_PAAS_HOST}" to C:\Windows\System32\drivers\etc\host file.  
mac: Execute "sudo vim /etc/hosts" and add "127.0.0.1 dev.{BK_PAAS_HOST}".


## Start the process
```bash
python manage.py celery worker -l info -B
python manage.py runserver 8000
```


## Access the page  
Enter URL http://dev.{BK_PAAS_HOST}:8000/ in browser to access the app.
