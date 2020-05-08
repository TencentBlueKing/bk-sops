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

"""
version log app name, need to add in the INSTALLED_APPS
example:
    from version_log.quick_start_settings import version_log_app
    INSTALLED_APPS += (
        version_log_app,
    )

version log url setting, need to add in the root urls.py
example:
    from version_log.quick_start_settings import version_log_app
    import version_log.config as config
    urlpatterns += [
        url(r'^{}'.format(config.ENTRANCE_URL), include('{}.urls'.format(version_log_app))),
    ]
"""
version_log_app = 'version_log'
