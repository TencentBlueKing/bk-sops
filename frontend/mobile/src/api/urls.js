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
export function getMobileUrlSetting (SITE_URL, BIZ_CC_ID, PLATFORM_URL = 'weixin/') {
    return {
        business: SITE_URL + PLATFORM_URL + 'api/v3/weixin_business/',
        component: SITE_URL + PLATFORM_URL + 'api/v3/weixin_component/',
        template: SITE_URL + PLATFORM_URL + 'api/v3/weixin_template/',
        variable: SITE_URL + PLATFORM_URL + 'api/v3/weixin_variable/',
        instance: SITE_URL + PLATFORM_URL + 'api/v3/weixin_taskflow/',
        templateCollect: SITE_URL + PLATFORM_URL + 'template/api/collect/' + BIZ_CC_ID + '/',
        templateCollectList: SITE_URL + PLATFORM_URL + 'template/api/get_collect_template/' + BIZ_CC_ID + '/',
        instancePreview: SITE_URL + PLATFORM_URL + 'taskflow/api/preview_task_tree/' + BIZ_CC_ID + '/',
        instanceStart: SITE_URL + PLATFORM_URL + 'taskflow/api/action/start/' + BIZ_CC_ID + '/',
        instancePause: SITE_URL + PLATFORM_URL + 'taskflow/api/action/pause/' + BIZ_CC_ID + '/',
        instanceRevoke: SITE_URL + PLATFORM_URL + 'taskflow/api/action/revoke/' + BIZ_CC_ID + '/',
        instanceResume: SITE_URL + PLATFORM_URL + 'taskflow/api/action/resume/' + BIZ_CC_ID + '/',
        instanceDetail: SITE_URL + PLATFORM_URL + 'taskflow/detail/' + BIZ_CC_ID + '/',
        instanceStatus: SITE_URL + PLATFORM_URL + 'taskflow/api/status/' + BIZ_CC_ID + '/',
        nodeActInfo: SITE_URL + PLATFORM_URL + 'taskflow/api/nodes/data/' + BIZ_CC_ID + '/',
        nodeActDetails: SITE_URL + PLATFORM_URL + 'taskflow/api/nodes/detail/' + BIZ_CC_ID + '/',
        nodeRetry: SITE_URL + PLATFORM_URL + 'taskflow/api/nodes/action/retry/' + BIZ_CC_ID + '/',
        nodeSkip: SITE_URL + PLATFORM_URL + 'taskflow/api/nodes/action/skip/' + BIZ_CC_ID + '/',
        nodeRevoke: SITE_URL + PLATFORM_URL + 'taskflow/api/nodes/action/revoke/' + BIZ_CC_ID + '/',
        pauseNodeResume: SITE_URL + PLATFORM_URL + 'taskflow/api/nodes/action/callback/' + BIZ_CC_ID + '/',
        pauseSubProcess: SITE_URL + PLATFORM_URL + 'taskflow/api/nodes/action/pause_subproc/' + BIZ_CC_ID + '/',
        resumeSubProcess: SITE_URL + PLATFORM_URL + 'taskflow/api/nodes/action/resume_subproc/' + BIZ_CC_ID + '/',
        setSleepNode: SITE_URL + PLATFORM_URL + 'taskflow/api/nodes/spec/timer/reset/' + BIZ_CC_ID + '/',
        schemes: SITE_URL + PLATFORM_URL + 'api/v3/weixin_scheme/'
    }
}
