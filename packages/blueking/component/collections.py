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

from .apis.bk_login import CollectionsBkLogin
from .apis.bk_paas import CollectionsBkPaas
from .apis.cc import CollectionsCC
from .apis.cmsi import CollectionsCMSI
from .apis.gse import CollectionsGSE
from .apis.job import CollectionsJOB
from .apis.sops import CollectionsSOPS


# Available components
AVAILABLE_COLLECTIONS = {
    'bk_login': CollectionsBkLogin,
    'bk_paas': CollectionsBkPaas,
    'cc': CollectionsCC,
    'cmsi': CollectionsCMSI,
    'gse': CollectionsGSE,
    'job': CollectionsJOB,
    'sops': CollectionsSOPS,
}
