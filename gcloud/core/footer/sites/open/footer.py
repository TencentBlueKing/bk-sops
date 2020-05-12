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

from django.utils.translation import ugettext_lazy as _

from gcloud.core.models import EnvironmentVariables


def i18n_footer():
    default = """
        <div class="copyright">
            <ul class="link-list">
                <a href="tencent://message/?uin=800802001&site=qq&menu=yes" class="link-item">{}(800802001)</a>
                <a href="http://bk.tencent.com/s-mart/community/" class="link-item" target="_blank">{}</a>
                <a href="http://bk.tencent.com/" class="link-item" target="_blank">{}</a>
            </ul>
            <div class="desc">Copyright &copy; 2012-${{year}} Tencent BlueKing. All Rights Reserved.</div>
            <div>{}</div>
        </div>
        """.format(
        _("QQ咨询"), _("蓝鲸论坛"), _("蓝鲸官网"), _("蓝鲸智云 版权所有")
    )

    return EnvironmentVariables.objects.get_var("BKAPP_FOOTER", default)


FOOTER = i18n_footer
