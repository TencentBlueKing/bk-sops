# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import os

from config import BK_PAAS_HOST as _BK_PAAS_HOST

REMOTE_ANALYSIS_URL = "%s/console/static/js/analysis.min.js" % os.environ.get("BK_PAAS_HOST", _BK_PAAS_HOST)
REMOTE_API_URL = "%s/console/static/bk_api/api.js" % os.environ.get("BK_PAAS_HOST", _BK_PAAS_HOST)

ESB_SDK_NAME = "packages.blueking.component"

CALLBACK_KEY = b"5w15CAhkRsjp5SF2Jk_ypzi4jVgsDtzSro1-7Gnl2hQ="
RSA_PRIV_KEY = """
-----BEGIN RSA PRIVATE KEY-----
MIICXQIBAAKBgQCr5dIZVAp6ia+tLVlDKPUZP4RD7sH+Rbc9eHIy46OoBQeLgRhp
93MEarByPlSdO0BveWi/o7PzAxTX3aev2PobfuDkCG0xQNpyXtq7NMU9GP4lo9MD
eEw0+GNvzKjxl4sn9ajCvAFMRcAt61/JqIQnxE+/iymoAVK67gfTOTvckQIDAQAB
AoGAVWLhjCdM1TWTiChgkJXFufbtEnmE73Nd5DDyOQkOgCWPa+KCaBC8l1MPto/z
o+6MwVLDj34XovzC27+EzjqvcSvb8IgYlY2cY4Sn73CDPRMHN4WZTk1+Bt0JABDz
iUN6gY/uBTbwMO/erETocpE+LCseRYXWFTnACWCqIzryA2ECQQDkUIim2Bg2PQXt
+3pDGAwNj44gVHld+Y3XL4sPv0h7eS+X8wiFI/zAK9TW15wJvjVh4aWBbz3EeXfR
hLjruIgVAkEAwL322W8+dMcHvm4Dbe+U3cmyu15MZY/InxKa4Yes3E/VtuevcvLz
9F5ah8tzI56RukALwaKsa9VKNvxVMc6FjQJATbDt30B3dLVtOB8z6nLbXx3zciLs
rcLGtmvSOUiRBJsnS+CCjLPDRS1lHrp9uX8FMUqUhCfzb9EZqa0tM+E2RQJBAKrN
bRygzYs0+XLTESzyPE0TOdV7Kl5yPcph9WjZD+Goye4tgLhv/qpWlwlxzNYK5n9T
1FdDbmKdAAicMm9R4d0CQQCop0FTm4D125ZUUVQBQ2MjlQyhFdJSX9/p2uqelize
T8ow3nMSbvx5X28wOjbk04tmfM/kVqcVhFWhDHjHZzlt
-----END RSA PRIVATE KEY-----
"""

# PUB_KEY for frontend, which can not use three quotes
RSA_PUB_KEY = (
    "-----BEGIN PUBLIC KEY-----\\n"
    + "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCr5dIZVAp6ia+tLVlDKPUZP4RD\\n"
    + "7sH+Rbc9eHIy46OoBQeLgRhp93MEarByPlSdO0BveWi/o7PzAxTX3aev2PobfuDk\\n"
    + "CG0xQNpyXtq7NMU9GP4lo9MDeEw0+GNvzKjxl4sn9ajCvAFMRcAt61/JqIQnxE+/\\n"
    + "iymoAVK67gfTOTvckQIDAQAB\\n"
    + "-----END PUBLIC KEY-----"
)

# APIGW Auth
APIGW_APP_CODE_KEY = "bk_app_code"
APIGW_USER_USERNAME_KEY = "bk_username"

COMPATIBLE_MODULE_MAP = {
    # 插件路径迁移兼容
    "pipeline.components.collections.common": "pipeline_plugins.components.collections.common",
    "pipeline.components.collections.controller": "pipeline_plugins.components.collections.controller",
    "pipeline.components.collections.sites.enterprise.bk": "pipeline_plugins.components.collections.sites.open.bk",
    "pipeline.components.collections.sites.enterprise.cc": "pipeline_plugins.components.collections.sites.open.cc",
    "pipeline.components.collections.sites.enterprise.job": "pipeline_plugins.components.collections.sites.open.job",
    "pipeline_plugins.components.collections.sites.enterprise.bk": "pipeline_plugins.components.collections.sites.open.bk",  # noqa
    "pipeline_plugins.components.collections.sites.enterprise.cc": "pipeline_plugins.components.collections.sites.open.cc",  # noqa
    "pipeline_plugins.components.collections.sites.enterprise.job": "pipeline_plugins.components.collections.sites.open.job",  # noqa
    "pipeline_plugins.components.collections.sites.open.cc_plugins.v1_0": "pipeline_plugins.components.collections.sites.open.cc.create_set.v1_0",  # noqa
    # 变量路径迁移兼容
    "pipeline.variables.collections.common": "pipeline_plugins.variables.collections.common",
    "pipeline.variables.collections.sites.enterprise.cc": "pipeline_plugins.variables.collections.sites.open.cc",
    "pipeline_plugins.variables.collections.sites.enterprise.cc": "pipeline_plugins.variables.collections.sites.open.cc",  # noqa
}

USER_TOKEN_TYPE = "bk_token"
