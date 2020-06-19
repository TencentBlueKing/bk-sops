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

__group_name__ = _("配置平台(CMDB)")

from .batch_delete_set import *  # noqa
from .create_set import *  # noqa
from .empty_set_hosts import *  # noqa
from .replace_fault_machine import *  # noqa
from .transfer_fault_host import *  # noqa
from .transfer_host_module import *  # noqa
from .transfer_host_resource import *  # noqa
from .transfer_to_idle import *  # noqa
from .update_host import *  # noqa
from .update_module import *  # noqa
from .update_set import *  # noqa
from .update_set_service_status import *  # noqa
from .host_lock.add_host_lock import *  # noqa
from .host_lock.delete_host_lock import *  # noqa

