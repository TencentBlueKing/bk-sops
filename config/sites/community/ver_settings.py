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
import base64

import env

REMOTE_ANALYSIS_URL = "%s/console/static/js/analysis.min.js" % env.BK_PAAS_HOST
REMOTE_API_URL = "%s/console/static/bk_api/api.js" % env.BK_PAAS_HOST

ESB_SDK_NAME = "packages.blueking.component"

CALLBACK_KEY = b"jbSH1_3PFsM8WRZZpUXJPhlJuvuA44A7Ov0nPhFk5ZY="
DEFAULT_RSA_PRIV_KEY = """
-----BEGIN RSA PRIVATE KEY-----
MIICWwIBAAKBgQDA2XZvbf++4M6YLSgS93kYJS34e2TZvq/s6r0yFDz0je38ekW0
2aH5efPTNijbJgHIbqfXzm8lBpmBbk9VlUHaJVyZitqI6xYBqb3WBRu9WYEd8skF
y1mwOEbxOgsXoOPd9tLkt4etSMzm7kdBqmZKIeiAOtbmirDqkuz6M64b5wIDAQAB
AoGAdHxmX5RP4FomMCFGjX5R9NWwWOEf366g0ThRI4i58PYyBElPBZhXkDurna6f
KxBgD1NXqrEUzYaY/mdFIGrRpQfBPXDTSsJC+r68nxglcGVhuHCFvkY94J5bgYus
f7z2QkWdHi/LdENxP1eo+4ExcJ/XAHgOC18ThYTnZDo7G2ECQQDuzN9uSccn3sRE
Namwg54mcekkaTvBPLpX7+zNyLrNG6vGl/3NPQqi9D2ACXYkeWk8aQ65LoqLYnJJ
4bWmKaRPAkEAzr1S9q1rx/bV6iJOoEeeNGddWizWatTjLCT9XcXkETfIDc3YTpVD
bESXAcagtf6PbkNP1TG1MeXlTVhYp4tw6QJAa+frtnxkH+ILsf7FtNtkpV6nySo8
NC9qzL2/taVUs8YjMtQPfaRtoADZoXelCQpLwV5/prIfLKjJmBUD7he3BQJAVKYs
XBhx8zRcLjvR2cq5OlfAX3XQbXmxcpfKriSi13HxlcVc9gAj1SbYdb+wehQ7AjjJ
bU+nE0FAfETaN+/eUQJAMN4sJTjEMkeSeE+SBzqsmzc4ajMHRrhtu989JgZZvDyr
LOah9mmRwLJdcfa3Js+jw2lOCmxzqauYZHVHg/hH7g==
-----END RSA PRIVATE KEY-----
"""
RSA_PRIV_KEY = base64.b64decode(env.RSA_PRIV_KEY).decode("utf-8") if env.RSA_PRIV_KEY else DEFAULT_RSA_PRIV_KEY

# PUB_KEY for frontend, which can not use three quotes
DEFAULT_RSA_PUB_KEY = (
    "-----BEGIN PUBLIC KEY-----\\n"
    + "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDA2XZvbf++4M6YLSgS93kYJS34\\n"
    + "e2TZvq/s6r0yFDz0je38ekW02aH5efPTNijbJgHIbqfXzm8lBpmBbk9VlUHaJVyZ\\n"
    + "itqI6xYBqb3WBRu9WYEd8skFy1mwOEbxOgsXoOPd9tLkt4etSMzm7kdBqmZKIeiA\\n"
    + "OtbmirDqkuz6M64b5wIDAQAB\\n"
    + "-----END PUBLIC KEY-----"
)

RSA_PUB_KEY = base64.b64decode(env.RSA_PUB_KEY).decode("utf-8") if env.RSA_PUB_KEY else DEFAULT_RSA_PUB_KEY

# APIGW Auth
APIGW_APP_CODE_KEY = "bk_app_code"
APIGW_USER_USERNAME_KEY = "bk_username"

COMPATIBLE_MODULE_MAP = {
    # 插件路径迁移兼容
    "pipeline.components.collections.common": "pipeline_plugins.components.collections.common",
    "pipeline.components.collections.controller": "pipeline_plugins.components.collections.controller",
    "pipeline.components.collections.sites.community.bk": "pipeline_plugins.components.collections.sites.open.bk",
    "pipeline.components.collections.sites.community.cc": "pipeline_plugins.components.collections.sites.open.cc",
    "pipeline.components.collections.sites.community.job": "pipeline_plugins.components.collections.sites.open.job",
    "pipeline_plugins.components.collections.sites.community.bk": "pipeline_plugins.components.collections.sites.open.bk",  # noqa
    "pipeline_plugins.components.collections.sites.community.cc": "pipeline_plugins.components.collections.sites.open.cc",  # noqa
    "pipeline_plugins.components.collections.sites.community.job": "pipeline_plugins.components.collections.sites.open.job",  # noqa
    "pipeline_plugins.components.collections.sites.open.cc_plugins.v1_0": "pipeline_plugins.components.collections.sites.open.cc.create_set.v1_0",  # noqa
    # 变量路径迁移兼容
    "pipeline.variables.collections.common": "pipeline_plugins.variables.collections.common",
    "pipeline.variables.collections.sites.community.cc": "pipeline_plugins.variables.collections.sites.open.cc",
    "pipeline_plugins.variables.variables.collections.sites.community.cc": "pipeline_plugins.variables.collections.sites.open.cc",  # noqa
}

USER_TOKEN_TYPE = "bk_token"
