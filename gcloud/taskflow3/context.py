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

from django.utils import translation
from django.utils.translation import ugettext_lazy as _

from gcloud.core.utils import get_biz_maintainer_info

logger = logging.getLogger("root")


class TaskContext(object):
    """
    @summary: 流程任务内置环境变量
    """
    prefix = '_system'

    def __init__(self, taskflow, operator=''):
        # 执行任务的操作员
        operator = operator or taskflow.executor
        biz_cc_id = taskflow.business.cc_id
        # 调用蓝鲸API网关的执行者，一般是业务运维
        executor, _ = get_biz_maintainer_info(biz_cc_id, operator, use_in_context=True)

        self.language = translation.get_language()
        self.biz_cc_id = biz_cc_id
        self.biz_cc_name = taskflow.business.cc_name
        self.biz_supplier_account = taskflow.business.cc_owner
        self.operator = operator
        self.executor = executor
        self.task_id = taskflow.id
        self.task_name = taskflow.pipeline_instance.name

    @classmethod
    def to_flat_key(cls, key):
        return '${%s.%s}' % (cls.prefix, key)

    def context(self):
        return {
            '${%s}' % TaskContext.prefix: {
                'type': 'plain',
                'is_param': True,
                'value': self
            }
        }

    @classmethod
    def flat_details(cls):
        details = [
            {
                'key': cls.to_flat_key('language'),
                'name': _(u"执行环境语言CODE"),
            },
            {
                'key': cls.to_flat_key('biz_cc_id'),
                'name': _(u"任务所属的CMDB业务ID"),
            },
            {
                'key': cls.to_flat_key('biz_cc_name'),
                'name': _(u"任务所属的CMDB业务名称"),
            },
            {
                'key': cls.to_flat_key('biz_supplier_account'),
                'name': _(u"任务所属的CMDB业务开发商账号"),
            },
            {
                'key': cls.to_flat_key('operator'),
                'name': _(u"任务的操作员（点击开始执行的人员）"),
            },
            {
                'key': cls.to_flat_key('executor'),
                'name': _(u"任务的执行者（调用API网关接口的人员）"),
            },
            {
                'key': cls.to_flat_key('task_id'),
                'name': _(u"任务ID"),
            },
            {
                'key': cls.to_flat_key('task_name'),
                'name': _(u"任务名称"),
            }
        ]
        return details
