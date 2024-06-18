# -*- coding: utf-8 -*-
"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from django.utils.translation import ugettext_lazy as _

from gcloud.core.models import EnvironmentVariables


def i18n_footer(language):
    default = """
        <div class="copyright">
            <ul class="link-list">
                <a href="https://wpa1.qq.com/KziXGWJs?_type=wpa&qidian=true" class="link-item" target="_blank">{}</a>
                <a href="http://bk.tencent.com/s-mart/community/" class="link-item" target="_blank">{}</a>
                <a href="http://bk.tencent.com/index" class="link-item" target="_blank">{}</a>
            </ul>
            <div class="desc">Copyright &copy; 2012 Tencent BlueKing. \
            All Rights Reserved. V${{sops_version}}</div>
        </div>
        """.format(
        _("技术支持"), _("社区论坛"), _("产品官网")
    )

    footer_key = "BKAPP_FOOTER"
    if language != "zh-cn":
        footer_key = "BKAPP_FOOTER_{}".format(language.upper())
    return EnvironmentVariables.objects.get_var(footer_key, default)


FOOTER_INFO = {
    "tech_support_url": "https://wpa1.qq.com/KziXGWJs?_type=wpa&qidian=true",
    "smart_url": "http://bk.tencent.com/s-mart/community/",
    "bk_tencent_url": "http://bk.tencent.com/index",
}

FOOTER = i18n_footer
