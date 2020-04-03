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


from django.http import JsonResponse
from django.views.decorators.http import require_GET

from blueapps.account.decorators import login_exempt
from gcloud import err_code
from gcloud.apigw.decorators import mark_request_whether_is_trust
from gcloud.commons.template.models import CommonTemplate
from gcloud.apigw.views.utils import format_template_list_data

try:
    from bkoauth.decorators import apigw_required
except ImportError:
    from packages.bkoauth.decorators import apigw_required


@login_exempt
@require_GET
@apigw_required
@mark_request_whether_is_trust
def get_common_template_list(request):
    templates = CommonTemplate.objects.select_related("pipeline_template").filter(
        is_deleted=False
    )

    return JsonResponse(
        {
            "result": True,
            "data": format_template_list_data(templates),
            "code": err_code.SUCCESS.code,
        }
    )
