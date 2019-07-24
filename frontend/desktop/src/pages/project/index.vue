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
<template>
    <div class="project-container">
        <div class="list-wrapper">
            <BaseTitle :title="i18n.projectManage"></BaseTitle>
            <div class="list-header">
                <bk-button
                    v-cursor="{ active: !hasPermission(['create'], projectActions, authOperations) }"
                    type="primary"
                    :class="['create-project-btn', {
                        'btn-permission-disable': !hasPermission(['create'], projectActions, authOperations)
                    }]"
                    @click="onCreateProject">
                    {{i18n.createProject}}
                </bk-button>
                <div class="filter-area">
                    <div class="switch-status" @click="onClosedProjectToggle">
                        <span :class="['checkbox', { checked: isClosedShow }]"></span>
                        <span class="checkbox-name">{{i18n.showClosedProject}}</span>
                    </div>
                    <div class="search-input">
                        <BaseInput
                            v-model="searchStr"
                            class="search-input"
                            :placeholder="i18n.placeholder"
                            @input="onSearchInput">
                        </BaseInput>
                        <i class="common-icon-search"></i>
                    </div>
                </div>
            </div>
            <div class="project-table-content">
                <table class="project-table" v-bkloading="{ isLoading: loading, opacity: 1 }">
                    <thead>
                        <tr>
                            <th width="10%">ID</th>
                            <th width="30%">{{ i18n.projectName}}</th>
                            <th width="40%">{{ i18n.projectDesc}}</th>
                            <th width="10%">{{ i18n.creator }}</th>
                            <th width="10%">{{ i18n.operation }}</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="item in projectList" :key="item.id">
                            <td>{{item.id}}</td>
                            <td><div class="project-name" :title="item.name">{{item.name}}</div></td>
                            <td><div class="project-desc" :title="item.desc">{{item.desc || '--' }}</div></td>
                            <td>{{item.creator}}</td>
                            <td>
                                <bk-button
                                    v-cursor="{ active: !hasPermission(['view'], item.auth_actions, projectOperations) }"
                                    :class="['operate-btn', {
                                        'btn-permission-disable': !hasPermission(['view'], item.auth_actions, projectOperations)
                                    }]"
                                    type="default"
                                    @click="onViewProject(item)">
                                    {{i18n.view}}
                                </bk-button>
                                <bk-button
                                    v-cursor="{ active: !hasPermission(['edit'], item.auth_actions, projectOperations) }"
                                    :class="['operate-btn', {
                                        'btn-permission-disable': !hasPermission(['edit'], item.auth_actions, projectOperations)
                                    }]"
                                    type="default"
                                    @click="onEditProject(item)">
                                    {{i18n.edit}}
                                </bk-button>
                                <bk-button
                                    v-if="item.is_disable"
                                    v-cursor="{ active: !hasPermission(['edit'], item.auth_actions, projectOperations) }"
                                    :class="['operate-btn', {
                                        'btn-permission-disable': !hasPermission(['edit'], item.auth_actions, projectOperations)
                                    }]"
                                    type="default"
                                    @click="onChangeProjectStatus(item, 'start')">
                                    {{i18n.start}}
                                </bk-button>
                                <bk-button
                                    v-else
                                    v-cursor="{ active: !hasPermission(['edit'], item.auth_actions, projectOperations) }"
                                    :class="['operate-btn', {
                                        'btn-permission-disable': !hasPermission(['edit'], item.auth_actions, projectOperations)
                                    }]"
                                    type="default"
                                    @click="onChangeProjectStatus(item, 'stop')">
                                    {{i18n.stop}}
                                </bk-button>
                            </td>
                        </tr>
                        <tr v-if="!projectList.length" class="empty-tr">
                            <td colspan="4">
                                <div class="empty-data"><NoData /></div>
                            </td>
                        </tr>
                    </tbody>
                </table>
                <div class="panagation" v-if="totalPage > 1">
                    <div class="page-info">
                        <span> {{i18n.total}} {{totalCount}} {{i18n.item}}{{i18n.comma}} {{i18n.currentPageTip}} {{currentPage}} {{i18n.page}}</span>
                    </div>
                    <bk-paging
                        :cur-page.sync="currentPage"
                        :total-page="totalPage"
                        @page-change="onPageChange">
                    </bk-paging>
                </div>
            </div>
        </div>
        <CopyrightFooter></CopyrightFooter>
        <bk-dialog
            v-if="isProjectDialogShow"
            :quick-close="false"
            :has-header="true"
            :ext-cls="'common-dialog'"
            :title="projectDialogTitle"
            :is-show.sync="isProjectDialogShow"
            width="600"
            padding="30px 20px"
            @confirm="onProjectConfirm"
            @cancel="onEditProjectCancel">
            <div slot="content" class="dialog-content">
                <div class="common-form-item">
                    <label class="required">{{ i18n.name }}</label>
                    <div class="common-form-content">
                        <BaseInput
                            name="projectName"
                            :disabled="dialogType === 'edit'"
                            v-model="projectDetail.name"
                            data-vv-validate-on=" "
                            v-validate="nameRule">
                        </BaseInput>
                        <span v-show="errors.has('projectName')" class="common-error-tip error-msg">{{ errors.first('projectName') }}</span>
                    </div>
                </div>
                <div class="common-form-item">
                    <label class="required">{{ i18n.timeZone }}</label>
                    <div class="common-form-content">
                        <bk-selector
                            :disabled="dialogType === 'edit'"
                            :list="timeZoneList"
                            :selected="projectDetail.timeZone"
                            @item-selected="onChangeTimeZone">
                        </bk-selector>
                    </div>
                </div>
                <div class="common-form-item">
                    <label>{{ i18n.desc }}</label>
                    <div class="common-form-content">
                        <textarea v-model="projectDetail.desc" rows="5"></textarea>
                    </div>
                </div>
            </div>
        </bk-dialog>
        <bk-dialog
            v-if="isOperationDialogShow"
            :quick-close="false"
            :has-header="true"
            :ext-cls="'common-dialog'"
            :title="projectStatusTitle"
            :is-show="isOperationDialogShow"
            width="400"
            padding="30px"
            @confirm="onChangeStatusConfirm"
            @cancel="isOperationDialogShow = false">
            <div slot="content" class="operation-dialog-tips">
                {{i18n.confirm}}{{operationType === 'start' ? i18n.start : i18n.stop}}{{i18n.project}}:{{projectDetail.name}}?
            </div>
        </bk-dialog>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
    import { mapState, mapActions } from 'vuex'
    import { errorHandler } from '@/utils/errorHandler.js'
    import toolsUtils from '@/utils/tools.js'
    import NoData from '@/components/common/base/NoData.vue'
    import CopyrightFooter from '@/components/layout/CopyrightFooter.vue'
    import BaseTitle from '@/components/common/base/BaseTitle.vue'
    import BaseInput from '@/components/common/base/BaseInput.vue'
    import { NAME_REG, STRING_LENGTH } from '@/constants/index.js'
    import { getTimeZoneList } from '@/constants/timeZones.js'
    import permission from '@/mixins/permission.js'

    export default {
        name: 'ProjectHome',
        components: {
            NoData,
            BaseTitle,
            BaseInput,
            CopyrightFooter
        },
        mixins: [permission],
        data () {
            return {
                searchStr: '',
                projectList: [],
                loading: true,
                countPerPage: 15,
                totalCount: 0,
                totalPage: 1,
                currentPage: 1,
                isClosedShow: false,
                isProjectDialogShow: false,
                isOperationDialogShow: false,
                dialogType: 'create',
                operationType: 'stop',
                projectDetailLoading: false,
                addPengding: false,
                updatePending: false,
                projectDetail: {
                    name: '',
                    timeZone: 'Asia/Shanghai',
                    desc: ''
                },
                timeZoneList: getTimeZoneList(),
                nameRule: {
                    required: true,
                    max: STRING_LENGTH.PROJECT_NAME_MAX_LENGTH,
                    regex: NAME_REG
                },
                projectActions: [],
                projectOperations: [],
                projectResource: {},
                i18n: {
                    projectManage: gettext('项目管理'),
                    createProject: gettext('新建项目'),
                    editProject: gettext('编辑项目'),
                    showClosedProject: gettext('显示已停用项目'),
                    placeholder: gettext('请输入ID、名称、描述、创建人'),
                    projectName: gettext('项目名称'),
                    projectDesc: gettext('项目描述'),
                    creator: gettext('创建人'),
                    operation: gettext('操作'),
                    total: gettext('共'),
                    item: gettext('条记录'),
                    comma: gettext('，'),
                    currentPageTip: gettext('当前第'),
                    page: gettext('页'),
                    view: gettext('查看'),
                    edit: gettext('编辑'),
                    stop: gettext('停用'),
                    start: gettext('启用'),
                    controll: gettext('权限控制'),
                    name: gettext('名称'),
                    timeZone: gettext('时区'),
                    desc: gettext('描述'),
                    confirm: gettext('确认'),
                    project: gettext('项目')
                }
            }
        },
        computed: {
            ...mapState('project', {
                'authResource': state => state.authResource,
                'authOperations': state => state.authOperations,
                'project_id': state => state.project_id
            }),
            projectDialogTitle () {
                return this.dialogType === 'create' ? this.i18n.createProject : this.i18n.editProject
            },
            projectStatusTitle () {
                return this.operationType === 'stop' ? this.i18n.stop : this.i18n.start
            }
        },
        created () {
            this.queryProjectCreatePerm()
            this.getProjectList()
            this.onSearchInput = toolsUtils.debounce(this.searchInputhandler, 500)
        },
        methods: {
            ...mapActions([
                'queryUserPermission'
            ]),
            ...mapActions('project', [
                'loadProjectList',
                'createProject',
                'loadProjectDetail',
                'updateProject'
            ]),
            async queryProjectCreatePerm () {
                try {
                    const res = await this.queryUserPermission({
                        resource_type: 'project',
                        action_ids: JSON.stringify(['create'])
                    })
                    const hasCreatePerm = !!res.data.details.find(item => {
                        return item.action_id === 'create' && item.is_pass
                    })
                    if (hasCreatePerm) {
                        this.projectActions = ['create']
                    }
                } catch (err) {
                    errorHandler(err, this)
                }
            },
            async getProjectList () {
                this.loading = true

                try {
                    const data = {
                        limit: this.countPerPage,
                        offset: (this.currentPage - 1) * this.countPerPage,
                        is_disable: this.isClosedShow
                    }
                    
                    if (this.searchStr !== '') {
                        data.q = this.searchStr
                    }

                    const projectList = await this.loadProjectList(data)
                    this.projectList = projectList.objects || []
                    this.totalCount = projectList.meta.total_count
                    this.projectOperations = projectList.meta.auth_operations
                    this.projectResource = projectList.meta.auth_resource
                    const totalPage = Math.ceil(this.totalCount / this.countPerPage)
                    if (!totalPage) {
                        this.totalPage = 1
                    } else {
                        this.totalPage = totalPage
                    }
                } catch (err) {
                    errorHandler(err, this)
                } finally {
                    this.loading = false
                }
            },
            async getProjectDetail (id) {
                try {
                    this.projectDetailLoading = false
                    this.projectDetail = await this.loadProjectDetail(id)
                } catch (err) {
                    errorHandler(err, this)
                } finally {
                    this.projectDetailLoading = false
                }
            },
            
            async addProject () {
                if (this.addPengding) {
                    return
                }
                this.addPengding = true
                try {
                    const { name, timeZone: time_zone, desc } = this.projectDetail
                    const data = {
                        name,
                        desc,
                        time_zone
                    }
                    await this.createProject(data)
                    this.isProjectDialogShow = false
                    this.getProjectList()
                } catch (err) {
                    errorHandler(err, this)
                } finally {
                    this.addPengding = false
                }
            },
            async changeProject (disabled = false) {
                if (this.updatePending) {
                    return
                }
                this.updatePending = true
                try {
                    const { id, name, timeZone: time_zone, desc } = this.projectDetail
                    const data = {
                        id,
                        name,
                        desc,
                        time_zone,
                        is_disable: disabled
                    }
                    await this.updateProject(data)
                    this.isProjectDialogShow = false
                    this.isOperationDialogShow = false
                    this.clearProjectDetail()
                    this.getProjectList()
                } catch (err) {
                    errorHandler(err, this)
                } finally {
                    this.updatePending = false
                }
            },
            onPageChange (page) {
                this.currentPage = page
                this.getProjectList()
            },
            searchInputhandler () {
                this.currentPage = 1
                this.getProjectList()
            },
            onProjectPermissonCheck (required, project, event) {
                if (!this.hasPermission(required, project.auth_actions, this.projectOperations)) {
                    this.applyForPermission(['create'], project, this.projectOperations, this.projectResource)
                    event.preventDefault()
                }
            },
            clearProjectDetail () {
                this.projectDetail = {
                    name: '',
                    timeZone: 'Asia/Shanghai',
                    desc: ''
                }
            },
            onClosedProjectToggle () {
                this.isClosedShow = !this.isClosedShow
                this.currentPage = 1
                this.getProjectList()
            },
            onCreateProject () {
                if (!this.hasPermission(['create'], this.projectActions, this.authOperations)) {
                    const resourceData = {
                        name: gettext('项目'),
                        auth_actions: this.projectActions
                    }
                    this.applyForPermission(['create'], resourceData, this.projectOperations, this.projectResource)
                } else {
                    this.dialogType = 'create'
                    this.isProjectDialogShow = true
                }
            },
            onViewProject (project) {
                if (!this.hasPermission(['view'], project.auth_actions, this.projectOperations)) {
                    this.applyForPermission(['view'], project, this.projectOperations, this.projectResource)
                    return
                }
                this.$router.push(`/template/home/${this.project_id}/`)
            },
            onEditProject (project) {
                if (!this.hasPermission(['edit'], project.auth_actions, this.projectOperations)) {
                    this.applyForPermission(['edit'], project, this.projectOperations, this.projectResource)
                    return
                }
                this.isProjectDialogShow = true
                this.dialogType = 'edit'
                this.projectDetail = {
                    id: project.id,
                    name: project.name,
                    timeZone: project.time_zone,
                    desc: project.desc
                }
            },
            onEditProjectCancel () {
                this.isProjectDialogShow = false
                this.clearProjectDetail()
            },
            onProjectConfirm () {
                this.$validator.validateAll().then(result => {
                    if (!result) {
                        return
                    }
                    if (this.dialogType === 'edit') {
                        this.changeProject()
                    } else {
                        this.addProject()
                    }
                })
            },
            onChangeTimeZone (value) {
                this.projectDetail.timeZone = value
            },
            onChangeProjectStatus (project, type) {
                if (!this.hasPermission(['edit'], project.auth_actions, this.projectOperations)) {
                    this.applyForPermission(['edit'], project, this.projectOperations, this.projectResource)
                    return
                }
                this.operationType = type
                this.projectDetail = {
                    id: project.id,
                    name: project.name,
                    timeZone: project.time_zone,
                    desc: project.desc
                }
                this.isOperationDialogShow = true
            },
            onChangeStatusConfirm () {
                const disabled = this.operationType === 'stop'
                this.isOperationDialogShow = false
                this.changeProject(disabled)
            }
        }
    }
</script>
<style lang="scss" scoped>
    @import '@/scss/config.scss';
    .project-container {
        min-width: 1320px;
        min-height: calc(100% - 50px);
        background: $whiteNodeBg;
        .dialog-content {
            word-break: break-all;
        }
    }
    .list-wrapper {
        padding: 0 60px;
        min-height: calc(100vh - 240px);
    }
    .list-header {
        padding: 20px 0;
        .create-project-btn {
            width: 120px;
            height: 32px;
            line-height: 30px;
        }
        .filter-area {
            float: right;
            display: flex;
            justify-content: space-between;
            align-items: center;
            width: 520px;
            .switch-status {
                display: inline-block;
            }
        }
        .search-input {
            position: relative;
            width: 360px;
            input {
                height: 32px;
                padding: 0 32px 0 10px;
                font-size: 14px;
                color: #666666;
                border: 1px solid #c3cdd7;
                line-height: 32px;
                outline: none;
                &:hover {
                    border-color: #c0c4cc;
                }
                &:focus {
                    border-color: $blueDefault;
                }
            }
        }
        .common-icon-search {
            position: absolute;
            right: 15px;
            top: 8px;
            color: #63656e;
        }
        .switch-status {
            font-size: 14px;
            cursor: pointer;
            .checkbox {
                display: inline-block;
                position: relative;
                width: 14px;
                height: 14px;
                color: $whiteDefault;
                border: 1px solid $formBorderColor;
                border-radius: 2px;
                text-align: center;
                vertical-align: -2px;
                &:hover {
                    border-color: $greyDark;
                }
                &.checked {
                    background: $blueDefault;
                    border-color: $blueDefault;
                    &::after {
                        content: "";
                        position: absolute;
                        left: 2px;
                        top: 2px;
                        height: 4px;
                        width: 8px;
                        border-left: 1px solid;
                        border-bottom: 1px solid;
                        border-color: $whiteDefault;
                        transform: rotate(-45deg);
                    }
                }
            }
        }
    }
    .project-table {
        width: 100%;
        font-size: 12px;
        border: 1px solid #dddddd;
        border-collapse: collapse;
        background: #ffffff;
        table-layout: fixed;
        tr:not(.empty-tr):hover {
            background: $whiteNodeBg;
        }
        th,
        td {
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #dddddd;
            &:first-child {
                padding-left: 20px;
            }
        }
        th {
            background: #fafafa;
        }
        .empty-tr td {
            padding: 10px;
        }
        .project-name,
        .project-desc {
            max-width: 100%;
            text-overflow: ellipsis;
            white-space: nowrap;
            overflow: hidden;
        }
        .operate-btn {
            margin-right: 5px;
            padding: 0;
            height: auto;
            line-height: 1;
            background: transparent;
            border: none;
            font-size: 12px;
            color: #3c96ff;
        }
        .empty-data {
            padding: 120px 0;
        }
    }
    .panagation {
        padding: 10px 20px;
        text-align: right;
        border: 1px solid #dde4eb;
        border-top: none;
        background: #ffff;
        .page-info {
            float: left;
            line-height: 36px;
            font-size: 12px;
        }
        .bk-page {
            display: inline-block;
        }
    }
    .dialog-content {
        label {
            font-weight: normal;
        }
        .common-form-content {
            margin-right: 30px;
        }
        textarea {
            padding: 10px;
            width: 100%;
            border: 1px solid #dddddd;
            border-radius: 2px;
            resize: none;
            outline: none;
            &:hover {
                border-color: #c0c4cc;
            }
        }
    }
    .operation-dialog-tips {
        word-break: break-all;
    }
</style>
