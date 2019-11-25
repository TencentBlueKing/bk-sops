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
export function getUrlSetting (SITE_URL, PROJECT_ID) {
    return {
        // 业务人员列表
        bizPerson: SITE_URL + 'core/api/get_roles_and_personnel/' + PROJECT_ID + '/',
        permission: SITE_URL + 'core/api/query_apply_permission_url/',
        permissionQuery: SITE_URL + 'core/api/query_resource_verify_perms/',
        userList: SITE_URL + 'core/api/get_user_list/',
        // 更改默认项目
        projectDefaultChange: SITE_URL + 'core/api/change_default_project/',
        projectBaseInfo: SITE_URL + 'core/api/get_basic_info/',
        homelist: SITE_URL + 'taskflow/home/' + PROJECT_ID + '/',
        business: SITE_URL + 'api/v3/business/',
        component: SITE_URL + 'api/v3/component/',
        template: SITE_URL + 'api/v3/template/',
        variable: SITE_URL + 'api/v3/variable/',
        instance: SITE_URL + 'api/v3/taskflow/',
        function: SITE_URL + 'api/v3/function_task/',
        periodic: SITE_URL + 'api/v3/periodic_task/',
        project: SITE_URL + 'api/v3/project/',
        collectList: SITE_URL + 'api/v3/collection/',
        commonProject: SITE_URL + 'api/v3/common_project/',
        subform: SITE_URL + 'template/api/form/' + PROJECT_ID + '/',
        // 有某模板权限的人员列表
        templatePersons: SITE_URL + 'template/api/get_perms/' + PROJECT_ID + '/',
        templatePersonsSave: SITE_URL + 'template/api/save_perms/' + PROJECT_ID + '/',
        // templateCollect: SITE_URL + 'template/api/collect/' + PROJECT_ID + '/',
        templateUploadCheck: SITE_URL + 'template/api/import_check/' + PROJECT_ID + '/',
        templateImport: SITE_URL + 'template/api/import/' + PROJECT_ID + '/',
        templateExport: SITE_URL + 'template/api/export/' + PROJECT_ID + '/',
        templateSummary: SITE_URL + 'template/api/get_template_count/' + PROJECT_ID + '/',
        templateAutoDraw: SITE_URL + 'template/api/draw_pipeline/',
        instanceClone: SITE_URL + 'taskflow/api/clone/' + PROJECT_ID + '/',
        instancePreview: SITE_URL + 'taskflow/api/preview_task_tree/' + PROJECT_ID + '/',
        instanceStart: SITE_URL + 'taskflow/api/action/start/' + PROJECT_ID + '/',
        instancePause: SITE_URL + 'taskflow/api/action/pause/' + PROJECT_ID + '/',
        instanceRevoke: SITE_URL + 'taskflow/api/action/revoke/' + PROJECT_ID + '/',
        instanceResume: SITE_URL + 'taskflow/api/action/resume/' + PROJECT_ID + '/',
        instanceModify: SITE_URL + 'taskflow/api/inputs/modify/' + PROJECT_ID + '/',
        instanceClaim: SITE_URL + 'taskflow/api/flow/claim/',
        instanceDetail: SITE_URL + 'taskflow/detail/' + PROJECT_ID + '/',
        instanceStatus: SITE_URL + 'taskflow/api/status/',
        internalVariable: SITE_URL + 'taskflow/api/context/',
        nodeActInfo: SITE_URL + 'taskflow/api/nodes/data/' + PROJECT_ID + '/',
        // 执行详情
        nodeActDetails: SITE_URL + 'taskflow/api/nodes/detail/' + PROJECT_ID + '/',
        jobInstanceLog: SITE_URL + 'taskflow/api/nodes/get_job_instance_log/',
        nodeRetry: SITE_URL + 'taskflow/api/nodes/action/retry/' + PROJECT_ID + '/',
        nodeSkip: SITE_URL + 'taskflow/api/nodes/action/skip/' + PROJECT_ID + '/',
        nodeRevoke: SITE_URL + 'taskflow/api/nodes/action/revoke/' + PROJECT_ID + '/',
        skipExclusiveGateway: SITE_URL + 'taskflow/api/nodes/action/skip_exg/' + PROJECT_ID + '/',
        pauseNodeResume: SITE_URL + 'taskflow/api/nodes/action/callback/' + PROJECT_ID + '/',
        pauseSubProcess: SITE_URL + 'taskflow/api/nodes/action/pause_subproc/' + PROJECT_ID + '/',
        resumeSubProcess: SITE_URL + 'taskflow/api/nodes/action/resume_subproc/' + PROJECT_ID + '/',
        setSleepNode: SITE_URL + 'taskflow/api/nodes/spec/timer/reset/' + PROJECT_ID + '/',
        taskCount: SITE_URL + 'taskflow/api/query_task_count/' + PROJECT_ID + '/',
        schemes: SITE_URL + 'api/v3/scheme/',
        commonSchemes: SITE_URL + 'api/v3/common_scheme/',
        bizConfig: SITE_URL + 'config/api/biz_config/' + PROJECT_ID + '/',
        configBizExecutor: SITE_URL + 'config/api/biz_executor/' + PROJECT_ID + '/',
        appmaker: SITE_URL + 'api/v3/appmaker/',
        appmakerEdit: SITE_URL + 'appmaker/save/' + PROJECT_ID + '/',
        appmakerSummary: SITE_URL + 'appmaker/get_appmaker_count/' + PROJECT_ID + '/',
        analysisTemplate: SITE_URL + 'analysis/query_template_by_group/',
        analysisAtom: SITE_URL + 'analysis/query_atom_by_group/',
        analysisAppmaker: SITE_URL + 'analysis/query_appmaker_by_group/',
        analysisInstance: SITE_URL + 'analysis/query_instance_by_group/',
        categorys: SITE_URL + 'analysis/get_task_category/',
        periodicEnable: SITE_URL + 'periodictask/api/enabled/' + PROJECT_ID + '/',
        periodicModifyCron: SITE_URL + 'periodictask/api/cron/' + PROJECT_ID + '/',
        periodicModifyConstants: SITE_URL + 'periodictask/api/constants/' + PROJECT_ID + '/',
        commonTemplate: SITE_URL + 'api/v3/common_template/',
        commonSubAtom: SITE_URL + 'common_template/api/form/',
        commonTemplatePersons: SITE_URL + 'common_template/api/get_perms/',
        commonTemplatePersonsSave: SITE_URL + 'common_template/api/save_perms/',
        commonTemplateImport: SITE_URL + 'common_template/api/import/',
        commonTemplateExport: SITE_URL + 'common_template/api/export/',
        commonTemplateUploadCheck: SITE_URL + 'common_template/api/import_check/',
        taskCreateMethod: SITE_URL + 'taskflow/api/get_task_create_method/',
        cc_search_host: SITE_URL + 'pipeline/cc_search_host/' + PROJECT_ID + '/',
        cc_search_topo_tree: SITE_URL + 'pipeline/cc_search_topo_tree/' + PROJECT_ID + '/',
        cc_get_mainline_object_topo: SITE_URL + 'pipeline/cc_get_mainline_object_topo/' + PROJECT_ID + '/',
        packageSource: SITE_URL + 'api/v3/package_source/',
        syncTask: SITE_URL + 'api/v3/sync_task/'
    }
}
