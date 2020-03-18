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
    <div class="functor-container">
        <div class="list-wrapper">
            <base-title :title="i18n.functorList"></base-title>
            <div class="operation-area clearfix">
                <advance-search-form
                    :search-config="{ placeholder: i18n.placeholder }"
                    :search-form="searchForm"
                    @onSearchInput="onSearchInput"
                    @submit="onSearchFormSubmit">
                    <template v-slot:operation>
                        <bk-button
                            theme="primary"
                            class="task-create-btn"
                            @click="onCreateTask">
                            {{i18n.new}}
                        </bk-button>
                    </template>
                    <template v-slot:search-extend>
                        <span class="auto-redraw" @click.stop>
                            <bk-checkbox v-model="isAutoRedraw" @change="onAutoRedrawChange">{{ i18n.autoRedraw }}</bk-checkbox>
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
                    <bk-table-column :label="i18n.business" width="160">
                        <template slot-scope="props">
                            <span :title="props.row.task.project.name">{{ props.row.task.project.name }}</span>
                        </template>
                    </bk-table-column>
                    <bk-table-column :label="i18n.taskId" prop="task.id" width="110"></bk-table-column>
                    <bk-table-column :label="i18n.name" min-width="200">
                        <template slot-scope="props">
                            <a
                                v-if="!hasPermission(['view'], props.row.auth_actions, tplAuthOperations)"
                                v-cursor
                                class="text-permission-disable"
                                :title="props.row.task.name"
                                @click="onTaskPermissonCheck(['view'], props.row, $event)">
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
                    <bk-table-column :label="i18n.createdTime" prop="create_time" width="200"></bk-table-column>
                    <bk-table-column :label="i18n.claimedTime" width="200">
                        <template slot-scope="props">
                            {{ props.row.claim_time || '--' }}
                        </template>
                    </bk-table-column>
                    <bk-table-column :label="i18n.creator" prop="creator" width="120"></bk-table-column>
                    <bk-table-column :label="i18n.claimant" width="120">
                        <template slot-scope="props">
                            {{ props.row.claimant || '--' }}
                        </template>
                    </bk-table-column>
                    <bk-table-column :label="i18n.claimStatus" width="120">
                        <template slot-scope="props">
                            <span :class="statusClass(props.row.status)"></span>
                            {{statusMethod(props.row.status, props.row.status_name)}}
                        </template>
                    </bk-table-column>
                    <bk-table-column :label="i18n.taskStatus" width="120">
                        <template slot-scope="props">
                            <div class="task-status">
                                <span :class="executeStatus[props.$index] && executeStatus[props.$index].cls"></span>
                                <span v-if="executeStatus[props.$index]" class="task-status-text">{{executeStatus[props.$index].text}}</span>
                            </div>
                        </template>
                    </bk-table-column>
                    <bk-table-column :label="i18n.operation" width="100">
                        <template slot-scope="props">
                            <template v-if="props.row.status === 'submitted'">
                                <a
                                    v-if="!hasPermission(['claim'], props.row.auth_actions, tplAuthOperations)"
                                    v-cursor
                                    class="text-permission-disable"
                                    @click="onTaskPermissonCheck(['claim'], props.row, $event)">
                                    {{ i18n.claim }}
                                </a>
                                <router-link
                                    v-else
                                    class="functor-operation-btn"
                                    :to="{
                                        name: 'functionTaskExecute',
                                        params: { project_id: props.row.task.project.id },
                                        query: { instance_id: props.row.task.id }
                                    }">
                                    {{ i18n.claim }}
                                </router-link>
                            </template>
                            <template v-else>
                                <a
                                    v-if="!hasPermission(['view'], props.row.auth_actions, tplAuthOperations)"
                                    v-cursor
                                    class="text-permission-disable"
                                    @click="onTaskPermissonCheck(['view'], props.row, $event)">
                                    {{ i18n.view }}
                                </a>
                                <router-link
                                    v-else
                                    class="functor-operation-btn"
                                    :to="{
                                        name: 'functionTaskExecute',
                                        params: { project_id: props.row.task.project.id },
                                        query: { instance_id: props.row.task.id }
                                    }">
                                    {{ i18n.view }}
                                </router-link>
                            </template>
                        </template>
                    </bk-table-column>
                    <div class="empty-data" slot="empty"><NoData :message="i18n.empty" /></div>
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
            :title="i18n.new"
            :value="isShowNewTaskDialog"
            @confirm="onConfirmlNewTask"
            @cancel="onCancelNewTask">
            <div class="create-task-content">
                <div class="common-form-item">
                    <label>{{i18n.choiceBusiness}}</label>
                    <div class="common-form-content">
                        <bk-select
                            v-model="business.id"
                            class="bk-select-inline"
                            :popover-width="430"
                            :searchable="true"
                            :is-loading="business.loading"
                            :placeholder="i18n.statusPlaceholder"
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
                        <span v-show="business.empty" class="common-error-tip error-msg">{{i18n.choiceBusiness}}</span>
                    </div>
                </div>
                <div class="common-form-item">
                    <label>{{i18n.choiceTemplate}}</label>
                    <div class="common-form-content">
                        <bk-select
                            v-model="template.id"
                            class="bk-select-inline"
                            :popover-width="260"
                            :is-loading="business.loading"
                            :searchable="template.searchable"
                            :placeholder="i18n.statusPlaceholder"
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
                                content: i18n.tips }"></i>
                        <span v-show="template.empty" class="common-error-tip error-msg">{{i18n.choiceTemplate}}</span>
                    </div>
                </div>
            </div>
            <div slot="footer" class="dialog-footer">
                <div class="bk-button-group">
                    <bk-button
                        theme="primary"
                        :class="{
                            'btn-permission-disable': !hasConfirmPerm
                        }"
                        v-cursor="{ active: !hasConfirmPerm }"
                        @click="onConfirmlNewTask">
                        {{i18n.confirm}}
                    </bk-button>
                    <bk-button theme="default" @click="onCancelNewTask">{{i18n.cancel}}</bk-button>
                </div>
            </div>
        </bk-dialog>
    </div>
</template>
<script>
    import '@/utils/i18n.js'
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
            label: gettext('所属项目'),
            key: 'selectedProject',
            loading: false,
            placeholder: gettext('请选择项目'),
            list: []
        },
        {
            type: 'dateRange',
            key: 'executeTime',
            placeholder: gettext('选择日期时间范围'),
            label: gettext('提单时间'),
            value: []
        },
        {
            type: 'input',
            key: 'creator',
            label: gettext('提单人'),
            placeholder: gettext('请输入提单人'),
            value: ''
        },
        {
            type: 'select',
            label: gettext('状态'),
            key: 'statusSync',
            loading: false,
            placeholder: gettext('请选择状态'),
            list: [
                { 'value': 'submitted', 'name': gettext('未认领') },
                { 'value': 'claimed', 'name': gettext('已认领') },
                { 'value': 'executed', 'name': gettext('已执行') },
                { 'value': 'finished', 'name': gettext('完成') }
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
                i18n: {
                    functorList: gettext('职能化中心'),
                    placeholder: gettext('请输入ID或流程名称'),
                    business: gettext('所属项目'),
                    taskId: gettext('任务ID'),
                    createdTime: gettext('提单时间'),
                    claimedTime: gettext('认领时间'),
                    finishedTime: gettext('执行结束'),
                    name: gettext('任务名称'),
                    billTimePlaceholder: gettext('请选择时间'),
                    creator: gettext('提单人'),
                    claimant: gettext('认领人'),
                    claimStatus: gettext('认领状态'),
                    taskStatus: gettext('任务状态'),
                    operation: gettext('操作'),
                    claim: gettext('认领'),
                    view: gettext('查看'),
                    new: gettext('新建'),
                    choiceBusiness: gettext('选择项目'),
                    choiceTemplate: gettext('选择模板'),
                    tips: gettext('如果未找到模板，请联系项目运维在流程模板的使用权限中对你或所有职能化人员授予“新建任务权限”'),
                    total: gettext('共'),
                    item: gettext('条记录'),
                    comma: gettext('，'),
                    currentPageTip: gettext('当前第'),
                    page: gettext('页'),
                    functorType: gettext('任务分类'),
                    functorTypePlaceholder: gettext('请选择分类'),
                    query: gettext('搜索'),
                    reset: gettext('清空'),
                    confirm: gettext('确认'),
                    cancel: gettext('取消'),
                    autoRedraw: gettext('实时刷新')
                },
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
                            name: gettext('项目流程'),
                            children: []
                        },
                        {
                            name: gettext('公共流程'),
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
                tplAuthResource: {},
                commonTplAuthResource: {},
                tplAuthOperations: [],
                commonTplAuthOperations: [],
                tplAction: []
            }
        },
        computed: {
            ...mapState({
                categorys: state => state.categorys
            }),
            ...mapState('project', {
                'timeZone': state => state.timezone
            }),
            hasConfirmPerm () {
                const authOperations = this.isCommonTemplate ? this.commonTplAuthOperations : this.tplAuthOperations
                return this.hasPermission(['create_task'], this.tplAction, authOperations)
            },
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
        methods: {
            ...mapActions('functionTask/', [
                'loadFunctionTaskList'
            ]),
            ...mapActions('templateList/', [
                'loadTemplateList'
            ]),
            ...mapMutations('atomForm/', [
                'clearAtomForm'
            ]),
            ...mapActions('project/', [
                'loadProjectList'
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
                    this.tplAuthOperations = functorListData.meta.auth_operations
                    this.tplAuthResource = functorListData.meta.auth_resource
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
                    return gettext('完成')
                } else if (status === 'submitted') {
                    return gettext('未认领')
                } else if (status === 'rejected') {
                    return gettext('已驳回')
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
                        this.tplAuthResource = value[0].meta.auth_resource
                        this.tplAuthOperations = value[0].meta.auth_operations
                        this.commonTplAuthResource = value[1].meta.auth_resource
                        this.commonTplAuthOperations = value[1].meta.auth_operations
                        this.clearAtomForm()
                    })
                } catch (e) {
                    errorHandler(e, this)
                } finally {
                    this.template.loading = false
                }
            },
            onSelectedBusiness (id) {
                this.business.id = id
                this.getTemplateList()
                this.business.empty = false
                this.template.id = ''
                this.template.name = ''
                this.template.disabled = false
                this.template.id = ''
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
                if (!this.hasConfirmPerm) {
                    const authResource = this.isCommonTemplate ? this.commonTplAuthResource : this.tplAuthResource
                    const authOperations = this.isCommonTemplate ? this.commonTplAuthOperations : this.tplAuthOperations
                    const resourceData = {
                        name: this.template.name,
                        id: this.template.id,
                        auth_actions: this.tplAction
                    }
                    this.applyForPermission(['create_task'], resourceData, authOperations, authResource)
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
            },
            onClearTemplate () {
                this.template.id = ''
                this.template.name = ''
            },
            onClearBusiness () {
                this.business.id = ''
                this.template.id = ''
                this.template.name = ''
                this.template.disabled = true
            },
            onTaskPermissonCheck (required, template, event) {
                this.applyForPermission(required, template.task, this.tplAuthOperations, this.tplAuthResource)
                event.preventDefault()
            },
            onSearchFormSubmit (data) {
                this.requestData = data
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
