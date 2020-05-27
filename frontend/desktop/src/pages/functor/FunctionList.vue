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
    <div class="functor-container">
        <div class="list-wrapper">
            <base-title :title="$t('职能化中心')"></base-title>
            <div class="operation-area clearfix">
                <advance-search-form
                    :search-config="{ placeholder: $t('请输入ID或流程名称') }"
                    :search-form="searchForm"
                    @onSearchInput="onSearchInput"
                    @submit="onSearchFormSubmit">
                    <template v-slot:operation>
                        <bk-button
                            theme="primary"
                            class="task-create-btn"
                            @click="onCreateTask">
                            {{$t('新建')}}
                        </bk-button>
                    </template>
                    <template v-slot:search-extend>
                        <span class="auto-redraw" @click.stop>
                            <bk-checkbox v-model="isAutoRedraw" @change="onAutoRedrawChange">{{ $t('实时刷新') }}</bk-checkbox>
                        </span>
                    </template>
                </advance-search-form>
            </div>
            <div class="functor-table-content">
                <bk-table
                    :data="functorList"
                    :pagination="pagination"
                    v-bkloading="{ isLoading: listLoading, opacity: 1 }"
                    @page-change="onPageChange"
                    @page-limit-change="handlePageLimitChange">
                    <bk-table-column :label="$t('所属项目')" width="160">
                        <template slot-scope="props">
                            <span :title="props.row.task.project.name">{{ props.row.task.project.name }}</span>
                        </template>
                    </bk-table-column>
                    <bk-table-column :label="$t('任务ID')" prop="task.id" width="110"></bk-table-column>
                    <bk-table-column :label="$t('任务名称')" min-width="200">
                        <template slot-scope="props">
                            <a
                                v-if="!hasPermission(['task_view'], props.row.auth_actions)"
                                v-cursor
                                class="text-permission-disable"
                                :title="props.row.task.name"
                                @click="onTaskPermissonCheck(['task_view'], props.row)">
                                {{props.row.task.name}}
                            </a>
                            <router-link
                                v-else
                                class="task-name"
                                :title="props.row.task.name"
                                :to="{
                                    name: 'functionTaskExecute',
                                    params: { project_id: props.row.task.project.id },
                                    query: { instance_id: props.row.task.id }
                                }">
                                {{props.row.task.name}}
                            </router-link>
                        </template>
                    </bk-table-column>
                    <bk-table-column :label="$t('提单时间')" prop="create_time" width="200"></bk-table-column>
                    <bk-table-column :label="$t('认领时间')" width="200">
                        <template slot-scope="props">
                            {{ props.row.claim_time || '--' }}
                        </template>
                    </bk-table-column>
                    <bk-table-column :label="$t('提单人')" prop="creator" width="120"></bk-table-column>
                    <bk-table-column :label="$t('认领人')" width="120">
                        <template slot-scope="props">
                            {{ props.row.claimant || '--' }}
                        </template>
                    </bk-table-column>
                    <bk-table-column :label="$t('认领状态')" width="120">
                        <template slot-scope="props">
                            <span :class="statusClass(props.row.status)"></span>
                            {{statusMethod(props.row.status, props.row.status_name)}}
                        </template>
                    </bk-table-column>
                    <bk-table-column :label="$t('执行状态')" width="120">
                        <template slot-scope="props">
                            <div class="task-status">
                                <span :class="executeStatus[props.$index] && executeStatus[props.$index].cls"></span>
                                <span v-if="executeStatus[props.$index]" class="task-status-text">{{executeStatus[props.$index].text}}</span>
                            </div>
                        </template>
                    </bk-table-column>
                    <bk-table-column :label="$t('操作')" width="100">
                        <template slot-scope="props">
                            <template v-if="props.row.status === 'submitted'">
                                <a
                                    v-if="!hasPermission(['task_claim'], props.row.auth_actions)"
                                    v-cursor
                                    class="text-permission-disable"
                                    @click="onTaskPermissonCheck(['task_claim'], props.row)">
                                    {{ $t('认领') }}
                                </a>
                                <router-link
                                    v-else
                                    class="functor-operation-btn"
                                    :to="{
                                        name: 'functionTaskExecute',
                                        params: { project_id: props.row.task.project.id },
                                        query: { instance_id: props.row.task.id }
                                    }">
                                    {{ $t('认领') }}
                                </router-link>
                            </template>
                            <template v-else>
                                <a
                                    v-if="!hasPermission(['task_view'], props.row.auth_actions)"
                                    v-cursor
                                    class="text-permission-disable"
                                    @click="onTaskPermissonCheck(['task_view'], props.row)">
                                    {{ $t('查看') }}
                                </a>
                                <router-link
                                    v-else
                                    class="functor-operation-btn"
                                    :to="{
                                        name: 'functionTaskExecute',
                                        params: { project_id: props.row.task.project.id },
                                        query: { instance_id: props.row.task.id }
                                    }">
                                    {{ $t('查看') }}
                                </router-link>
                            </template>
                        </template>
                    </bk-table-column>
                    <div class="empty-data" slot="empty"><NoData :message="$t('无数据')" /></div>
                </bk-table>
            </div>
        </div>
        <CopyrightFooter></CopyrightFooter>
        <bk-dialog
            width="600"
            ext-cls="common-dialog"
            :theme="'primary'"
            :mask-close="false"
            :header-position="'left'"
            :title="$t('新建')"
            :value="isShowNewTaskDialog"
            @confirm="onConfirmlNewTask"
            @cancel="onCancelNewTask">
            <div class="create-task-content">
                <div class="common-form-item">
                    <label>{{$t('选择项目')}}</label>
                    <div class="common-form-content">
                        <bk-select
                            v-model="business.id"
                            class="bk-select-inline"
                            :popover-width="430"
                            :searchable="true"
                            :is-loading="business.loading"
                            :placeholder="$t('请选择')"
                            :clearable="true"
                            @clear="onClearBusiness"
                            @selected="onSelectedBusiness">
                            <bk-option
                                v-for="(option, index) in business.list"
                                :key="index"
                                :id="option.id"
                                :name="option.name">
                            </bk-option>
                        </bk-select>
                        <span v-show="business.empty" class="common-error-tip error-msg">{{$t('选择项目')}}</span>
                    </div>
                </div>
                <div class="common-form-item">
                    <label>{{$t('选择模板')}}</label>
                    <div class="common-form-content">
                        <bk-select
                            v-model="template.id"
                            class="bk-select-inline"
                            :popover-width="260"
                            :is-loading="business.loading"
                            :searchable="template.searchable"
                            :placeholder="$t('请选择')"
                            :clearable="true"
                            :disabled="template.disabled"
                            @selected="onSelectedTemplate"
                            @clear="onClearTemplate">
                            <bk-option-group
                                v-for="(group, index) in template.list"
                                :name="group.name"
                                :key="index">
                                <bk-option v-for="(childOption, childIndex) in group.children"
                                    :key="childIndex"
                                    :id="childOption.id"
                                    :name="childOption.name">
                                </bk-option>
                            </bk-option-group>
                        </bk-select>
                        <i class="common-icon-info template-selector-tips"
                            v-bk-tooltips="{
                                width: 400,
                                placement: 'top',
                                content: $t('如果未找到模板，请联系项目运维在流程模板的使用权限中对你或所有职能化人员授予“新建任务权限”') }"></i>
                        <span v-show="template.empty" class="common-error-tip error-msg">{{$t('选择模板')}}</span>
                    </div>
                </div>
            </div>
            <div slot="footer" class="dialog-footer">
                <bk-button
                    theme="primary"
                    :loading="permissionLoading"
                    :class="{ 'btn-permission-disable': !hasCreateTaskPerm }"
                    v-cursor="{ active: !hasCreateTaskPerm }"
                    @click="onConfirmlNewTask">
                    {{$t('确认')}}
                </bk-button>
                <bk-button theme="default" @click="onCancelNewTask">{{$t('取消')}}</bk-button>
            </div>
        </bk-dialog>
    </div>
</template>
<script>
    import i18n from '@/config/i18n/index.js'
    import { mapActions, mapMutations, mapState } from 'vuex'
    import { errorHandler } from '@/utils/errorHandler.js'
    import CopyrightFooter from '@/components/layout/CopyrightFooter.vue'
    import NoData from '@/components/common/base/NoData.vue'
    import BaseTitle from '@/components/common/base/BaseTitle.vue'
    import AdvanceSearchForm from '@/components/common/advanceSearchForm/index.vue'
    import toolsUtils from '@/utils/tools.js'
    import moment from 'moment-timezone'
    import permission from '@/mixins/permission.js'
    import task from '@/mixins/task.js'
    const searchForm = [
        {
            type: 'select',
            label: i18n.t('所属项目'),
            key: 'selectedProject',
            loading: false,
            placeholder: i18n.t('请选择项目'),
            list: []
        },
        {
            type: 'dateRange',
            key: 'executeTime',
            placeholder: i18n.t('选择日期时间范围'),
            label: i18n.t('提单时间'),
            value: []
        },
        {
            type: 'input',
            key: 'creator',
            label: i18n.t('提单人'),
            placeholder: i18n.t('请输入提单人'),
            value: ''
        },
        {
            type: 'select',
            label: i18n.t('状态'),
            key: 'statusSync',
            loading: false,
            placeholder: i18n.t('请选择状态'),
            list: [
                { 'value': 'submitted', 'name': i18n.t('未认领') },
                { 'value': 'claimed', 'name': i18n.t('已认领') },
                { 'value': 'executed', 'name': i18n.t('已执行') },
                { 'value': 'finished', 'name': i18n.t('完成') }
            ]
        }
    ]
    export default {
        name: 'functionHome',
        components: {
            CopyrightFooter,
            AdvanceSearchForm,
            BaseTitle,
            NoData
        },
        mixins: [permission, task],
        props: ['project_id', 'app_id'],
        data () {
            return {
                listLoading: true,
                functorSync: 0,
                searchStr: undefined,
                isShowNewTaskDialog: false,
                functorBasicInfoLoading: true,
                functorList: [],
                executeStatus: [], // 任务执行状态
                business: {
                    list: [],
                    loading: false,
                    id: '',
                    searchable: true,
                    empty: false
                },
                template: {
                    list: [
                        {
                            name: i18n.t('项目流程'),
                            children: []
                        },
                        {
                            name: i18n.t('公共流程'),
                            children: []
                        }
                    ],
                    loading: false,
                    searchable: true,
                    id: '',
                    name: '',
                    empty: false,
                    disabled: false
                },
                isCommonTemplate: false,
                isAutoRedraw: false,
                autoRedrawTimer: null,
                status: undefined,
                functorCategory: [],
                requestData: {
                    selectedProject: '',
                    executeTime: [],
                    creator: '',
                    statusSync: '',
                    flowName: ''
                },
                pagination: {
                    current: 1,
                    count: 0,
                    limit: 15,
                    'limit-list': [15, 20, 30]
                },
                permissionLoading: false, // 查询公共流程在项目下的创建任务权限 loading
                tplAction: [],
                hasCreateTaskPerm: true
            }
        },
        computed: {
            ...mapState({
                'categorys': state => state.categorys,
                'permissionMeta': state => state.permissionMeta
            }),
            ...mapState('project', {
                'timeZone': state => state.timezone
            }),
            searchForm () {
                const value = searchForm
                value[0].list = this.business.list.map(m => ({ name: m.name, value: m.id }))
                return value
            }
        },
        created () {
            this.loadFunctionTask()
            this.onSearchInput = toolsUtils.debounce(this.searchInputhandler, 500)
            this.getProjectList()
        },
        beforeDestroy () {
            this.clearAutoRedraw()
        },
        methods: {
            ...mapActions([
                'queryUserPermission'
            ]),
            ...mapActions('functionTask/', [
                'loadFunctionTaskList'
            ]),
            ...mapActions('templateList/', [
                'loadTemplateList'
            ]),
            ...mapActions('project/', [
                'loadProjectList'
            ]),
            ...mapMutations('atomForm/', [
                'clearAtomForm'
            ]),
            async loadFunctionTask () {
                this.listLoading = true
                try {
                    const { selectedProject, executeTime, creator, statusSync, flowName } = this.requestData
                    const data = {
                        limit: this.pagination.limit,
                        offset: (this.pagination.current - 1) * this.pagination.limit,
                        task__pipeline_instance__name__contains: flowName || undefined,
                        creator: creator || undefined,
                        task__project__id: selectedProject || undefined,
                        status: statusSync || undefined
                    }
                    if (executeTime[0] && executeTime[1]) {
                        if (this.common) {
                            data['pipeline_template__start_time__gte'] = moment(executeTime[0]).format('YYYY-MM-DD')
                            data['pipeline_template__start_time__lte'] = moment(executeTime[1]).add('1', 'd').format('YYYY-MM-DD')
                        } else {
                            data['create_time__gte'] = moment.tz(executeTime[0], this.timeZone).format('YYYY-MM-DD')
                            data['create_time__lte'] = moment.tz(executeTime[1], this.timeZone).add('1', 'd').format('YYYY-MM-DD')
                        }
                    }
                    const functorListData = await this.loadFunctionTaskList(data)
                    const list = functorListData.objects
                    const taskList = functorListData.objects.map(m => m.task)
                    this.functorList = list
                    this.pagination.count = functorListData.meta.total_count
                    // mixins getExecuteStatus
                    this.getExecuteStatus('executeStatus', taskList)
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.listLoading = false
                }
            },
            onPageChange (page) {
                this.pagination.current = page
                this.loadFunctionTask()
                // 重置自动刷新时间
                this.onOpenAutoRedraw()
            },
            searchInputhandler (data) {
                this.requestData.flowName = data
                this.pagination.current = 1
                this.loadFunctionTask()
            },
            statusMethod (status, status_name) {
                if (status === 'finished') {
                    return i18n.t('完成')
                } else if (status === 'submitted') {
                    return i18n.t('未认领')
                } else if (status === 'rejected') {
                    return i18n.t('已驳回')
                }
                return status_name
            },
            statusClass (status) {
                let cls
                switch (status) {
                    case 'submitted': // 未认领
                        cls = 'common-icon-flag-circle default'
                        break
                    case 'claimed': // 已认领
                        cls = 'common-icon-flag-circle success'
                        break
                    case 'executed': // 已执行
                        cls = 'common-icon-dark-circle-ellipsis primary'
                        break
                    case 'rejected': // 已驳回
                        cls = 'common-icon-dark-circle-close'
                        break
                    case 'finished': // 完成
                        cls = 'bk-icon icon-check-circle-shape'
                        break
                    default:
                        cls = ''
                }

                return cls
            },
            onCreateTask () {
                this.isShowNewTaskDialog = true
            },
            async getProjectList () {
                this.business.loading = true
                try {
                    const businessData = await this.loadProjectList({ limit: 0 })
                    this.business.list = businessData.objects
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.business.loading = false
                }
            },
            async getTemplateList () {
                this.template.loading = true
                try {
                    // 查询职能化数据及公共流程数据
                    await Promise.all([
                        this.loadTemplateList({ project__id: this.business.id }),
                        this.loadTemplateList({ common: 1 })
                    ]).then(value => {
                        this.template.list[0].children = value[0].objects
                        this.template.list[1].children = value[1].objects
                        this.clearAtomForm()
                    })
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.template.loading = false
                }
            },
            onSelectedBusiness (id) {
                const business = this.business.list.find(item => item.id === id)
                this.business.id = id
                this.business.name = business.name
                this.business.auth_actions = business.auth_actions
                this.getTemplateList()
                this.business.empty = false
                this.template.id = ''
                this.template.name = ''
                this.template.disabled = false
                this.hasCreateTaskPerm = true
            },
            onSelectedTemplate (id) {
                const templateList = this.template.list
                let resource_uri = ''
                let name, tplAction

                if (id === undefined) {
                    return
                }

                templateList.some(group => {
                    return group.children.some(item => {
                        if (item.id === id) {
                            resource_uri = item.resource_uri
                            name = item.name
                            tplAction = item.auth_actions
                            return true
                        }
                    })
                })

                this.isCommonTemplate = false
                // 通过resource_uri查找是否是公共流程
                if (resource_uri.search('common_template') !== -1) {
                    this.isCommonTemplate = true
                }
                this.template.id = id
                this.template.name = name
                this.template.empty = false
                this.tplAction = tplAction
                this.checkCreateTaskPerm()
            },
            async checkCreateTaskPerm () {
                if (this.isCommonTemplate) {
                    try {
                        this.permissionLoading = true
                        const bkSops = this.permissionMeta.system.find(item => item.id === 'bk_sops')
                        const data = {
                            action: ['common_flow_create_task'],
                            resources: [
                                {
                                    system: bkSops.id,
                                    type: 'project',
                                    id: this.business.id,
                                    attributes: {}
                                },
                                {
                                    system: bkSops.id,
                                    type: 'common_flow',
                                    id: this.template.id,
                                    attributes: {}
                                }
                            ]
                        }
                        const resp = this.queryUserPermission(data)
                        this.hasCreateTaskPerm = resp.is_allow
                    } catch (error) {
                        errorHandler(error, this)
                    } finally {
                        this.permissionLoading = false
                    }
                } else {
                    this.hasCreateTaskPerm = this.hasPermission(['flow_create_task'], this.tplAction)
                }
            },
            applyCreateTaskPerm () {
                let reqPermission = []
                let curPermission = []
                let resourceData = {}
                if (this.isCommonTemplate) {
                    reqPermission = ['common_flow_create_task']
                    curPermission = [...this.tplAction, ...this.business.auth_actions]
                    resourceData = {
                        common_flow: [{
                            id: this.template.id,
                            name: this.template.name
                        }],
                        project: [{
                            id: this.business.id,
                            name: this.business.name
                        }]
                    }
                } else {
                    reqPermission = ['flow_create_task']
                    curPermission = [...this.tplAction]
                    resourceData = {
                        flow: [{
                            id: this.template.id,
                            name: this.template.name
                        }]
                    }
                }
                this.applyForPermission(reqPermission, curPermission, resourceData)
            },
            onConfirmlNewTask () {
                if (this.business.id === '') {
                    this.business.empty = true
                    return
                }
                if (this.template.id === '') {
                    this.template.empty = true
                    return
                }
                if (this.permissionLoading) {
                    return
                }

                if (!this.hasCreateTaskPerm) {
                    this.applyCreateTaskPerm()
                    return
                }

                if (this.isCommonTemplate) {
                    this.$router.push({
                        name: 'functionTemplateStep',
                        params: { project_id: this.business.id, step: 'selectnode' },
                        query: { template_id: this.template.id, common: 1, entrance: 'function' }
                    })
                } else {
                    this.$router.push({
                        name: 'functionTemplateStep',
                        params: { project_id: this.business.id, step: 'selectnode' },
                        query: { template_id: this.template.id, entrance: 'function' }
                    })
                }
            },
            onCancelNewTask () {
                this.onClearTemplate()
                this.onClearBusiness()
                this.isShowNewTaskDialog = false
                this.business.empty = false
                this.template.empty = false
                this.hasCreateTaskPerm = true
            },
            onClearTemplate () {
                this.template.id = ''
                this.template.name = ''
            },
            onClearBusiness () {
                this.business.id = ''
                this.business.auth_actions = []
                this.template.id = ''
                this.template.name = ''
                this.template.disabled = true
            },
            onTaskPermissonCheck (required, data) {
                const permissionData = {
                    task: [{
                        id: data.task.id,
                        name: data.task.name
                    }]
                }
                this.applyForPermission(required, data.auth_actions, permissionData)
            },
            onSearchFormSubmit (data) {
                this.requestData = data
                this.pagination.current = 1
                this.loadFunctionTask()
            },
            onAutoRedrawChange (val) {
                if (val) {
                    return this.onOpenAutoRedraw()
                }
                this.clearAutoRedraw()
            },
            // 开启自动刷新
            onOpenAutoRedraw () {
                if (!this.isAutoRedraw) {
                    return this.clearAutoRedraw()
                }
                clearTimeout(this.autoRedrawTimer)
                this.autoRedrawTimer = setTimeout(() => {
                    this.loadFunctionTask()
                    this.onOpenAutoRedraw()
                }, 15000)
            },
            // 关闭自动刷新
            clearAutoRedraw () {
                clearTimeout(this.autoRedrawTimer)
                this.autoRedrawTimer = null
                this.isAutoRedraw = false
            },
            handlePageLimitChange (val) {
                this.pagination.limit = val
                this.pagination.current = 1
                this.onOpenAutoRedraw() // 重置自动刷新时间
                this.loadFunctionTask()
            }
        }
    }
</script>
<style lang='scss' scoped>
@import '@/scss/config.scss';
@import '@/scss/task.scss';
.bk-select-inline,.bk-input-inline {
    display: inline-block;
    width: 260px;
}
.functor-container {
    min-width: 1320px;
    min-height: calc(100% - 50px);
    background: #f4f7fa;
}
.list-wrapper {
    padding: 0 60px;
    min-height: calc(100vh - 240px);
}
.operation-area {
    margin: 20px 0;
    .task-create-btn {
        min-width: 120px;
    }
    .auto-redraw {
        margin-left: 30px;
        display: inline-block;
    }
}
.advanced-search {
    margin: 0;
}

.functor-table-content {
    background: #ffffff;
    a.task-name {
        color: $blueDefault;
    }
    .functor-operation-btn {
        color: #3a84ff;
    }
    .empty-data {
        padding: 120px 0;
    }
    .task-status {
       @include ui-task-status;
    }
}
.panagation {
    padding: 10px 20px;
    text-align: right;
    border: 1px solid #dde4eb;
    border-top: none;
    background: #fafbfd;
    .page-info {
        float: left;
        line-height: 36px;
        font-size: 14px;
    }
    .bk-page {
        display: inline-block;
    }
}
.icon-check-circle-shape {
    color: $greenDefault;
}
.common-icon-dark-circle-close {
    color: $redDefault;
}
.default {
    color: #979ba5;
}
.primary {
    color: #3a84ff;
}
.success {
    color: #2dcb56;
}
.create-task-content {
    padding: 30px;
    .common-form-item {
        label {
            width: 70px;
            font-weight: normal;
        }
        .common-form-content {
            position: relative;
            margin-left: 80px;
            margin-right: 30px;
            .template-selector-tips {
                position: absolute;
                right: -20px;
                top: 9px;
            }
        }
    }
    .bk-select-inline {
        width: 430px;
    }
}
.dialog-footer {
    .bk-button {
        margin-left: 10px;
        width: 90px;
    }
}
</style>
