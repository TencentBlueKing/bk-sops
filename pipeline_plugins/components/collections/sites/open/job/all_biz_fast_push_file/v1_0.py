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

from pipeline.component_framework.component import Component

from pipeline_plugins.base.utils.inject import supplier_account_for_business
from pipeline_plugins.components.collections.sites.open.job.all_biz_fast_push_file.base_service import (
    BaseAllBizJobFastPushFileService,
)
from gcloud.conf import settings

__group_name__ = _("作业平台(JOB)")


class AllBizJobFastPushFileService(BaseAllBizJobFastPushFileService):
    def get_params_list(self, data, parent_data):
        biz_cc_id = int(data.get_one_of_inputs("all_biz_cc_id"))
        upload_speed_limit = data.get_one_of_inputs("upload_speed_limit")
        download_speed_limit = data.get_one_of_inputs("download_speed_limit")
        job_timeout = data.get_one_of_inputs("job_timeout")
        file_source = self.get_file_source(data, parent_data)

        executor = parent_data.get_one_of_inputs("executor")
        supplier_account = supplier_account_for_business(biz_cc_id)
        # 拼装参数列表
        params_list = []
        for source in file_source:
            for attr in data.get_one_of_inputs("job_dispatch_attr"):
                job_account = attr["job_target_account"]
                job_target_path = attr["job_target_path"]
                result, target_server = self.get_target_server_biz_set(
                    executor, [attr], supplier_account, logger_handle=self.logger, ip_key="job_ip_list"
                )
                if not result:
                    raise Exception("源文件信息处理失败，请检查ip配置是否正确")

                job_kwargs = {
                    "bk_scope_type": self.biz_scope_type,
                    "bk_scope_id": str(biz_cc_id),
                    "bk_biz_id": biz_cc_id,
                    "file_source_list": [source],
                    "target_server": target_server,
                    "account_alias": job_account,
                    "file_target_path": job_target_path,
                }
                if upload_speed_limit:
                    job_kwargs["upload_speed_limit"] = int(upload_speed_limit)
                if download_speed_limit:
                    job_kwargs["download_speed_limit"] = int(download_speed_limit)
                if job_timeout:
                    job_kwargs["timeout"] = int(job_timeout)
                params_list.append(job_kwargs)

        return params_list


class AllBizJobFastPushFileComponent(Component):
    name = _("业务集快速分发文件")
    code = "all_biz_job_fast_push_file"
    bound_service = AllBizJobFastPushFileService
    form = "%scomponents/atoms/job/all_biz_fast_push_file/v1_0.js" % settings.STATIC_URL
    version = "v1.0"
    desc = _("跨业务分发文件时需要在作业平台添加白名单")
