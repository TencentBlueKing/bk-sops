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
from django.conf.urls import url

from pipeline_plugins.components.utils.bcs_client import BCSClient


def bcs_get_clusters(request):

    project_id = request.GET['project_id']
    client = BCSClient()
    result = client.get_clusters(project_id)

    if not result['result']:
        return JsonResponse(result)

    data = []
    for cluster in result['data']:
        data.append({
            'text': cluster['name'],
            'value': cluster['cluster_id']
        })

    result['data'] = data
    return JsonResponse(result)


def bcs_get_musters(request):
    project_id = request.GET['project_id']
    bk_biz_id = request.GET['bk_biz_id']
    client = BCSClient()
    result = client.get_musters(bk_biz_id=bk_biz_id, project_id=project_id)

    if not result['result']:
        return JsonResponse(result)

    data = []
    for muster in result['data']:
        data.append({
            'text': muster['name'],
            'value': muster['id']
        })

    result['data'] = data
    return JsonResponse(result)


def bcs_get_muster_versions(request):
    project_id = request.GET['project_id']
    bk_biz_id = request.GET['bk_biz_id']
    muster_id = request.GET['muster_id']
    client = BCSClient()
    result = client.get_muster_versions(
        bk_biz_id=bk_biz_id,
        project_id=project_id,
        muster_id=muster_id
    )

    if not result['result']:
        return JsonResponse(result)

    data = []
    for muster_ver in result['data']:
        data.append({
            'text': muster_ver['show_version_name'],
            'value': '{id}_{show_id}'.format(
                id=muster_ver['id'],
                show_id=muster_ver['show_version_id']
            )
        })

    result['data'] = data
    return JsonResponse(result)


def bcs_get_version_template(request):
    project_id = request.GET['project_id']
    bk_biz_id = request.GET['bk_biz_id']
    version_id = request.GET['version_id']
    obj_type = request.GET['obj_type'].lower()

    # decompose {id}_{show_id}
    if '_' in version_id:
        version_id = int(version_id.split('_')[0])

    client = BCSClient()
    result = client.get_version_templates(
        bk_biz_id=bk_biz_id,
        project_id=project_id,
        version_id=version_id
    )

    if not result['result']:
        return JsonResponse(result)

    data = []
    for version_tmpl in result['data'].get(obj_type, []):
            data.append({
                'text': version_tmpl['name'],
                'value': '{id}_{name}'.format(
                    id=version_tmpl['id'],
                    name=version_tmpl['name']
                )
            })

    result['data'] = data
    return JsonResponse(result)


def bcs_get_namespaces(request):
    project_id = request.GET['project_id']
    bk_biz_id = request.GET['bk_biz_id']
    client = BCSClient()
    result = client.get_namespaces(
        project_id=project_id,
        bk_biz_id=bk_biz_id
    )

    if not result['result']:
        return JsonResponse(result)

    data = []
    for ns in result['data']:
        data.append({
            'text': ns['name'],
            'value': ns['id']
        })

    result['data'] = data
    return JsonResponse(result)


def bcs_get_instances(request):
    project_id = request.GET['project_id']
    bk_biz_id = request.GET['bk_biz_id']
    category = request.GET['category']
    namespace = request.GET.get('namespace')
    client = BCSClient()
    result = client.get_instances(
        project_id=project_id,
        bk_biz_id=bk_biz_id,
        category=category,
        namespace=namespace
    )

    if not result['result']:
        return JsonResponse(result)

    data = []
    for instance in result['data']:
        data.append({
            'text': '[{ns}]-{name}'.format(
                ns=instance['namespace'],
                name=instance['name']
            ),
            'value': instance['id']
        })

    result['data'] = data
    return JsonResponse(result)


def bcs_get_instance_versions(request):
    project_id = request.GET['project_id']
    bk_biz_id = request.GET['bk_biz_id']
    instance_id = request.GET['instance_id']
    client = BCSClient()
    result = client.get_instance_versions(
        bk_biz_id=bk_biz_id,
        project_id=project_id,
        instance_id=instance_id,
    )

    if not result['result']:
        return JsonResponse(result)

    data = []
    for version_tmpl in result['data']:
        data.append({
            'text': version_tmpl['name'],
            'value': version_tmpl['id']
        })

    result['data'] = data
    return JsonResponse(result)


urlpatterns = [
    url(r'bcs_get_clusters/$', bcs_get_clusters),
    url(r'bcs_get_musters/$', bcs_get_musters),
    url(r'bcs_get_muster_versions/$', bcs_get_muster_versions),
    url(r'bcs_get_version_templates/$', bcs_get_version_template),
    url(r'bcs_get_namespaces/$', bcs_get_namespaces),
    url(r'bcs_get_instances/$', bcs_get_instances),
    url(r'bcs_get_instance_versions/$', bcs_get_instance_versions),
]
