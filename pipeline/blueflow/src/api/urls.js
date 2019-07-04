/**
* Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
* Copyright (C) 2017-2019 THL A29 Limited, a Tencent company. All rights reserved.
* Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
* http://opensource.org/licenses/MIT
* Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
*/
export function getUrlSetting (SITE_URL, BIZ_CC_ID) {
    return {
        // 业务人员列表
        bizPerson: SITE_URL + 'core/api/get_roles_and_personnel/' + BIZ_CC_ID + '/',
        // 更改默认业务
        bizDefaultChange: SITE_URL + 'core/api/change_default_business/' + BIZ_CC_ID + '/',
        homelist: SITE_URL + 'taskflow/home/' + BIZ_CC_ID + '/',
        business: SITE_URL + 'api/v3/business/',
        component: SITE_URL + 'api/v3/component/',
        template: SITE_URL + 'api/v3/template/',
        variable: SITE_URL + 'api/v3/variable/',
        instance: SITE_URL + 'api/v3/taskflow/',
        function: SITE_URL + 'api/v3/function_task/',
        businessBaseInfo: SITE_URL + 'template/get_business_basic_info/',
        subform: SITE_URL + 'template/api/form/' + BIZ_CC_ID + '/',
        // 有某模板权限的人员列表
        templatePersons: SITE_URL + 'template/api/get_perms/' + BIZ_CC_ID + '/',
        templatePersonsSave: SITE_URL + 'template/api/save_perms/' + BIZ_CC_ID + '/',
        templateCollect: SITE_URL + 'template/api/collect/' + BIZ_CC_ID + '/',
        templateUploadCheck: SITE_URL + 'template/api/import_check/' + BIZ_CC_ID + '/',
        templateImport: SITE_URL + 'template/api/import/' + BIZ_CC_ID + '/',
        templateExport: SITE_URL + 'template/api/export/' + BIZ_CC_ID + '/',
        instanceClone: SITE_URL + 'taskflow/api/clone/' + BIZ_CC_ID + '/',
        instancePreview: SITE_URL + 'taskflow/api/preview_task_tree/' + BIZ_CC_ID + '/',
        instanceStart: SITE_URL + 'taskflow/api/action/start/' + BIZ_CC_ID + '/',
        instancePause: SITE_URL + 'taskflow/api/action/pause/' + BIZ_CC_ID + '/',
        instanceRevoke: SITE_URL + 'taskflow/api/action/revoke/' + BIZ_CC_ID + '/',
        instanceResume: SITE_URL + 'taskflow/api/action/resume/' + BIZ_CC_ID + '/',
        instanceModify: SITE_URL + 'taskflow/api/inputs/modify/' + BIZ_CC_ID + '/',
        instanceClaim: SITE_URL + 'taskflow/api/flow/claim/' + BIZ_CC_ID + '/',
        instanceDetail: SITE_URL + 'taskflow/detail/' + BIZ_CC_ID + '/',
        instanceStatus: SITE_URL + 'taskflow/api/status/' + BIZ_CC_ID + '/',
        nodeActInfo: SITE_URL + 'taskflow/api/nodes/data/' + BIZ_CC_ID + '/',
        // 执行详情
        nodeActDetails: SITE_URL + 'taskflow/api/nodes/detail/' + BIZ_CC_ID + '/',
        nodeRetry: SITE_URL + 'taskflow/api/nodes/action/retry/' + BIZ_CC_ID + '/',
        nodeSkip: SITE_URL + 'taskflow/api/nodes/action/skip/' + BIZ_CC_ID + '/',
        nodeRevoke: SITE_URL + 'taskflow/api/nodes/action/revoke/' + BIZ_CC_ID + '/',
        skipExclusiveGateway: SITE_URL + 'taskflow/api/nodes/action/skip_exg/' + BIZ_CC_ID + '/',
        pauseNodeResume: SITE_URL + 'taskflow/api/nodes/action/callback/' + BIZ_CC_ID + '/',
        pauseSubProcess: SITE_URL + 'taskflow/api/nodes/action/pause_subproc/' + BIZ_CC_ID + '/',
        resumeSubProcess: SITE_URL + 'taskflow/api/nodes/action/resume_subproc/' + BIZ_CC_ID + '/',
        setSleepNode: SITE_URL + 'taskflow/api/nodes/spec/timer/reset/' + BIZ_CC_ID + '/',
        taskCount: SITE_URL + 'taskflow/api/query_task_count/' + BIZ_CC_ID + '/',
        schemes: SITE_URL + 'api/v3/schemes/',
        configBizExecutor: SITE_URL + 'config/api/biz_executor/' + BIZ_CC_ID + '/',
        appmaker: SITE_URL + 'api/v3/appmaker/',
        appmakerEdit: SITE_URL + 'appmaker/save/' + BIZ_CC_ID + '/',
        analysisTemplate: SITE_URL + 'analysis/query_template_by_group/',
        analysisAtom: SITE_URL + 'analysis/query_atom_by_group/',
        analysisAppmaker: SITE_URL + 'analysis/query_appmaker_by_group/',
        analysisInstance: SITE_URL + 'analysis/query_instance_by_group/',
        categorys: SITE_URL + 'analysis/get_task_category/'
    }
}
