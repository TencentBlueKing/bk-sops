<!-- TOC -->

- [单元测试](#单元测试)
- [核心流程测试](#核心流程测试)

<!-- TOC -->



## 单元测试步骤

进入bamboo-pipeline/test目录，下面的相关操作都在该目录中进行。

1. 安装相关包

   ``` bash
   $ pip install -r requirements.txt
   ```

2. 初始化数据库

   ``` bash
   $ python manage.py migrate
   ```

   注：默认使用sqlite数据库，这种做法目录中会多生成一个db.sqlite3文件。也可以使用下面**核心流程控制步骤**中mysql作为数据库进行测试。

3. 启动相关服务

   ``` bash
   $ rabbitmq-server
   $ redis-server
   $ python manage.py celery worker -B -l info
   ```

4. 开启单元测试

   ``` bash
   $ python manage.py test pipeline.tests
   ```

5. 如果测试成功，会有如下显示：

   ``` bash
   .....
   ----------------------------------------------------------------------
   Ran 457 tests in 17.075s
   
   OK
   ```
   
----
## 核心流程测试步骤



进入bamboo-pipeline/test目录，下面相关操作都在该目录中进行。

1. 安装相关包

   ``` bash
   $ pip install -r requirements.txt
   $ pip install pytest
   $ pip install pytest_django
   ```

2. 创建并初始化数据库

   ``` bash
   $ mysql
   > CREATE DATABASE `bambootest` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
   > exit
   $ PIPELINE_TEST_DB_TYPE="mysql" PIPELINE_TEST_DB_NAME="bambootest" PIPELINE_TEST_DB_USER="root" PIPELINE_TEST_DB_PWD="" python manage.py migrate
   ```

   数据库名、用户、密码等根据实际情况进行替换

3. 启动相关服务

   ``` bash
   $ rabbitmq-server
   $ redis-server
   $ PIPELINE_TEST_DB_TYPE="mysql" PIPELINE_TEST_DB_NAME="bambootest" PIPELINE_TEST_DB_USER="root" PIPELINE_TEST_DB_PWD="" python manage.py celery worker -B -l info
   ```

4. 开启核心流程测试

   ``` bash
   $ PIPELINE_TEST_DB_TYPE="mysql" PIPELINE_TEST_DB_NAME="bambootest" PIPELINE_TEST_DB_USER="root" PIPELINE_TEST_DB_PWD="" pytest pipeline_test_use/tests
   ```

5. 如果成功, 会有如下显示：

   ``` bash
   collected 51 items
   ....
   51 passed in 461.75s (0:07:41)
   ```

   

