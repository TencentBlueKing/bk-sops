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
from django.conf import settings

import env
from api.client import BKComponentClient

NODEMAN_API_ENTRY = env.BK_NODEMAN_API_ENTRY or "{}/{}".format(settings.BK_PAAS_ESB_HOST, "api/c/compapi/v2/nodeman")

NODEMAN_API_ENTRY_V2 = env.BK_NODEMAN_API_ENTRY or "{}/{}".format(
    settings.BK_PAAS_ESB_HOST,
    "api/c/compapi/{bk_api_ver}/nodeman/api".format(bk_api_ver=settings.DEFAULT_BK_API_VER),
)


def _get_nodeman_api(api_name):
    return "{}/{}/".format(NODEMAN_API_ENTRY, api_name)


def _get_nodeman_api_v2(api_name):
    return "{}/{}/".format(NODEMAN_API_ENTRY_V2, api_name)


class BKNodeManClient(BKComponentClient):
    def create_task(self, bk_biz_id, bk_cloud_id, node_type, op_type, creator, hosts):
        return self._request(
            method="post",
            url=_get_nodeman_api("create_task"),
            data={
                "bk_biz_id": bk_biz_id,
                "bk_cloud_id": bk_cloud_id,
                "node_type": node_type,
                "op_type": op_type,
                "creator": creator,
                "hosts": hosts,
            },
        )

    def get_task_info(self, bk_biz_id, job_id):
        return self._request(
            method="get",
            url=_get_nodeman_api("get_task_info"),
            data={"bk_biz_id": bk_biz_id, "job_id": job_id},
        )

    def get_log(self, host_id, bk_biz_id):
        return self._request(
            method="get",
            url=_get_nodeman_api("get_log"),
            data={"host_id": host_id, "bk_biz_id": bk_biz_id},
        )

    def search_host_plugin(self, bk_biz_id, pagesize, conditions):
        return self._request(
            method="post",
            url=_get_nodeman_api_v2("plugin/search"),
            data={"bk_biz_id": bk_biz_id, "pagesize": pagesize, "conditions": conditions},
        )

    def job_install(self, job_type, hosts, **kwargs):
        data = {"job_type": job_type, "hosts": hosts}
        data.update(kwargs)
        return self._request(method="post", url=_get_nodeman_api_v2("job/install"), data=data)

    def remove_host(self, bk_biz_id, bk_host_id, is_proxy):
        return self._request(
            method="post",
            url=_get_nodeman_api_v2("remove_host"),
            data={"bk_biz_id": bk_biz_id, "bk_host_id": bk_host_id, "is_proxy": is_proxy},  # 是否移除PROXY
        )

    def job_operate(self, job_type, bk_biz_id, bk_host_id):
        return self._request(
            method="post",
            url=_get_nodeman_api_v2("job/operate"),
            data={"job_type": job_type, "bk_biz_id": bk_biz_id, "bk_host_id": bk_host_id},
        )

    def job_details(self, job_id):
        return self._request(method="post", url=_get_nodeman_api_v2("job/details"), data={"job_id": job_id})

    def get_job_log(self, job_id, instance_id):
        return self._request(
            method="post",
            url=_get_nodeman_api_v2("job/log"),
            data={"job_id": job_id, "instance_id": instance_id},
        )

    def cloud_list(self):
        return self._request(method="get", url=_get_nodeman_api_v2("cloud"), data={})

    def ap_list(self):
        return self._request(method="get", url=_get_nodeman_api_v2("ap"), data={})

    def plugin_operate(self, params: dict):
        return self._request(method="post", url=_get_nodeman_api_v2("plugin/operate"), data=params)

    def plugin_process(self, category):
        return self._request(method="post", url=_get_nodeman_api_v2("plugin/process"), data={"category": category})

    def plugin_package(self, name, os):
        return self._request(method="post", url=_get_nodeman_api_v2("plugin/package"), data={"name": name, "os": os})

    def get_rsa_public_key(self, executor):
        return self._request(
            method="post",
            url=_get_nodeman_api("core/api/encrypt_rsa/fetch_public_keys"),
            data={
                "bk_app_code": settings.APP_CODE,
                "bk_app_secret": settings.SECRET_KEY,
                "bk_username": executor,
                "names": ["DEFAULT"],
            },
        )

    def install_channel(self):
        return self._request(method="get", url=_get_nodeman_api_v2("install_channel"), data={})

    def get_ipchooser_host_details(self, params: dict):
        return self._request(method="post", url=_get_nodeman_api("core/api/ipchooser_host/details"), data=params)
