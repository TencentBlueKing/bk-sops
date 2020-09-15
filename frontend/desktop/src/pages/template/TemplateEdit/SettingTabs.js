/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2020 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
import i18n from '@/config/i18n/index.js'

const SETTING_TABS = [
    {
        id: 'globalVariableTab',
        icon: 'common-icon-square-code',
        title: i18n.t('全局变量'),
        desc: i18n.t()
    },
    {
        id: 'templateConfigTab',
        icon: 'common-icon-square-attribute',
        title: i18n.t('基础信息')
    },
    {
        id: 'tplSnapshootTab',
        icon: 'common-icon-clock-reload',
        title: i18n.t('本地快照'),
        desc: i18n.t('可自动保存最近的50次快照，每5分钟一次。仅在本地浏览器存储。')
    },
    {
        id: 'templateDataEditTab',
        icon: 'common-icon-paper',
        title: i18n.t('模板数据')
    }
]

export default SETTING_TABS
