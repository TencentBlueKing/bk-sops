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
<template>
    <div class="project-container">
        <div class="list-wrapper">
            <base-title :title="$t('项目管理')"></base-title>
            <div class="list-header">
                <!-- <bk-button
                    v-cursor="{ active: !hasPermission(['create'], projectActions, authOperations) }"
                    theme="primary"
                    :class="['create-project-btn', {
                        'btn-permission-disable': !hasPermission(['create'], projectActions, authOperations)
                    }]"
                    @click="onCreateProject">
                    {{$t('新建项目')}}
                </bk-button> -->
                <div class="filter-area">
                    <bk-checkbox v-model="isClosedShow" @change="onClosedProjectToggle">{{$t('显示已停用项目')}}</bk-checkbox>
                    <div class="search-input">
                        <bk-input
                            v-model.trim="searchStr"
                            class="search-input"
                            clearable
                            :right-icon="'bk-icon icon-search'"
                            :placeholder="$t('请输入ID、名称、描述、创建人')"
                            @change="onSearchInput">
                        </bk-input>
                    </div>
                </div>
            </div>
            <div class="project-table-content">
                <bk-table
                    class="project-table"
                    :data="projectList"
                    :pagination="pagination"
                    v-bkloading="{ isLoading: loading, opacity: 1 }"
                    @page-change="onPageChange"
                    @page-limit-change="handlePageLimitChange">
                    <bk-table-column label="ID" prop="id" width="80"></bk-table-column>
                    <bk-table-column :label="$t('项目名称')" prop="name"></bk-table-column>
                    <bk-table-column :label="$t('项目描述')">
                        <template slot-scope="props">
                            {{props.row.desc || '--'}}
                        </template>
                    </bk-table-column>
                    <bk-table-column :label="$t('创建人')" prop="creator"></bk-table-column>
                    <bk-table-column :label="$t('操作')">
                        <template slot-scope="props">
                            <template
                                v-for="(item, index) in OptBtnList">
                                <a
                                    v-if="isShowOptBtn(props.row.is_disable, item.name)"
                                    v-cursor="{ active: !hasPermission([item.power], props.row.auth_actions, projectOperations) }"
                                    :key="index"
                                    :class="['operate-btn', {
                                        'text-permission-disable': !hasPermission([item.power], props.row.auth_actions, projectOperations)
                                    }]"
                                    :text="true"
                                    @click="onClickOptBtn(props.row, item.name)">
                                    {{
                                        item.name === 'view'
                                            ? (!hasPermission([item.power], props.row.auth_actions, projectOperations) ? item.text : item.enter )
                                            : item.text
                                    }}
                                </a>
                            </template>
                        </template>
                    </bk-table-column>
                    <div class="empty-data" slot="empty"><NoData /></div>
                </bk-table>
            </div>
        </div>
        <CopyrightFooter></CopyrightFooter>
        <bk-dialog
            width="600"
            padding="30px 20px"
            ext-cls="common-dialog"
            :theme="'primary'"
            :mask-close="false"
            :header-position="'left'"
            :title="projectDialogTitle"
            :value="isProjectDialogShow"
            @confirm="onProjectConfirm"
            @cancel="onEditProjectCancel">
            <div class="dialog-content">
                <div class="common-form-item">
                    <label class="required">{{ $t('名称') }}</label>
                    <div class="common-form-content">
                        <bk-input
                            name="projectName"
                            :disabled="dialogType === 'edit'"
                            v-model="projectDetail.name"
                            data-vv-validate-on=" "
                            v-validate="nameRule">
                        </bk-input>
                        <span v-show="errors.has('projectName')" class="common-error-tip error-msg">{{ errors.first('projectName') }}</span>
                    </div>
                </div>
                <div class="common-form-item">
                    <label class="required">{{ $t('时区') }}</label>
                    <div class="common-form-content">
                        <bk-select
                            v-model="projectDetail.timeZone"
                            :searchable="true"
                            :disabled="dialogType === 'edit'"
                            :placeholder="$t('请选择')"
                            @selected="onChangeTimeZone">
                            <bk-option
                                v-for="(option, index) in timeZoneList"
                                :key="index"
                                :id="option.id"
                                :name="option.name">
                            </bk-option>
                        </bk-select>
                    </div>
                </div>
                <div class="common-form-item">
                    <label>{{ $t('描述') }}</label>
                    <div class="common-form-content">
                        <textarea
                            v-model="projectDetail.desc"
                            rows="5"
                            name="projectDesc"
                            data-vv-validate-on=" "
                            v-validate="descRule">
                        </textarea>
                        <span v-show="errors.has('projectDesc')" class="common-error-tip error-msg">{{ errors.first('projectDesc') }}</span>
                    </div>
                </div>
            </div>
        </bk-dialog>
        <bk-dialog
            width="400"
            padding="30px"
            ext-cls="common-dialog"
            :theme="'primary'"
            :mask-close="false"
            :header-position="'left'"
            :title="projectStatusTitle"
            :value="isOperationDialogShow"
            @confirm="onChangeStatusConfirm"
            @cancel="isOperationDialogShow = false">
            <div class="operation-dialog-tips">
                {{$t('确认')}}{{operationType === 'start' ? $t('启用') : $t('停用')}}{{$t('项目')}}:{{projectDetail.name}}?
            </div>
        </bk-dialog>
    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import { mapState, mapActions, mapMutations } from 'vuex'
    import { errorHandler } from '@/utils/errorHandler.js'
    import toolsUtils from '@/utils/tools.js'
    import NoData from '@/components/common/base/NoData.vue'
    import CopyrightFooter from '@/components/layout/CopyrightFooter.vue'
    import BaseTitle from '@/components/common/base/BaseTitle.vue'
    import { NAME_REG, STRING_LENGTH } from '@/constants/index.js'
    import { getTimeZoneList } from '@/constants/timeZones.js'
    import permission from '@/mixins/permission.js'
    const OptBtnList = [
        {
            name: 'view',
            power: 'view',
            text: i18n.t('查看'),
            enter: i18n.t('进入')
        },
        {
            name: 'edit',
            power: 'edit',
            text: i18n.t('编辑')
        },
        {
            name: 'start',
            power: 'edit',
            text: i18n.t('启用')
        },
        {
            name: 'stop',
            power: 'edit',
            text: i18n.t('停用')
        }
    ]
    export default {
        name: 'ProjectHome',
        components: {
            NoData,
            BaseTitle,
            CopyrightFooter
        },
        mixins: [permission],
        data () {
            return {
                OptBtnList,
                searchStr: '',
                projectList: [],
                loading: true,
                totalPage: 1,
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
                descRule: {
                    max: STRING_LENGTH.PROJECT_DESC_LENGTH
                },
                projectActions: [],
                projectOperations: [],
                projectResource: {},
                pagination: {
                    current: 1,
                    count: 0,
                    limit: 15,
                    'limit-list': [15, 20, 30]
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
                return this.dialogType === 'create' ? i18n.t('新建项目') : i18n.t('编辑项目')
            },
            projectStatusTitle () {
                return this.operationType === 'stop' ? i18n.t('停用') : i18n.t('启用')
            }
        },
        created () {
            this.queryProjectCreatePerm()
            this.getProjectList()
            this.onSearchInput = toolsUtils.debounce(this.searchInputhandler, 500)
        },
        methods: {
            ...mapMutations('project', [
                'setTimeZone'
            ]),
            ...mapActions([
                'queryUserPermission'
            ]),
            ...mapActions('project', [
                'loadProjectList',
                'createProject',
                'loadProjectDetail',
                'updateProject',
                'changeDefaultProject'
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
                        limit: this.pagination.limit,
                        offset: (this.pagination.current - 1) * this.pagination.limit,
                        is_disable: this.isClosedShow
                    }
                    
                    if (this.searchStr !== '') {
                        data.q = this.searchStr
                    }
                    
                    const projectList = await this.loadProjectList(data)
                    this.projectList = projectList.objects || []
                    this.pagination.count = projectList.meta.total_count
                    this.projectOperations = projectList.meta.auth_operations
                    this.projectResource = projectList.meta.auth_resource
                    const totalPage = Math.ceil(this.pagination.count / this.pagination.limit)
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
                    this.loadProjectList({ limit: 0 })
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
                this.pagination.current = page
                this.getProjectList()
            },
            searchInputhandler () {
                this.pagination.current = 1
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
                this.pagination.current = 1
                this.getProjectList()
            },
            onCreateProject () {
                if (!this.hasPermission(['create'], this.projectActions, this.authOperations)) {
                    const resourceData = {
                        name: i18n.t('项目'),
                        auth_actions: this.projectActions
                    }
                    this.applyForPermission(['create'], resourceData, this.projectOperations, this.projectResource)
                } else {
                    this.dialogType = 'create'
                    this.isProjectDialogShow = true
                }
            },
            async onViewProject (project) {
                if (!this.hasPermission(['view'], project.auth_actions, this.projectOperations)) {
                    this.applyForPermission(['view'], project, this.projectOperations, this.projectResource)
                    return
                }
                const id = project.id
                // 切换项目上下文
                await this.changeDefaultProject(id)
                const timeZone = this.projectList.find(m => Number(m.id) === Number(id)).time_zone || 'Asia/Shanghai'
                this.setTimeZone(timeZone)
                $.atoms = {}

                this.$router.push({
                    name: 'process',
                    params: { project_id: id }
                })
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
            },
            /**
             * 是否显示操作按钮
             * @param {Boolean} isDisable
             * @param {String} name
             */
            isShowOptBtn (isDisable, name) {
                if (isDisable) {
                    return name === 'start'
                } else {
                    return ['view', 'edit', 'stop'].includes(name)
                }
            },
            /**
             * 操作按钮点击
             * @param {Object} item
             * @param {String} name
             */
            onClickOptBtn (item, name) {
                const _this = this
                switch (name) {
                    case 'view':
                        _this.onViewProject(item)
                        break
                    case 'edit':
                        _this.onEditProject(item)
                        break
                    default:
                        _this.onChangeProjectStatus(item, name)
                }
            },
            handlePageLimitChange (val) {
                this.pagination.limit = val
                this.pagination.current = 1
                this.getProjectList()
            }
        }
    }
</script>
<style lang="scss" scoped>
    .project-container {
        min-width: 1320px;
        min-height: calc(100% - 50px);
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
        overflow: hidden;
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
            .switch-status {
                display: inline-block;
            }
            .bk-form-checkbox {
                margin-right: 30px;
            }
        }
        .search-input {
            position: relative;
            width: 360px;
        }
    }
    .project-table {
        background-color: #ffffff;
    }
    .operate-btn {
        margin-right: 5px;
        padding: 5px;
        height: auto;
        line-height: 1;
        background: transparent;
        border: none;
        font-size: 12px;
        color: #3a84ff;
        cursor: pointer;
        &.bk-button {
            min-width: unset;
        }
    }
    .dialog-content {
        padding: 20px 0;
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
        padding: 20px;
    }
</style>
