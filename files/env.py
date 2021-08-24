# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import os

BKAPP_NFS_CONTAINER_ROOT = os.getenv("BKAPP_NFS_CONTAINER_ROOT")
BKAPP_NFS_HOST_ROOT = os.getenv("BKAPP_NFS_HOST_ROOT")

# BKREPO相关配置信息，启用
BKREPO_ENDPOINT_URL = os.getenv("BKAPP_BKREPO_ENDPOINT_URL")
BKREPO_USERNAME = os.getenv("BKAPP_BKREPO_USERNAME")
BKREPO_PASSWORD = os.getenv("BKAPP_BKREPO_PASSWORD")
BKREPO_PROJECT = os.getenv("BKAPP_BKREPO_PROJECT")
BKREPO_BUCKET = os.getenv("BKAPP_BKREPO_BUCKET")

# JOB默认文件业务ID
JOB_FILE_BIZ_ID = int(os.getenv("BKAPP_JOB_FILE_BIZ_ID", -1))
# JOB凭据名称
JOB_CREDENTIAL_NAME = os.getenv("BKAPP_JOB_CREDENTIAL_NAME", "SopsBKRepoCredential")
# JOB文件源标识
JOB_FILE_SOURCE_CODE = os.getenv("BKAPP_JOB_FILE_SOURCE_CODE", "SopsBKRepoFileSource")
# JOB文件源别名
JOB_FILE_SOURCE_ALIAS = os.getenv("BKAPP_JOB_FILE_SOURCE_ALIAS", "标准运维蓝鲸制品库文件源")

BKAPP_FILE_MGR_SOURCE_ACCOUNT = os.getenv("BKAPP_FILE_MGR_SOURCE_ACCOUNT", "root")
