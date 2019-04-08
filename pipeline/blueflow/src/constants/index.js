/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
* Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
* an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
* specific language governing permissions and limitations under the License.
*/
const TASK_STATE_DICT = {
    'CREATED': gettext('未执行'),
    'RUNNING': gettext('执行中'),
    'SUSPENDED': gettext('暂停'),
    'NODE_SUSPENDED': gettext('节点暂停'),
    'FAILED': gettext('失败'),
    'FINISHED': gettext('完成'),
    'REVOKED': gettext('撤销')
}

const NODE_DICT = {
    'startpoint': gettext('开始节点'),
    'endpoint': gettext('结束节点'),
    // 'startPoint': gettext('开始节点'),
    // 'endPoint': gettext('结束节点'),
    'parallelgateway': gettext('并行网关'),
    'branchgateway': gettext('分支网关'),
    'convergegateway': gettext('汇聚网关'),
    'tasknode': gettext('标准插件节点'),
    'subflow': gettext('子流程节点')
}

// 最大长度常量
const TEMPLATE_NAME_MAX_LENGTH = 50
const TEMPLATE_NODE_NAME_MAX_LENGTH = 50
const TASK_NAME_MAX_LENGTH = 100
const STAGE_NAME_MAX_LENGTH = 50
const DRAFT_NAME_MAX_LENGTH = 20
const SCHEME_NAME_MAX_LENGTH = 30
const APP_NAME_MAX_LENGTH = 20
const APP_DESCRIPTION_MAX_LENGTH = 30
const VARIABLE_NAME_MAX_LENGTH = 20
const VARIABLE_KEY_MAX_LENGTH = 20

const STRING_LENGTH = {
    TEMPLATE_NAME_MAX_LENGTH,
    TEMPLATE_NODE_NAME_MAX_LENGTH,
    TASK_NAME_MAX_LENGTH,
    STAGE_NAME_MAX_LENGTH,
    DRAFT_NAME_MAX_LENGTH,
    SCHEME_NAME_MAX_LENGTH,
    APP_NAME_MAX_LENGTH,
    APP_DESCRIPTION_MAX_LENGTH,
    VARIABLE_NAME_MAX_LENGTH,
    VARIABLE_KEY_MAX_LENGTH
}

const NAME_REG = /^[^'"‘’“”\$<>]+$/
// celery的crontab时间表达式正则表达式（分钟 小时 星期 日 月）（以空格分割）
// 例子请见图片assets/images/task-zh.png
const PERIODIC_REG = /^((\*\/)?(([0-5]?\d[,-/])*([0-5]?\d))|\*)[ ]((\*\/)?(([0]?[0-9]|1\d|2[0-3])[,-/])*(([0]?[0-9]|1\d|2[0-3]))|\*)[ ]((\*\/)?((([0-6][,-/])*[0-6])|((mon|tue|wed|thu|fri|sat|sun)[,-/])*(mon|tue|wed|thu|fri|sat|sun))|\*)[ ]((\*\/)?((0?[1-9]|[12]\d|3[01])[,-/])*((0?[1-9]|[12]\d|3[01]))|\*)[ ]((\*\/)?((0?[1-9]|1[0-2])[,-/])*(0?[1-9]|1[0-2])|\*)$/

/* eslint-disable */
const URL_REG= new RegExp('^(https?|ftp|file)://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]$')
/* eslint-enable */

export { TASK_STATE_DICT, NODE_DICT, NAME_REG, URL_REG , PERIODIC_REG, STRING_LENGTH}
