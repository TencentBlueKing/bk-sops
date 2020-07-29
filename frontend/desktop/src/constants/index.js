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
const TASK_STATE_DICT = {
    'CREATED': i18n.t('未执行'),
    'RUNNING': i18n.t('执行中'),
    'READY': i18n.t('排队中'),
    'SUSPENDED': i18n.t('暂停'),
    'NODE_SUSPENDED': i18n.t('节点暂停'),
    'FAILED': i18n.t('失败'),
    'FINISHED': i18n.t('完成'),
    'REVOKED': i18n.t('撤销')
}

const NODE_DICT = {
    'startpoint': i18n.t('开始节点'),
    'endpoint': i18n.t('结束节点'),
    // 'startPoint': i18n.t('开始节点'),
    // 'endPoint': i18n.t('结束节点'),
    'parallelgateway': i18n.t('并行网关'),
    'branchgateway': i18n.t('分支网关'),
    'convergegateway': i18n.t('汇聚网关'),
    'tasknode': i18n.t('标准插件节点'),
    'subflow': i18n.t('子流程节点')
}

const INVALID_NAME_CHAR = '\'‘"”$&<>'

const SYSTEM_GROUP_ICON = ['CMDB', 'JOB', 'BK', 'Nodeman', 'Monitor', 'GCLOUD', 'TCM']
const BK_PLUGIN_ICON = {
    'bk_http_request': 'common-icon-bk-plugin-http',
    'bk_notify': 'common-icon-bk-plugin-notify',
    'sleep_timer': 'common-icon-bk-plugin-timer',
    'pause_node': 'common-icon-bk-plugin-pause'
}

// 最大长度常量
const TEMPLATE_NAME_MAX_LENGTH = 50
const TEMPLATE_NODE_NAME_MAX_LENGTH = 50
const TASK_NAME_MAX_LENGTH = 100
const STAGE_NAME_MAX_LENGTH = 50
const DRAFT_NAME_MAX_LENGTH = 20
const PROJECT_NAME_MAX_LENGTH = 50
const PROJECT_DESC_LENGTH = 512
const SCHEME_NAME_MAX_LENGTH = 30
const APP_NAME_MAX_LENGTH = 20
const APP_DESCRIPTION_MAX_LENGTH = 30
const VARIABLE_NAME_MAX_LENGTH = 20
const VARIABLE_KEY_MAX_LENGTH = 20
const SOURCE_NAME_MAX_LENGTH = 50

const STRING_LENGTH = {
    TEMPLATE_NAME_MAX_LENGTH,
    TEMPLATE_NODE_NAME_MAX_LENGTH,
    TASK_NAME_MAX_LENGTH,
    STAGE_NAME_MAX_LENGTH,
    DRAFT_NAME_MAX_LENGTH,
    PROJECT_NAME_MAX_LENGTH,
    PROJECT_DESC_LENGTH,
    SCHEME_NAME_MAX_LENGTH,
    APP_NAME_MAX_LENGTH,
    APP_DESCRIPTION_MAX_LENGTH,
    VARIABLE_NAME_MAX_LENGTH,
    VARIABLE_KEY_MAX_LENGTH,
    SOURCE_NAME_MAX_LENGTH
}

const NAME_REG = /^[^'"‘’“”\$<>]+$/
const PACKAGE_NAME_REG = /^[^\d][\w]*?$/
// celery的crontab时间表达式正则表达式（分钟 小时 星期 日 月）（以空格分割）
// 例子请见图片assets/images/task-zh.png
const PERIODIC_REG = /^((\*\/)?(([0-5]?\d[,-/])*([0-5]?\d))|\*)[ ]((\*\/)?(([0]?[0-9]|1\d|2[0-3])[,-/])*(([0]?[0-9]|1\d|2[0-3]))|\*)[ ]((\*\/)?((([0-6][,-/])*[0-6])|((mon|tue|wed|thu|fri|sat|sun)[,-/])*(mon|tue|wed|thu|fri|sat|sun))|\*)[ ]((\*\/)?((0?[1-9]|[12]\d|3[01])[,-/])*((0?[1-9]|[12]\d|3[01]))|\*)[ ]((\*\/)?((0?[1-9]|1[0-2])[,-/])*(0?[1-9]|1[0-2])|\*)$/

/* eslint-disable */
const URL_REG= new RegExp('^(https?|ftp|file)://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]$')
/* eslint-enable */

export {
    TASK_STATE_DICT, NODE_DICT, SYSTEM_GROUP_ICON, BK_PLUGIN_ICON, NAME_REG,
    INVALID_NAME_CHAR, PACKAGE_NAME_REG, URL_REG, PERIODIC_REG, STRING_LENGTH
}
