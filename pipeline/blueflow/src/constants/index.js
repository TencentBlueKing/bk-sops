/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
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
    'parallelgateway': gettext('并行网关'),
    'branchgateway': gettext('分支网关'),
    'convergegateway': gettext('汇聚网关'),
    'tasknode': gettext('原子节点'),
    'subflow': gettext('子流程节点')
}

const NAME_REG = /^[A-Za-z0-9\_\-\[\]\【\】\(\)\（\）\u4e00-\u9fa5]+$/

export { TASK_STATE_DICT, NODE_DICT, NAME_REG }
