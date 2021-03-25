# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import logging

from blueapps.account import get_user_model

logger = logging.getLogger("blueapps")


def get_component_client_common_args():
    """
    获取ComponentClient需要的common_args
    @return:
    {
        bk_username = 'xxx'
    }
    @rtype: dict
    """
    try:
        last_login_user = get_user_model().objects.all().order_by("-last_login")[0]
    except IndexError:
        logger.exception("There is not a last_login_user")
        raise IndexError("There is not a last_login_user")
    username = last_login_user.username
    return dict(bk_username=username)
